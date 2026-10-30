#!/usr/bin/env node
/**
 * measure_overflow.js — audit slide overflow at "Teks Besar" (960×540).
 *
 * Measures each top-level section's scrollHeight vs clientHeight AFTER forcing
 * the deck into text-large mode (base resolution 960×540). Reveal lays out
 * sections at the base resolution regardless of the window's transform scale,
 * so scrollHeight reflects the TRUE virtual content height.
 *
 * Usage:
 *   node scripts/measure_overflow.js mgg01.html
 *   node scripts/measure_overflow.js mgg02.html --limit 5   # show only top-5 offenders
 */

const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const args = process.argv.slice(2);
const TARGET = args[0];
const LIMIT = (() => {
  const i = args.indexOf('--limit');
  return i >= 0 ? parseInt(args[i + 1], 10) : Infinity;
})();

const CHROME =
  process.env.CHROME_PATH ||
  process.env.CHROME_BIN ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;

if (!TARGET) {
  console.error('Usage: node scripts/measure_overflow.js <file.html> [--limit N]');
  process.exit(2);
}
if (!fs.existsSync(TARGET)) {
  console.error('File not found: ' + TARGET);
  process.exit(2);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function getJson(url) {
  return new Promise((resolve, reject) => {
    http
      .get(url, (r) => {
        let d = '';
        r.on('data', (c) => (d += c));
        r.on('end', () => {
          try { resolve(JSON.parse(d)); } catch (e) { reject(e); }
        });
      })
      .on('error', reject);
  });
}

async function waitForDebugger() {
  for (let i = 0; i < 60; i++) {
    try {
      const list = await getJson(`http://127.0.0.1:${PORT}/json/list`);
      const page = list.find((t) => t.type === 'page');
      if (page && page.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch (e) { /* not up yet */ }
    await sleep(200);
  }
  throw new Error('Chrome DevTools did not become available');
}

class CDP {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.id = 0;
    this.pending = new Map();
    this.listeners = [];
  }
  async connect() {
    await new Promise((res, rej) => {
      this.ws.onopen = res;
      this.ws.onerror = rej;
    });
    this.ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.id && this.pending.has(m.id)) {
        const { resolve, reject } = this.pending.get(m.id);
        this.pending.delete(m.id);
        m.error ? reject(new Error(m.error.message)) : resolve(m.result);
      } else {
        this.listeners.forEach((fn) => fn(m));
      }
    };
  }
  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
}

const MEASURE_JS = `(function () {
  // Two problems to defeat:
  // 1) section has overflow:hidden, so scrollHeight stays == clientHeight and
  //    never reports the clipped content.
  // 2) Reveal scales sections with transform, and getBoundingClientRect
  //    returns post-transform geometry.
  // Fix: strip overflow:hidden AND transform, so every element reports its
  //    natural UNTRANSFORMED layout box in the 960×540 coordinate space.
  var style = document.createElement('style');
  style.textContent =
    '.reveal .slides, .reveal .slides > section, ' +
    '.reveal .slides > section > section { ' +
    'transform: none !important; overflow: visible !important; ' +
    'position: static !important; } ' +
    '.reveal .slides > section { display: block !important; ' +
    'height: auto !important; min-height: 540px; }';
  document.head.appendChild(style);

  var slides = Array.prototype.slice.call(
    document.querySelectorAll('.reveal .slides > section')
  );
  var result = slides.map(function (s, i) {
    // content natural height = max bottom of any descendant, minus top
    var top = Infinity, bottom = -Infinity;
    var walker = document.createTreeWalker(s, NodeFilter.SHOW_ELEMENT, null);
    var node;
    while ((node = walker.nextNode())) {
      var r = node.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) {
        if (r.top < top) top = r.top;
        if (r.bottom > bottom) bottom = r.bottom;
      }
    }
    var contentH = Math.round(bottom - top);
    var overflow = Math.max(0, contentH - 540);
    var h = s.querySelector('h1,h2,h3,h4');
    var t = h ? h.textContent.trim().replace(/\\s+/g, ' ').slice(0, 70)
              : '(slide ' + (i + 1) + ')';
    return { n: i + 1, title: t, scroll: contentH, client: 540, overflow: overflow };
  });
  return result;
})()`;

async function main() {
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-overflow-'));
  const fileUrl = 'file://' + path.resolve(TARGET);

  const chrome = spawn(CHROME, [
    '--headless=new',
    '--disable-gpu',
    '--no-sandbox',
    '--no-first-run',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${userDataDir}`,
    '--window-size=1920,1080',
    'about:blank',
  ], { stdio: 'ignore' });

  try {
    const wsUrl = await waitForDebugger();
    const cdp = new CDP(wsUrl);
    await cdp.connect();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');

    await cdp.send('Page.navigate', { url: fileUrl });
    await sleep(1500);

    // Wait until Reveal is initialized and the aspect switcher exists.
    for (let i = 0; i < 40; i++) {
      const r = await cdp.send('Runtime.evaluate', {
        expression: 'typeof Reveal !== "undefined" && typeof setAspectMode === "function"',
        returnByValue: true,
      });
      if (r.result && r.result.value === true) break;
      await sleep(250);
    }

    // Force text-large (960×540) and let Reveal relayout.
    await cdp.send('Runtime.evaluate', {
      expression: 'setAspectMode("text-large")',
    });
    await sleep(1200);

    const res = await cdp.send('Runtime.evaluate', {
      expression: MEASURE_JS,
      returnByValue: true,
    });

    const slides = res.result && res.result.value ? res.result.value : [];
    const overflow = slides.filter((s) => s.overflow > 2);
    const safe = slides.length - overflow.length;

    console.log(`\n=== ${path.basename(TARGET)} @ Teks Besar (960×540) ===`);
    console.log(`Total slides: ${slides.length} | Safe: ${safe} | Overflow: ${overflow.length}\n`);

    if (overflow.length === 0) {
      console.log('✅ All slides fit within 960×540.');
    } else {
      overflow.sort((a, b) => b.overflow - a.overflow);
      for (const s of overflow.slice(0, LIMIT)) {
        const pct = ((s.overflow / s.client) * 100).toFixed(0);
        console.log(
          `  slide ${String(s.n).padStart(2, '0')}  +${s.overflow}px (${pct}%)  ${s.title}`
        );
      }
      if (overflow.length > LIMIT) {
        console.log(`  … and ${overflow.length - LIMIT} more (use --limit to see).`);
      }
    }
  } finally {
    try { chrome.kill('SIGKILL'); } catch (e) {}
    try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch (e) {}
  }
}

main().catch((e) => {
  console.error('❌ ' + e.message);
  process.exit(1);
});
