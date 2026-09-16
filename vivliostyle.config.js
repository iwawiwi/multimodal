// vivliostyle.config.js — build PDF formal (A4) untuk dokumen hands-on.
//
// Prinsip: sumber tunggal. File layar hands-on/mggNN-hands-on.html tetap utuh
// (interaktif, scroll, salin kode). Build Vivliostyle menyuntikkan CSS cetak
// formal (TOC otomatis + running header + nomor halaman) via flag --style
// (TANPA mengubah file layar). Lihat D-011b di references/design-decisions.md.
//
// Catatan: `style`/`css` adalah INLINE config (CLI flag), bukan di sini.
// File ini hanya memuat BuildTask: entry, size, static, output, dll.
const week = process.env.HANDSON_WEEK || '03';
const titles = {
  '02': 'Hands-on 02: Eksplorasi Word Embeddings',
  '03': 'Hands-on 03: Feature Extraction Gambar',
  '04': 'Hands-on 04: Representasi Audio & Video',
};

module.exports = {
  title: titles[week] || `Hands-on ${week}`,
  author: 'Pembelajaran Mesin Multimodal (IF25-40304)',
  language: 'id',
  size: 'A4',
  entry: [`hands-on/mgg${week}-hands-on.html`],
  // Server Vivliostyle menjadikan folder `hands-on/` sebagai root, sehingga
  // referensi `../assets/...` pada HTML perlu dipetakan ke folder assets asli
  // (resolve `../assets` dari root server `hands-on/` → `assets/` project).
  static: {
    '/assets': '../assets',
  },
  workspaceDir: '.vivliostyle',
  output: `pdf/mgg${week}-hands-on.pdf`,
};
