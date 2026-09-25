# Pembelajaran Mesin Multimodal

Portal perkuliahan **Pembelajaran Mesin Multimodal (IF25-40304)** — Institut Teknologi Sumatera (ITERA).

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

| Pertemuan | Slide Interaktif | Dokumen PDF | Lembar Kerja |
| :--- | :--- | :--- | :--- |
| 01 | [mgg01.html](mgg01.html) | [pdf/mgg01.pdf](pdf/mgg01.pdf) | — |
| 02 | [mgg02.html](mgg02.html) | [pdf/mgg02.pdf](pdf/mgg02.pdf) | [hands-on/mgg02-hands-on.html](hands-on/mgg02-hands-on.html) |
| 03 | [mgg03.html](mgg03.html) | [pdf/mgg03.pdf](pdf/mgg03.pdf) | [hands-on/mgg03-hands-on.html](hands-on/mgg03-hands-on.html) |
| 04 | [mgg04.html](mgg04.html) | [pdf/mgg04.pdf](pdf/mgg04.pdf) | [hands-on/mgg04-hands-on.html](hands-on/mgg04-hands-on.html) |
| 05 | [mgg05.html](mgg05.html) | [pdf/mgg05.pdf](pdf/mgg05.pdf) | — |
| 06 | [mgg06.html](mgg06.html) | [pdf/mgg06.pdf](pdf/mgg06.pdf) | [hands-on/mgg06-hands-on.html](hands-on/mgg06-hands-on.html) |
| 07 | [mgg07.html](mgg07.html) | [pdf/mgg07.pdf](pdf/mgg07.pdf) | — |
| 08 (UTS) | — | [pdf/uts-kisi-kisi.pdf](pdf/uts-kisi-kisi.pdf) *(kisi-kisi)* | — |
| 09 | [mgg09.html](mgg09.html) | [pdf/mgg09.pdf](pdf/mgg09.pdf) | [hands-on/mgg09-hands-on.html](hands-on/mgg09-hands-on.html) |
| 10 | [mgg10.html](mgg10.html) | [pdf/mgg10.pdf](pdf/mgg10.pdf) | — |
| 11 | [mgg11.html](mgg11.html) | [pdf/mgg11.pdf](pdf/mgg11.pdf) | — |
| 12 | [mgg12.html](mgg12.html) | [pdf/mgg12.pdf](pdf/mgg12.pdf) | — |
| 13 | [mgg13.html](mgg13.html) | [pdf/mgg13.pdf](pdf/mgg13.pdf) | [hands-on/mgg13-hands-on.html](hands-on/mgg13-hands-on.html) |
| 14 | [mgg14.html](mgg14.html) | [pdf/mgg14.pdf](pdf/mgg14.pdf) | — |
| 15 | [mgg15.html](mgg15.html) | [pdf/mgg15.pdf](pdf/mgg15.pdf) | — |

> PDF dirender otomatis oleh CI saat push — tidak disimpan di repositori. Kisi-kisi UTS bersifat publik; soal dan kunci ujian tidak diterbitkan di repositori ini (lihat `AGENTS.md` D-A12).

## Situs

Situs ini di-deploy ke GitHub Pages dan dapat diakses melalui:

**https://iwawiwi.github.io/multimodal/**

### Menjalankan secara lokal

Seluruh berkas HTML memakai path relatif, jadi harus disajikan lewat HTTP
(bukan `file://`) agar CSS, font, dan KaTeX termuat dengan benar:

```bash
npm start          # http://127.0.0.1:8080/index.html
```

Setara dengan `python3 -m http.server 8080 --bind 127.0.0.1`. Tekan `Ctrl+C`
untuk berhenti. Tidak ada dependensi tambahan yang perlu dipasang — server ini
memakai modul `http.server` bawaan Python 3.
