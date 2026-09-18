# AGENTS.md — Pembelajaran Mesin Multimodal (IF25-40304)

Panduan kerja untuk agen AI di repo ini. Pi memuat file ini otomatis setiap
sesi (`.agents/course-config.md` **tidak** dimuat otomatis — ia dibaca oleh
skill, bukan oleh pi).

**Baca ini dulu sebelum mengubah apa pun.** Repo ini dikerjakan beberapa agen
secara paralel; bagian *Status* dan *Keputusan Aktif* ada di sini supaya
pekerjaan tidak saling menimpa.

> Detail teknis proyek: `.agents/CODEBASE.md`
> Aturan desain: `.agents/skills/lecture-slide-designer/references/design-decisions.md`
> Jadwal & identitas kursus: `.agents/course-config.md`
> Kosakata visual: `.agents/skills/lecture-slide-designer/references/visual-vocabulary.md`

---

## 1. Aturan Kerja (WAJIB)

1. **JANGAN commit atau push tanpa instruksi eksplisit dari pengguna.**
   Termasuk `git add` tanpa diminta. Selesaikan pekerjaan, laporkan, tunggu.
2. **PDF tidak pernah di-commit.** Dirender oleh CI (`.github/workflows/deploy-pages.yml`).
   `tugas/*.pdf|aux|log|toc|ver|hst|out|html` dan `pdf/` sudah di-`.gitignore`.
3. **Satu branch per minggu** (`mgg03`, `mgg04`, …) bila diminta branch.
   Jangan merge/push sendiri. Branch yang sudah ter-merge boleh dihapus dengan
   `git branch -d` (aman, bukan `-D`).
4. **Bahasa Indonesia** untuk seluruh konten slide, tugas, dan hands-on.
   Identifier/path/command/error string tetap persis (jangan diterjemahkan).
5. **Jangan sentuh file di luar lingkup tugas.** Jika terpaksa (mis. `index.html`
   saat menambah deck), sebutkan di laporan.
6. **Sebelum melapor, selalu jalankan gate validasi** (§4). Jangan mengklaim
   "aman" tanpa menjalankan `validate_slide.py` dan `npm run measure`.

## 2. Keputusan Aktif (mengikat agen berikutnya)

Keputusan yang sudah disetujui pengguna dan **berlaku sampai diubah eksplisit**:

- **D-A01 — Rebalancing tiga pilar.** Tiga pilar (Representasi, Alignment, Fusi)
  harus punya rumah masing-masing di jadwal:
  - **Representasi** → W02 (Teks), W03 (Gambar), W04 (Audio & Video).
  - **Fusi** → W05 (Early & Late), W06 (Intermediate & Hybrid).
  - **Alignment** → **W07** — *bukan* "Mekanisme Attention". Attention diajarkan
    di dalam W07 sebagai mekanisme penyejajaran (dari DTW/HMM → attention adaptif).
  - Blok alignment yang ada di deck sumber W06 dipindahkan ke W07.
  - Aplikasi dipadatkan: W10 (Captioning), W11 (VQA + Sentimen), W12 (Generasi & Etika).
  - W13 = Evaluasi Model Multimodal, W14 = Studi Kasus Terpadu, W15 = Review Materi.
  - W08 (UTS) dan W16 (UAS) **tidak bergeser**.
- **D-A02 — Kepadatan deck = Opsi A.** Target **24–29 slide** per deck (maksimum 35).
  Deck sumber PPTX (~33–45 slide) harus dipadatkan; jangan salin mentah.
- **D-A03 — `index.html` dan `.agents/course-config.md` harus sinkron.**
  Judul minggu di kedua file wajib identik. Bila mengubah salah satu, ubah
  pasangannya di commit yang sama.
- **D-A04 — Tugas mingguan punya dua artefak.** `tugas/mggNN-tugas.md` (brief)
  **dan** `tugas/mggNN-tugas.tex` (dokumen LaTeX). `.md` tidak boleh dilewatkan.
  Hands-on: `hands-on/mggNN-hands-on.html` + entri CI (`HANDSON_WEEK=NN`).
