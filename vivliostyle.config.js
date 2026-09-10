// vivliostyle.config.js — build PDF formal (A4) untuk dokumen hands-on.
//
// Prinsip: sumber tunggal. File layar hands-on/mggNN-hands-on.html tetap utuh
// (interaktif, scroll, salin kode). Build Vivliostyle menyuntikkan CSS cetak
// formal (TOC otomatis + running header + nomor halaman) via flag --style
// (TANPA mengubah file layar). Lihat D-011b di references/design-decisions.md.
//
// Catatan: `style`/`css` adalah INLINE config (CLI flag), bukan di sini.
// File ini hanya memuat BuildTask: entry, size, static, output, dll.
module.exports = {
  title: 'Hands-on 02: Eksplorasi Word Embeddings',
  author: 'Pembelajaran Mesin Multimodal (IF25-40304)',
  language: 'id',
  size: 'A4',
  entry: ['hands-on/mgg02-hands-on.html'],
  // Server Vivliostyle menjadikan folder `hands-on/` sebagai root, sehingga
  // referensi `../assets/...` pada HTML perlu dipetakan ke folder assets asli
  // (resolve `../assets` dari root server `hands-on/` → `assets/` project).
  static: {
    '/assets': '../assets',
  },
  workspaceDir: '.vivliostyle',
  output: 'pdf/mgg02-hands-on.pdf',
};
