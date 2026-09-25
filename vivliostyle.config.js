// vivliostyle.config.js — build PDF formal (A4) untuk dokumen hands-on.
//
// Prinsip: sumber tunggal. File layar hands-on/mggNN-hands-on.html tetap utuh
// (interaktif, scroll, salin kode). Build Vivliostyle menyuntikkan CSS cetak
// formal (TOC otomatis + running header + nomor halaman) via flag --style
// (TANPA mengubah file layar). Lihat D-011b di references/design-decisions.md.
//
// Catatan: `style`/`css` adalah INLINE config (CLI flag), bukan di sini.
// File ini hanya memuat BuildTask: entry, size, static, output, dll.
const path = require('path');

const week = process.env.HANDSON_WEEK || '03';
const titles = {
  '02': 'Hands-on 02: Eksplorasi Word Embeddings',
  '03': 'Hands-on 03: Feature Extraction Gambar',
  '04': 'Hands-on 04: Representasi Audio & Video',
  '06': 'Hands-on 06: Early, Late & Intermediate Fusion',
  '09': 'Hands-on 09: Menyejajarkan Dua Ruang — dari Kontrastif ke CLIP',
  '13': 'Hands-on 13: Protokol Evaluasi & Uji Signifikansi',
};

// Dokumen non-mingguan (mis. kisi-kisi ujian) dipilih lewat `DOC=<kunci>`.
// Sumbernya tetap HTML supaya memakai jalur cetak yang sama dengan hands-on
// (Vivliostyle + print-formal.css) — tanpa perlu TeX Live sama sekali di CI.
const documents = {
  'uts-kisi-kisi': {
    entry: 'dokumen/uts-kisi-kisi.html',
    title: 'Kisi-Kisi Ujian Tengah Semester',
  },
};

const docKey = process.env.DOC;
const doc = docKey ? documents[docKey] : null;
if (docKey && !doc) {
  throw new Error(
    `DOC tidak dikenal: "${docKey}". Pilihan: ${Object.keys(documents).join(', ')}`
  );
}

const entry = doc ? doc.entry : `hands-on/mgg${week}-hands-on.html`;
const title = doc ? doc.title : titles[week] || `Hands-on ${week}`;
// Nama berkas keluaran mengikuti nama berkas sumber (satu aturan untuk semua).
const base = path.basename(entry, '.html');

module.exports = {
  title,
  author: 'Pembelajaran Mesin Multimodal (IF25-40304)',
  language: 'id',
  size: 'A4',
  entry: [entry],
  // Server Vivliostyle menjadikan folder berkas entri sebagai root, sehingga
  // referensi `../assets/...` pada HTML perlu dipetakan ke folder assets asli
  // (resolve `../assets` dari root server → `assets/` project).
  // Berlaku untuk entri di kedalaman satu: `hands-on/` maupun `dokumen/`.
  static: {
    '/assets': '../assets',
  },
  workspaceDir: '.vivliostyle',
  output: `pdf/${base}.pdf`,
};