- **D-A11 — Tugas didistribusikan lewat LMS, BUKAN lewat portal repo.**
  `index.html`, `README.md`, dan deck **tidak** menautkan berkas tugas, dan PDF
  tugas **tidak** dibangun CI (tetap di-`.gitignore`).
  - **Alasan:** repositori ini publik. Bila tugas diterbitkan lewat portal, berkas
    terbuka untuk angkatan berikutnya (bocor), padahal contoh dan instruksi tugas
    **diperbarui setiap tahun** — versi lama yang beredar merusak penilaian dan
    membuang kerja pembaruan itu.
  - `tugas/` tetap disimpan di repo untuk pelacakan versi dan riwayat revisi;
    hanya *jalur terbit*-nya yang sengaja tidak ada.
  - ❌ Jangan "memperbaiki" ini dengan menambah chip tugas di `index.html`,
    tautan di `README.md`, atau langkah `lualatex` di CI — itu justru meniadakan
    alasan di atas.
  - Saat audit melaporkan "tugas tidak bisa ditemukan", itu **perilaku yang
    diharapkan**, bukan gap.
- **D-A05 — Pola desain yang dipakai sejak mgg04** (detail di `design-decisions.md`):
  - Slide "kategori/karakteristik" → `grid-3` 3 kartu
    (`c-card c-card-{blue,mauve,teal} c-card-accent-top` + `<h3 style="color:...">`),
    ditutup `.c-callout-info`.
  - Slide konsep + gambar → `grid-2` + `.narrative-pane` (maks **3** `narrative-step`;
    4 langkah = overflow di Teks Besar).
  - Ringkasan alur matematis → kartu `c-card` berisi grid `auto 1fr`,
    label **"Alur Data Matematis:"** + KaTeX inline (`$...$`, bukan `$$`).
  - Rumus utama → `.formula-hero` + `.formula-breakdown` (3 `.formula-term-box`);
    setiap simbol wajib didefinisikan (D-017).
  - Atribusi gambar ringkas: `Sumber: [sumber]` (D-019). Jangan mengarang.
  - Slide kelebihan/kekurangan → `.pro-box` + `.con-box` (D-023); diagram
    arsitektur → inline SVG (D-024).
- **D-A06 — Tugas fusion dijadwalkan di akhir W06, bukan W05.**
  Materi fusion disajikan tuntas lebih dulu (W05: Early & Late; W06:
  Intermediate & Hybrid), lalu **satu** tugas terpadu diberikan di akhir W06
  (`T2 + B3 + F3 + H3`): mahasiswa memakai encoder pra-latih **dibekukan** dan
  menggarap hanya lapisan fusi — mengimplementasikan **dan** membandingkan
  Early/Late/Intermediate, lalu memberi argumen pemilihan. Hands-on W06 menjadi
  ajang latihan untuk tugas ini.
  - ❌ **Jangan** memberi tugas di W05: cakupan baru 2 dari 4 strategi, sehingga
    "pilih strategi terbaik" tidak adil dan bertabrakan dengan W06.
  - ❌ **Jangan** menumpuk tugas di W05/W06/W07 sekaligus — UTS mencakup W01–W07,
    dan 6 tugas berurutan sebelum UTS terlalu berat.
  - Hands-on berformat **code-first** (D-011); hands-on tanpa kode tidak sah.
- **D-A07 — W05 tanpa hands-on; penerapannya lewat studi kasus komprehensif.**
  W05 tidak punya laboratorium. Sebagai gantinya, studi kasus deteksi emosi disajikan
  dalam tiga langkah (*rumusan masalah* → *penerapan* → *analisis*) dan wajib:
  - menanyakan lebih dulu, menjawab kemudian (jangan sajikan solusi sebelum soal);
  - menutup kerangka yang dijanjikan (empat masalah klasik × strategi fusi);
  - memuat slide "ketika fusi tidak mengalahkan unimodal";
  - menyertakan jangkar konkret (dataset dan/atau metrik).
  Rincian: D-026 di `design-decisions.md`.
  - ❌ Hanya menambah hands-on W05 bila benar-benar diminta; lingkupnya wajib dibatasi
    pada "implementasikan dan bandingkan early vs late" (bukan "pilih yang terbaik").
