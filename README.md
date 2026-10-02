# Pembelajaran Mesin Multimodal

Portal perkuliahan **Pembelajaran Mesin Multimodal (IF25-40304)** — Institut Teknologi Sumatera (ITERA).

> **Situs kuliah: <https://iwawiwi.github.io/multimodal/>**
> Slide tiap pertemuan (HTML) beserta PDF-nya, PDF lembar kerja hands-on, dan kisi-kisi UTS
> tersedia di sana. PDF dibangun otomatis oleh CI dan **tidak disimpan di repositori ini**,
> sehingga tautan PDF tidak dapat dibuka dari tampilan GitHub — bukalah lewat situs.

## Identitas Mata Kuliah

| Item | Keterangan |
| :--- | :--- |
| Kode Mata Kuliah | `IF25-40304` |
| Nama Mata Kuliah | Pembelajaran Mesin Multimodal |
| Beban Studi | 3 SKS |
| Program Studi | Teknik Informatika |
| Fakultas | Teknologi Industri |
| Institusi | Institut Teknologi Sumatera (ITERA) |
| Tahun Akademik | 2026 |
| Dosen Pengampu | I Wayan Wiprayoga Wisesa |
| Surel Dosen | [wayan.wisesa@if.itera.ac.id](mailto:wayan.wisesa@if.itera.ac.id) |

## Silabus Materi Perkuliahan (16 Pertemuan)

| Pertemuan | Topik | Jenis | Hands-on |
| :--- | :--- | :--- | :--- |
| 01 | Pengantar Pembelajaran Mesin Multimodal | Kuliah | — |
| 02 | Representasi Modalitas I: Teks | Kuliah | Eksplorasi Word Embeddings |
| 03 | Representasi Modalitas II: Gambar | Kuliah | Feature Extraction Gambar |
| 04 | Representasi Modalitas III: Audio & Video | Kuliah | Representasi Audio & Video |
| 05 | Strategi Fusi Multimodal I: Early & Late Fusion | Kuliah | — |
| 06 | Strategi Fusi Multimodal II: Intermediate & Hybrid Fusion | Kuliah | Early, Late & Intermediate Fusion |
| 07 | Penyejajaran (Alignment): Temporal & Structural | Kuliah | — |
| 08 | **Ujian Tengah Semester (UTS)** | Evaluasi | — |
| 09 | Arsitektur Transformer Multimodal | Kuliah | — |
| 10 | Aplikasi 1: Image Captioning | Kuliah | — |
| 11 | Aplikasi 2: VQA & Analisis Sentimen Multimodal | Kuliah | — |
| 12 | Topik Lanjutan: Generasi Multimodal & Etika | Kuliah | — |
| 13 | Evaluasi Model Multimodal | Kuliah | Protokol Evaluasi & Uji Signifikansi |
| 14 | Studi Kasus Terpadu | Kuliah | — |
| 15 | Review Materi | Kuliah | — |
| 16 | **Ujian Akhir Semester (UAS)** | Evaluasi | — |

## Materi Tersedia

Tabel di bawah mendaftar **nama berkas** materi tiap pertemuan; seluruh berkasnya disajikan
melalui [**situs kuliah**](https://iwawiwi.github.io/multimodal/). Nama berkas sengaja tidak
ditautkan: berkas HTML di repositori hanya tampil sebagai kode sumber saat dibuka dari GitHub,
dan berkas PDF memang tidak ada di repositori (lihat catatan di bawah tabel).

| Pertemuan | Slide Interaktif | Dokumen PDF | Lembar Kerja |
| :--- | :--- | :--- | :--- |
| 01 | `mgg01.html` | `pdf/mgg01.pdf` | — |
| 02 | `mgg02.html` | `pdf/mgg02.pdf` | `hands-on/mgg02-hands-on.html` |
| 03 | `mgg03.html` | `pdf/mgg03.pdf` | `hands-on/mgg03-hands-on.html` |
| 04 | `mgg04.html` | `pdf/mgg04.pdf` | `hands-on/mgg04-hands-on.html` |
| 05 | `mgg05.html` | `pdf/mgg05.pdf` | — |
| 06 | `mgg06.html` | `pdf/mgg06.pdf` | `hands-on/mgg06-hands-on.html` |
| 07 | `mgg07.html` | `pdf/mgg07.pdf` | — |
| 08 (UTS) | — | `pdf/uts-kisi-kisi.pdf` *(kisi-kisi)* | — |
| 09 | `mgg09.html` | `pdf/mgg09.pdf` | `hands-on/mgg09-hands-on.html` |
| 10 | `mgg10.html` | `pdf/mgg10.pdf` | — |
| 11 | `mgg11.html` | `pdf/mgg11.pdf` | — |
| 12 | `mgg12.html` | `pdf/mgg12.pdf` | — |
| 13 | `mgg13.html` | `pdf/mgg13.pdf` | `hands-on/mgg13-hands-on.html` |
| 14 | `mgg14.html` | `pdf/mgg14.pdf` | — |
| 15 | `mgg15.html` | `pdf/mgg15.pdf` | — |

> PDF slide tiap pertemuan dan PDF lembar kerja hands-on dirender otomatis oleh CI saat
> push, jadi **tidak disimpan di repositori** dan hanya tersedia lewat
> [situs kuliah](https://iwawiwi.github.io/multimodal/). Kisi-kisi UTS bersifat publik dan
> tersedia sebagai PDF **dan** HTML (`dokumen/uts-kisi-kisi.html`); soal, kunci, dan rubrik
> ujian tidak diterbitkan di repositori ini (lihat `AGENTS.md` D-A12).

## Situs

Situs ini di-deploy ke GitHub Pages dan dapat diakses melalui:

**https://iwawiwi.github.io/multimodal/**

Semua PDF (slide tiap pertemuan dan lembar kerja hands-on) hanya tersedia di sana.

### Menjalankan secara lokal

Seluruh berkas HTML memakai path relatif, jadi harus disajikan lewat HTTP
(bukan `file://`) agar CSS, font, dan KaTeX termuat dengan benar:

```bash
npm start          # http://127.0.0.1:8080/index.html
```

Setara dengan `python3 -m http.server 8080 --bind 127.0.0.1`. Tekan `Ctrl+C`
untuk berhenti. Tidak ada dependensi tambahan yang perlu dipasang — server ini
memakai modul `http.server` bawaan Python 3.
