#!/usr/bin/env node
/**
 * bake.js — bake syntax highlighting + line numbers menjadi HTML statis.
 *
 * Mengapa: PDF dibangun oleh Vivliostyle dari HTML yang sama, tetapi
 * Prism.js (sorotan sintaks) dan line-numbers plugin berjalan lewat
 * JavaScript pada runtime browser. Vivliostyle tidak menjamin timing JS
 * selesai sebelum paginasi, dan nomor baris Prism memakai CSS counter
 * (`::before { content: counter(...) }`) yang tidak didukung mesin cetak.
 *
 * Solusi: script ini mengubah setiap blok kode menjadi markup statis —
 * token highlight Prism + nomor baris sebagai elemen <span> nyata — sehingga
 * HTML layar dan PDF mereproduksi tampilan yang sama persis, tanpa bergantung
 * pada JavaScript sama sekali.
 *
 * Pemakaian:
 *   node vivliostyle/bake.js <input.html> [output.html]
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const Prism = require(path.join(ROOT, 'node_modules', 'prismjs'));
require(path.join(ROOT, 'node_modules', 'prismjs', 'components', 'prism-python'));
require(path.join(ROOT, 'node_modules', 'prismjs', 'components', 'prism-bash'));

function decodeEntities(s) {
  return s
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function bakeCodeBlock(rawCode, lang) {
  const plain = decodeEntities(rawCode);
  const grammar = lang === 'python' ? Prism.languages.python : Prism.languages.bash;
  const highlighted = Prism.highlight(plain, grammar, lang);
  return highlighted
    .split('\n')
    .map((line, i) => {
      const content = line.length > 0 ? line : '&nbsp;';
      return (
        '<span class="code-line">' +
        `<span class="ln" aria-hidden="true">${i + 1}</span>` +
        `<span class="lc">${content}</span>` +
        '</span>'
      );
    })
    .join('\n');
}

function bake(input, output) {
  let html = fs.readFileSync(input, 'utf8');
  const re = /<pre[^>]*>\s*<code class="language-([a-z]+)">([\s\S]*?)<\/code>\s*<\/pre>/g;
  let count = 0;
  html = html.replace(re, (match, lang, codeInner) => {
    count++;
    const baked = bakeCodeBlock(codeInner, lang);
    return `<pre class="code-baked language-${lang}"><code>${baked}</code></pre>`;
  });
  fs.writeFileSync(output, html);
  return count;
}

const input = process.argv[2];
const output = process.argv[3] || input;
const n = bake(input, output);
console.log(`Baked ${n} code blocks -> ${output}`);