- **D-A08 — Notasi matematika di dalam diagram memakai KaTeX (D-029).**
  Simbol di dalam SVG **tidak boleh** ditulis sebagai teks literal.
  Kata yang melabeli kotak tetap `<text>` (`Visual`, `Konkatenasi`); setiap
  **simbol** memakai `<foreignObject>` + KaTeX `\(...\)`.
  - ❌ `<text>x_A</text>` → underscore tampil mentah, berbeda dari slide rumus.
  - ❌ `\(...\)` langsung di dalam `<text>` → KaTeX memberi kotak 0×0 (tak terlihat).
  - Ditegakkan linter (check #10 & #11). Semua deck **sudah patuh** — daftar
    pengecualian `MATH_TEXT_GRANDFATHERED` di `scripts/validate_slide.py` kosong;
    jangan isi ulang kecuali ada deck warisan baru.
- **D-A09 — Setiap minggu ber-hands-on punya satu slide jembatan**
  ("Latihan Terbimbing") **tepat SEBELUM** slide Rangkuman, dengan tautan ke
  `hands-on/mggNN-hands-on.html` dan PDF-nya. Isinya ringkas: tujuan + 3–4 langkah;
  slide ini **menunjuk** ke lab, bukan menggandakannya. Markup: **2×2 `.bridge-grid`**
  berisi `.bridge-step` bernomor + `.c-callout-info` + baris `.slide-links` dengan
  dua tombol (`.slide-btn-primary` "Buka Lembar Kerja", `.slide-btn-secondary`
  "Unduh PDF").
  - ❌ Jangan memakai `.pipeline-flow` 4 kolom di sini: deskripsi 100+ karakter
    terpecah di kolom sempit (kartu ~220px) dan tautan melebar 832px di mode 4:3.
    Grid 2×2 memangkas tinggi kartu menjadi ~95px.
  - ❌ Jangan menaruh path mentah (`hands-on/mggNN-…`) sebagai teks isi.
  - ❌ Jangan menaruhnya setelah Rangkuman: ringkasan harus menutup sesi.
  - Bila PPTX sumber punya slide hands-on, isinya **dipulihkan** — bukan dikarang.
    Bila tidak ada (mis. W04), slide boleh baru tetapi wajib mencerminkan isi
    hands-on yang sebenarnya.
  - Anggaran slide D-A02 dinaikkan menjadi **24–30** untuk minggu ber-hands-on.
  - Ditegakkan linter (check #12 & #13); rincian di D-030 `design-decisions.md`.
- **D-A10 — Tautan di PDF harus absolut ke host produksi.** Chrome membekukan
  URL server sementara (`http://127.0.0.1:8765/…`) ke anotasi PDF, sehingga PDF
  yang terbit memuat tautan mati. `scripts/export_pdf.py` menulis ulang **hanya
  target tautan** `hands-on/` dan `pdf/` menjadi absolut; path aset tetap relatif.
  Base URL diresolusi berurutan: `SITE_BASE_URL` → `PAGES_BASE_URL` (output
  `actions/configure-pages`, di-wire di CI) → `https://<owner>.github.io/<repo>`
  dari `GITHUB_REPOSITORY` → kosong.
  - ❌ **Jangan hardcode** URL repo. Repo ini akan ditransfer ke organisasi lain;
    resolusi dari env membuat tautan tetap benar tanpa sunting manual.
  - CI menjalankan `configure-pages` **sebelum** build PDF agar `base_url` tersedia.
  - HTML sumber tetap memakai path relatif (agar situs jalan di host mana pun).

## 3. Status Deck (perbarui saat menyelesaikan deck)

| Deck | Topik | Slide | Status |
| :--- | :--- | :---: | :--- |
| `mgg01.html` | Pengantar Pembelajaran Mesin Multimodal | 25 | ✅ selesai |
| `mgg02.html` | Representasi Modalitas I: Teks | 30 | ✅ selesai |
| `mgg03.html` | Representasi Modalitas II: Gambar | 25 | ✅ selesai |
| `mgg04.html` | Representasi Modalitas III: Audio & Video | 30 | ✅ selesai |
| `mgg05.html` | Strategi Fusi I: Early & Late Fusion | 28 | ✅ selesai |
| `mgg06.html` | Strategi Fusi II: Intermediate & Hybrid Fusion | 25 | ✅ selesai |
| `mgg07.html` … `mgg15.html` | — | — | ❌ belum dibuat |

  > Angka slide di atas diverifikasi terhadap `<section>` tiap berkas. Perbarui
  > tabel ini setiap kali deck berubah — `CODEBASE.md` §10 pernah tertinggal
  > dan melaporkan angka yang salah.

Artefak pendukung:

| Artefak | Ada |
| :--- | :--- |
| `hands-on/mgg02,03,04,06-hands-on.html` | ✅ |
| `tugas/mgg02,03,04,06-tugas.md` + `.tex` | ✅ (via LMS — lihat D-A11) |
| CI export `mgg01`–`mgg06` + hands-on 02/03/04/06 | ✅ |

> Setiap minggu yang punya hands-on **wajib** lengkap: file hands-on, entri
> `HANDSON_WEEK` di CI, judul di `vivliostyle.config.js`, kolom hands-on di
> `course-config.md`, dan chip di `index.html`.

## 4. Validasi (jalankan sebelum melapor)

```bash
python3 scripts/validate_slide.py mggNN.html   # tag, link, pelanggaran desain
npm run measure -- mggNN.html                  # overflow @ Teks Besar 960×540
git diff --check                               # whitespace
```

`measure_overflow.js` **hanya** menguji mode Teks Besar. Untuk memastikan 5 mode
(16:9, 16:10, 4:3, Teks Besar, Mobile), pakai probe headless Chrome + CDP
(buat sementara di `scripts/`, **hapus setelah selesai**).

**Target: 0 overflow di semua mode, headroom ≥ ~15px di Teks Besar.** Bila mepet,
rapatkan margin lokal (bukan mengecilkan font global) — atau pecah slide (D-009/D-016).

## 5. Struktur & Konvensi

```text
mggNN.html                     deck Reveal.js (satu file mandiri, boilerplate seragam)
index.html                     portal: kartu minggu + milestone UTS/UAS
css/catppuccin-latte.css       tema + komponen (sumber kebenaran komponen)
hands-on/mggNN-hands-on.html   lembar kerja (Prism baked, gaya code-first)
tugas/mggNN-tugas.{md,tex}     tugas mingguan (LaTeX pakai tugas-style.sty)
origin/*.pptx                  sumber asli (gitignored, TIDAK dipublikasikan)
scripts/                       validate_slide.py, measure_overflow.js, export_pdf.py, chrome_print_pdf.js
.agents/                       konteks proyek (CODEBASE.md, course-config.md)
```

- Deck baru: **salin boilerplate** dari deck terakhir (`mgg05.html`) — header,
  aspect switcher, footer, topic popover, `Reveal.initialize`, `setAspectMode`.
  Jangan tulis ulang dari nol.
- Total slide: `<span id="deck-slide-total">NN</span>` harus cocok dengan jumlah
  `<section>`. Nomor komentar `<!-- SLIDE N: ... -->` harus berurutan.
- Setiap `<section>` diberi `<aside class="notes">` (catatan dosen).
- Ekstraksi PPTX: `python3 /tmp/px.py "<file.pptx>"` (parser zip+XML tanpa
  dependensi; `python-pptx` tidak terpasang). Salin ulang bila `/tmp` bersih.

## 6. Jebakan yang Sudah Diketahui

- Boilerplate `<html>`/`<head>` **hanya boleh muncul sekali**. Menempel mentah
  blok boilerplate ke dalam file yang sudah ada menghasilkan tag bersarang.
- `$...$` = KaTeX inline; `$$...$$` = display (jadi blok terpusat). Untuk kartu
  "Alur Data Matematis" pakai inline `$...$`.
- `.diagram-canvas img` sudah punya `max-height: 260px` (css baris ~710).
  Override inline `max-height: none` akan merusak proporsi gambar.
- Gambar line-art berlatar putih → jadikan transparan + tint `#4c4f69`
  (`--ctp-text`); jangan tempel PNG berlatar putih di kanvas mantle.
- Token warna terlarang: `--ctp-red`, `--ctp-yellow`, `--ctp-sky`, `--ctp-pink`,
  `--ctp-rosewater`, `--ctp-flamingo` (linter menolak). Lihat `design-tokens.md`.
- Jangan pakai `.c-badge`, `data-transition="zoom"`, fragment `fade-up/-down/…`,
  atau satuan `cqi`/`vh` di slide.
- Referensi **wajib** pakai styled `<ol>` (monospace `[n]` + grid + hairline) — D-002.
- Penutup **wajib** layout minimal terpusat (bukan label "Selesai" + kartu) — D-004.
- Diskusi **wajib** 3 `.c-callout-*` bertumpuk (info→warning→success) — D-005.
