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


def inject_print_css(html_path):
    """Inject @page CSS for 16:9 landscape into HTML <head>. Returns temp file path."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    page_css = "@page { size: 1920px 1080px; margin: 0; }"
    style_tag = f"<style>\n{page_css}\n</style>\n</head>"
    html_modified = html.replace("</head>", style_tag, 1)

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

    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--virtual-time-budget=15000",
        "--window-size=1920,1080",
        f"--print-to-pdf={output_pdf}",
        target_url,
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        httpd.shutdown()

        try:
            os.unlink(tmp_html)
        except OSError:
            pass

        if res.returncode == 0 and os.path.exists(output_pdf):
            size_kb = os.path.getsize(output_pdf) / 1024
            print(f"✅ Successfully generated PDF: {output_pdf} ({size_kb:.1f} KB)")
            return True
        else:
            print(f"❌ Failed to generate PDF. Exit code: {res.returncode}")
            if res.stderr:
                print(f"   Stderr: {res.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        httpd.shutdown()
        try:
            os.unlink(tmp_html)
        except OSError:
            pass
        print(f"❌ Timeout: Chrome did not finish within 60 seconds.")
        return False
    except Exception as e:
        httpd.shutdown()
        try:
            os.unlink(tmp_html)
        except OSError:
            pass
        print(f"❌ Exception during PDF generation: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Reveal.js slides to PDF (16:9)")
    parser.add_argument("slide", nargs="?", default="mgg01.html", help="Slide HTML file")
    parser.add_argument("--out", default=None, help="Custom output PDF path")
    args = parser.parse_args()

    success = export_slide_to_pdf(args.slide, output_pdf=args.out)
    sys.exit(0 if success else 1)
