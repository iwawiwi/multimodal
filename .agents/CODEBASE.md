# Codebase Knowledge — Pembelajaran Mesin Multimodal (2026)

> Ringkasan arsitektur, struktur file, konvensi desain, dan workflow otomasi proyek ini.
> Ditulis otomatis saat onboarding awal.

---

## 1. Visi Proyek

Ini adalah **portal perkuliahan web statis** untuk mata kuliah **Pembelajaran Mesin Multimodal (IF25-40304, 3 SKS)** di Program Studi Teknik Informatika, Institut Teknologi Sumatera (ITERA), semester 2026.

Portal terdiri dari:
- **Landing page** (`index.html`) — Daftar 16 pertemuan dengan kartu mingguan seragam.
- **Slide presentasi interaktif** (`mggXX.html`) — Menggunakan **Reveal.js 5.1.0** dengan tema **Catppuccin Latte**.
- **Desain system & skill** (`.agents/skills/lecture-slide-designer/`) — Template, token desain, script otomasi.

---

## 2. Struktur File

```
multimodal-v2/
├── index.html                          # Portal perkuliahan (sticky hero + week cards grid)
├── mgg01.html                          # Slide Pertemuan 01 (25 slide Reveal.js)
├── css/
│   ├── portal.css                      # Styling portal (header, cards, footer, responsive)
│   └── catppuccin-latte.css            # Tema Reveal.js (full component system, ~600 baris)
├── assets/img/
│   ├── logo_1.png                      # Logo alternatif
│   ├── logo_2.png                      # Logo ITERA (digunakan di header)
│   ├── dikti-saintek-berdampak-black.svg
│   └── dikti-saintek-berdampak-color.svg  # Logo Kementerian Dikti
├── origin/                             # Sumber PPTX asli (15 file, pertemuan 01-15)
│   ├── Pembelajaran Mesin Multimodal - Pertemuan 01 v1.0.pptx
│   ├── Pembelajaran Mesin Multimodal - Pertemuan 01 v0.1.pptx
│   └── ... (sampai Pertemuan 15)
├── pdf/
│   └── mgg01.pdf                       # PDF hasil export (78KB, git skip-worktree)
├── .gitignore
└── .agents/
    ├── CODEBASE.md                     # ← File ini
    └── skills/lecture-slide-designer/
        ├── SKILL.md                    # Skill definition untuk pi (desain guidelines lengkap)
        ├── references/
        │   └── design-tokens.md        # Token warna, tipografi, komponen, layout archetypes
        ├── resources/
        │   └── slide-template.html     # Template HTML untuk slide baru (placeholder {{}})
        └── scripts/
            ├── extract_pptx.py         # Ekstrak teks & notes dari PPTX
            ├── validate_slide.py       # Validasi HTML (tag balancing, broken links)
            └── export_pdf.py           # Export slide ke PDF via headless Chrome
```

---

## 3. Stack Teknologi

| Layer | Teknologi |
|:---|:---|
| Presentasi | **Reveal.js 5.1.0** (CDN) |
| Tema Warna | **Catppuccin Latte** (custom CSS) |
| Font | **Plus Jakarta Sans** (sans), **JetBrains Mono** (mono) via Google Fonts |
| Ikon | **Google Material Symbols Outlined** via Google Fonts |
| Matematika | **KaTeX 0.16.9** (CDN, via RevealMath plugin) |
| Syntax Highlight | **highlight.js** (via RevealHighlight plugin) |
| Speaker Notes | RevealNotes plugin (tekan `S`) |
| PDF Export | Headless Chrome + local HTTP server (`export_pdf.py`) |

**Zero npm / Zero bundler** — seluruh dependensi dimuat dari CDN. Tidak ada `package.json`, `node_modules`, atau build step.

---

## 4. Design System — Catppuccin Latte

### 4.1 Palet Warna (Semantic Tokens)

| Token | Hex | Peran |
|:---|:---:|:---|
| `--ctp-base` | `#eff1f5` | Background utama slide & portal |
| `--ctp-mantle` | `#e6e9ef` | Background card & container |
| `--ctp-crust` | `#dce0e8` | Surface dalam, footer |
| `--ctp-text` | `#4c4f69` | Teks primer & heading |
| `--ctp-subtext1` | `#5c5f77` | Teks sekunder |
| `--ctp-blue` | `#1e66f5` | **Aksen primer** (heading, tombol, link) |
| `--ctp-mauve` | `#8839ef` | Konsep kunci, `<code>` |
| `--ctp-teal` | `#179299` | Arsitektur, definisi teknis |
| `--ctp-green` | `#40a02b` | Kelebihan/positif |
| `--ctp-peach` | `#fe640b` | Peringatan/tantangan |
| `--ctp-maroon` | `#e64553` | Kekurangan/negatif |

### 4.2 Tipografi

- **Heading:** Plus Jakarta Sans, `font-weight: 800`, `letter-spacing: -0.025em`
- **Body:** Plus Jakarta Sans, `0.84em`, `line-height: 1.5`
- **Code/Number:** JetBrains Mono, `font-weight: 700`
- **Zero CQI policy** — Tidak menggunakan `container-type` atau `cqi` units untuk menghindari bug layout recursion di Chromium DevTools.

