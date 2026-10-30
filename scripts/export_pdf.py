#!/usr/bin/env python3
"""
Compiles Reveal.js slides to standalone PDF (16:9, 1920×1080) using headless Chrome.
Injects @page CSS for correct page dimensions in print mode.

Usage:
    python3 export_pdf.py mgg01.html
    python3 export_pdf.py mgg01.html --out custom.pdf
"""

import sys
import os
import time
import argparse
import subprocess
import threading
import tempfile
import http.server
import socketserver
import shutil
import re


def get_chrome_path():
    # CI environments often expose the browser via these env vars.
    for env in ("CHROME_PATH", "CHROME_BIN", "GOOGLE_CHROME_BIN"):
        val = os.environ.get(env)
        if val and os.path.exists(val):
            return val
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "google-chrome",
        "google-chrome-stable",
        "chromium-browser",
        "chromium",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
        try:
            out = subprocess.run(["which", c], capture_output=True, text=True)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except Exception:
            pass
    return None


def resolve_site_base_url():
    """Base URL absolut untuk anotasi tautan di PDF.

    Chrome membekukan URL server sementara (http://127.0.0.1:8765/...) ke dalam
    anotasi PDF, sehingga tautan hands-on mati bagi mahasiswa. Tulis ulang target
    tautan menjadi URL produksi.

    Urutan sumber (tidak ada yang di-hardcode ke repo tertentu, agar repo ini
    tetap benar setelah ditransfer ke organisasi lain):
      1. SITE_BASE_URL           — override eksplisit
      2. PAGES_BASE_URL          — output `actions/configure-pages` (base_url)
      3. https://<owner>.github.io/<repo>  — dari GITHUB_REPOSITORY
      4. kosong                  — render lokal tetap memakai path relatif
    """
    explicit = os.environ.get("SITE_BASE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")

    pages_base = os.environ.get("PAGES_BASE_URL", "").strip()
    if pages_base:
        return pages_base.rstrip("/")

    slug = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if slug and "/" in slug:
        owner, repo = slug.split("/", 1)
        return f"https://{owner}.github.io/{repo}"

    return ""


def inject_print_css(html_path):
    """Inject @page CSS for 16:9 landscape into HTML <head>. Returns temp file path."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    page_css = "@page { size: 1920px 1080px; margin: 0; }"
    style_tag = f"<style>\n{page_css}\n</style>\n</head>"
    html_modified = html.replace("</head>", style_tag, 1)

    # Hanya target tautan yang diabsolutkan; path aset (CSS, gambar) tetap
    # relatif supaya render lokal di server sementara tetap berfungsi.
    base = resolve_site_base_url()
    if base:
        html_modified = re.sub(
            r'href="((?:hands-on|pdf)/[^"]+)"',
            lambda m: f'href="{base}/{m.group(1)}"',
            html_modified,
        )
    else:
        # Di lokal, tautan ke server sementara itu wajar (PDF tidak dipublikasikan).
        # Di CI, base URL yang hilang berarti PDF terbit dengan tautan mati.
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            print(
                '  ⚠️  Base URL tidak diketahui (SITE_BASE_URL / PAGES_BASE_URL / '
                'GITHUB_REPOSITORY kosong). Tautan hands-on di PDF akan menunjuk '
                'server lokal dan mati setelah dipublikasikan.',
                file=sys.stderr,
            )

    tmp_dir = os.path.dirname(os.path.abspath(html_path))
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".html", dir=tmp_dir)
    with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
        f.write(html_modified)

    return tmp_path


def export_slide_to_pdf(slide_filename, output_pdf=None):
    if not os.path.exists(slide_filename):
        print(f"Error: Slide file not found: {slide_filename}", file=sys.stderr)
        return False

    chrome = get_chrome_path()
    if not chrome:
        print("Error: Google Chrome or Chromium not found on system.", file=sys.stderr)
        return False

    base_name = os.path.splitext(os.path.basename(slide_filename))[0]
    os.makedirs("pdf", exist_ok=True)
    if not output_pdf:
        output_pdf = os.path.join("pdf", f"{base_name}.pdf")

    # Inject @page CSS into a temp copy
    with open(slide_filename, "r", encoding="utf-8") as f:
        expected_slides = len(re.findall(r"<section(?:\s|>)", f.read()))
    tmp_html = inject_print_css(slide_filename)
    tmp_basename = os.path.basename(tmp_html)

    # Start local temporary HTTP server
    port = 8765
    handler = http.server.SimpleHTTPRequestHandler

    class QuietServer(socketserver.TCPServer):
        allow_reuse_address = True

    try:
        httpd = QuietServer(("127.0.0.1", port), handler)
    except Exception:
        port = 8766
        httpd = QuietServer(("127.0.0.1", port), handler)

    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.4)

    target_url = (
        f"http://127.0.0.1:{port}/{tmp_basename}"
        f"?print-pdf&pdfSeparateFragments=false"
    )
    print(f"Rendering [16:9] 1920×1080 -> {output_pdf} ...")

    # Direct --print-to-pdf can print before Reveal.js initializes, producing
    # a valid-looking 1 KB blank PDF. Use CDP and wait for Reveal readiness.
    cdp_port = 9300 + (os.getpid() % 500)
    user_dir = tempfile.mkdtemp(prefix="multimodal-chrome-")
    chrome_cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--no-first-run", "--no-default-browser-check",
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir={user_dir}", "--window-size=1920,1080",
        "about:blank",
    ]
    cdp_script = os.path.join(os.path.dirname(__file__), "chrome_print_pdf.js")

    try:
        browser = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE, text=True)
        env = os.environ.copy()
        env["CDP_PORT"] = str(cdp_port)
        res = subprocess.run(
            ["node", cdp_script, target_url, output_pdf, str(expected_slides)],
            capture_output=True, text=True, timeout=90, env=env,
        )
        if res.returncode == 0 and os.path.exists(output_pdf):
            size_kb = os.path.getsize(output_pdf) / 1024
            print(f"✅ Successfully generated PDF: {output_pdf} ({size_kb:.1f} KB)")
            return True
        print(f"❌ Failed to generate PDF. Exit code: {res.returncode}")
        if res.stderr:
            print(f"   Stderr: {res.stderr[:1000]}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout: Chrome did not finish within 90 seconds.")
        return False
    except Exception as e:
        print(f"❌ Exception during PDF generation: {e}")
        return False
    finally:
        try:
            browser.terminate()
            browser.wait(timeout=5)
        except Exception:
            try:
                browser.kill()
            except Exception:
                pass
        httpd.shutdown()
        shutil.rmtree(user_dir, ignore_errors=True)
        try:
            os.unlink(tmp_html)
        except OSError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Reveal.js slides to PDF (16:9)")
    parser.add_argument("slide", nargs="?", default="mgg01.html", help="Slide HTML file")
    parser.add_argument("--out", default=None, help="Custom output PDF path")
    args = parser.parse_args()

    success = export_slide_to_pdf(args.slide, output_pdf=args.out)
    sys.exit(0 if success else 1)
