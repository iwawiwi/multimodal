#!/usr/bin/env node
/* Print Reveal.js deck after browser-side rendering completes. */
const fs = require('fs');
const http = require('http');
const { WebSocket } = require('ws');

const [url, output, expectedSlides] = process.argv.slice(2);
const port = Number(process.env.CDP_PORT || 9222);
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

function getJson(path) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}${path}`, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
}

async function main() {
  let target;
  for (let i = 0; i < 100; i++) {
    try {
      const pages = await getJson('/json/list');
      target = pages.find(page => page.webSocketDebuggerUrl && (page.type === 'page' || page.url === 'about:blank'));
      if (target?.webSocketDebuggerUrl) break;
    } catch (_) {}
    await sleep(100);
  }
  if (!target?.webSocketDebuggerUrl) throw new Error('Chrome CDP page unavailable');

  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });

  let nextId = 0;
  const pending = new Map();
  ws.onmessage = event => {
    const message = JSON.parse(event.data);
    if (pending.has(message.id)) {
      pending.get(message.id)(message);
      pending.delete(message.id);
    }
  };
  const command = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, message => message.error ? reject(new Error(JSON.stringify(message.error))) : resolve(message.result));
    ws.send(JSON.stringify({ id, method, params }));
  });

  await command('Page.enable');
  await command('Runtime.enable');
  await command('Page.navigate', { url });
  await sleep(1000);

  const readyExpression = `(() => {
    const imagesReady = [...document.images].every(image => image.complete);
    const fontsReady = !document.fonts || document.fonts.status === 'loaded';
    return Boolean(window.Reveal && Reveal.isReady && Reveal.isReady() && ${Number(expectedSlides)} <= Reveal.getTotalSlides() && imagesReady && fontsReady);
  })()`;
  let ready = false;
  for (let i = 0; i < 120; i++) {
    const result = await command('Runtime.evaluate', { expression: readyExpression, returnByValue: true });
    ready = result.result?.value === true;
    if (ready) break;
    await sleep(250);
  }
  if (!ready) throw new Error('Reveal.js did not become ready before PDF export');

  await command('Runtime.evaluate', {
    expression: `Reveal.configure({ embedded: false }); Reveal.slide(0); window.scrollTo(0, 0);`
  });
  await sleep(500);
  const pdf = await command('Page.printToPDF', {
    landscape: true,
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: false,
    pageRanges: ''
  });
  const data = Buffer.from(pdf.data, 'base64');
  const pageCount = (data.toString('latin1').match(/\/Type\s*\/Page(?!s)/g) || []).length;
  if (data.length < 10000 || pageCount < Number(expectedSlides)) {
    throw new Error(`Generated PDF invalid: ${data.length} bytes, ${pageCount} pages; expected ${expectedSlides}`);
  }
  fs.writeFileSync(output, data);
  ws.close();
  console.log(`Rendered ${pageCount} pages (${Math.round(data.length / 1024)} KB)`);
  process.exit(0);
}

main().catch(error => {
  console.error(`PDF export failed: ${error.message}`);
  process.exit(1);
});