### 4.3 Aturan Desain Kritis

1. **Zero-Badge Policy** — Tidak ada pill badge (`.c-badge`) di slide. Gunakan label tipografi bersih.
2. **Zero-Nested-Flex** — Di dalam `.c-card`, gunakan CSS Grid, bukan nested flexbox (mencegah freeze DevTools).
3. **Zero Viewport Height Units** — Tidak pakai `vh` di dalam slide (breaks Reveal.js transform scale).
4. **Fragment `fade-in` Only** — Tidak ada `fade-up`, `fade-left`, dll. (mencegah layout shift).
5. **Transition `fade` Only** — Tidak ada `zoom` (stutter pada proyektor kelas 30Hz/60Hz).
6. **Never Fragment Tables/Formulas/Diagrams** — Fragment hanya untuk CPL dan diskusi.

---

## 5. Arsitektur Portal (`index.html`)

### 5.1 Header (Sticky Hero)
- **Layout:** Edge-to-edge, `position: sticky`, `backdrop-filter: blur(16px)`
- **Kiri:** Logo ITERA + Logo Dikti (side-by-side, image only)
- **Tengah:** Kode mata kuliah, SKS, nama prodi, judul mata kuliah
- **Kanan:** Nama dosen & email

### 5.2 Week Cards Grid
- Grid responsif: `grid-template-columns: repeat(auto-fill, minmax(360px, 1fr))`
- Setiap card: `min-height: 420px`, flex column, uniform title/desc/topics/actions
- **3 state:** `active-ready` (biru, interaktif), `disabled` (abu-abu, button disabled), `milestone` (peach, untuk UTS/UAS)
- Dual action buttons: "Buka Slide" (primary) + "Ekspor PDF" (secondary)

### 5.3 Footer
- Cheatsheet pintasan keyboard (compact, inline flex-wrap chips)
- Footer institusi (copyright ITERA)

---

## 6. Arsitektur Slide (`mggXX.html`)

### 6.1 Persistent Deck Chrome
- **Header bar** (48px, fixed): Logo kiri, kontrol kanan (aspect ratio switcher, overview, pintasan, portal link)
- **Progress bar** (2.5px hairline): Gradient biru-sapphire, 0%-100%
- **Footer bar** (36px, fixed): Kode mata kuliah kiri, topic button tengah (buka popover), navigasi kanan

### 6.2 Aspect Ratio Engine
5 mode yang tersimpan di `localStorage`:

| Mode | Width × Height | Target |
|:---|:---:|:---|
| Auto | Dynamic | Auto-detect berdasarkan rasio viewport |
| 16:9 | 1280 × 720 | Monitor/TV FHD |
| 16:10 | 1280 × 800 | MacBook |
| 4:3 | 1024 × 768 | Proyektor kelas XGA |
| Mobile | 720 × 1000+ | Smartphone |

Script auto-detect di mode Auto:
- `ratio >= 1.65` → 16:9
- `ratio >= 1.45` → 16:10
- `ratio < 1.15 || width <= 768` → Mobile
- else → 4:3

### 6.3 Topic Navigation Popover
- Floating bottom-up popover di atas footer
- Auto-generate daftar isi dari `<h2>` / `<h1>` di setiap `<section>`
- Fitur search/filter real-time
- Active slide highlighting + auto-scroll
- Dismiss: click-outside atau `Esc`

### 6.4 Struktur Slide Pertemuan 01 (24 slide)
1. Cover (judul + identitas dosen)
2. CPL / Tujuan Pembelajaran (3 kompetensi)
3-8. Bagian 1: Apa Itu Multimodal? (definisi, motivasi, contoh)
9-16. Bagian 2: Tantangan Fundamental (representasi, alignment, fusion)
17-20. Bagian 3: Penerapan Model (Image Captioning, VQA, Sentimen, Retrieval, Pipeline)
21. Rangkuman
22. Diskusi Aktif
23. Referensi
24. Penutup & Teaser

---

## 7. 6 Academic Layout Archetypes

Desain system mendefinisikan 6 pola layout yang harus digunakan secara bervariasi (≤25% card grids, ≥75% archetype lain):

| # | Archetype | Class | Kapan Digunakan |
|:---|:---|:---|:---|
| 1 | Hero Diagram & Narrative Split | `.grid-2-1` / `.grid-1-2` + `.diagram-canvas` + `.narrative-pane` | Arsitektur deep learning, embedding space |
| 2 | Formula Breakout | `.formula-hero` + `.formula-breakdown` + `.formula-term-box` | Fungsi loss, metrik, persamaan matematis |
| 3 | Analytical Comparison Matrix | `.c-table` | Trade-off antar metode, evaluasi komparatif |
| 4 | Concrete Case Showcase | `.case-showcase` + `.case-input-pane` + `.case-model-pane` | Studi kasus riil, grounding teori |
| 5 | Horizontal Pipeline | `.pipeline-flow` + `.pipeline-step` | Alur pemrosesan end-to-end |
| 6 | Big Idea Canvas | `.big-idea-canvas` + `.big-idea-question` + `.big-idea-takeaway` | Pertanyaan pemantik, paradoks, transisi bagian |

---

## 8. Modular Pedagogical Blueprint

Setiap deck slide mengikuti struktur:

### Invariant Anchors (wajib ada di setiap pertemuan):
1. **Cover Slide** — Judul + identitas dosen
2. **CPL (3 kompetensi)** — Dengan `.grid-3` dan `.c-num-circle`
3. **Rangkuman** — Grid takeaway cards
4. **Diskusi Aktif** — 3 pertanyaan terbuka
5. **Referensi** — Sitasi akademik
6. **Penutup & Teaser** — Preview pertemuan berikutnya

### Fluid Core Modules (12-18 slide inti):
Dipilih berdasarkan **topik typology**:

| Typology | Topik Contoh | Archetype Chain |
|:---|:---|:---|
| Teoritis & Matematis | InfoNCE, Contrastive Loss | Big Idea → Formula → Table |
| Arsitektur & DL | CLIP, Cross-Attention | Diagram → Pipeline → Table |
| Sistem & Aplikasi | VQA, Image Captioning | Case → Pipeline → Table |
| Konseptual & Etika | Bias, Hallucination | Big Idea → Case → Table |

**Volume:** 18-25 slide per pertemuan (~2-3 menit/slide untuk 50-75 menit kuliah).

---

## 9. Workflow Otomasi

### 9.1 Ekstraksi Konten dari PPTX
```bash
uv run --with python-pptx python3 .agents/skills/lecture-slide-designer/scripts/extract_pptx.py "origin/<file>.pptx"
```
Mengambil teks, tabel, dan speaker notes dari file PPTX sumber.

### 9.2 Validasi HTML
```bash
python3 .agents/skills/lecture-slide-designer/scripts/validate_slide.py mggXX.html
python3 .agents/skills/lecture-slide-designer/scripts/validate_slide.py index.html
```
Mengecek: tag HTML seimbang, link lokal tidak broken.

### 9.3 Export PDF
```bash
python3 .agents/skills/lecture-slide-designer/scripts/export_pdf.py mggXX.html
```
Menggunakan headless Chrome → render `?print-pdf` → simpan ke `pdf/mggXX.pdf`.

### 9.4 Git PDF Management
```bash
git update-index --skip-worktree pdf/mggXX.pdf    # Hindari bloat repo
git update-index --no-skip-worktree pdf/mggXX.pdf  # Unskip saat release
```

---

## 10. Status Saat Ini

| Item | Status |
|:---|:---|
| `index.html` (portal) | ✅ Selesai, kartu minggu + milestone UTS/UAS |
| `mgg01.html` | ✅ Selesai, 25 slide |
| `mgg02.html` | ✅ Selesai, 30 slide |
| `mgg03.html` | ✅ Selesai, 25 slide |
| `mgg04.html` | ✅ Selesai, 30 slide |
| `mgg05.html` | ✅ Selesai, 28 slide |
| `mgg06.html` | ✅ Selesai, 25 slide |
| `mgg07.html` – `mgg15.html` | ❌ Belum dibuat |
| Hands-on 02/03/04/06 | ✅ `hands-on/mggNN-hands-on.html` |
| Tugas 02/03/04/06 | ✅ `.md` + `.tex` (LaTeX, `tugas-style.sty`) — didistribusikan via LMS, tidak lewat portal (D-A11) |
| Skill & design system | ✅ Lengkap (SKILL.md, tokens, template, scripts) |
| CI (GitHub Pages) | ✅ Export PDF slide + hands-on |

> Status mutakhir, keputusan aktif, dan aturan kerja ada di **`AGENTS.md`**
> (dimuat otomatis oleh pi). Dokumen ini menjelaskan arsitektur, bukan status.

---

## 11. Konvensi Penamaan File

- Slide: `mgg{XX}.html` (2 digit, zero-padded: `mgg01.html`, `mgg02.html`)
- PDF: `pdf/mgg{XX}.pdf`
- Template placeholder: `{{WEEK_NUM_2DIGIT}}`, `{{TOPIC_TITLE}}`, `{{WEEK_NUM}}`

---

## 12. Catatan Teknis Penting

1. **Reveal.js canvas positioning** — `.reveal` di-positioning absolut dengan `top: 50.5px` dan `bottom: 36px` untuk mengakomodasi persistent header (48px) + progress bar (2.5px) + footer (36px) = offset total ~86.5px.

2. **Aspect mode CSS hooks** — Class `.aspect-mobile`, `.aspect-4-3`, `.aspect-16-10`, `.aspect-16-9` di-attach ke `document.body` oleh JavaScript, dan CSS menggunakannya sebagai responsive override (bukan container queries).

3. **Debounced resize handler** — 200ms debounce dengan dimension guard (`if (cfg.width !== dim.width || cfg.height !== dim.height)`) sebelum `Reveal.configure()` untuk mencegah layout thrashing saat DevTools dibuka/di-resize.

4. **PDF print mode** — URL parameter `?print-pdf&pdfSeparateFragments=false` untuk rendering PDF tanpa fragment animation.
