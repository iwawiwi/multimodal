---
title: "Tugas Individu 09"
subtitle: "Menyejajarkan Ruang Embedding — InfoNCE, Penyelarasan, dan Model Pra-latih"
author: "IF25-40304 · Pembelajaran Mesin Multimodal · Institut Teknologi Sumatera"
date: "Pertemuan 09"
geometry: margin=2.5cm
fontsize: 11pt
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes: |
  \usepackage{fvextra}
  \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,commandchars=\\\{\}}
  \usepackage{fancyhdr}
  \pagestyle{fancy}
  \fancyhead[L]{\small IF25-40304 · Pembelajaran Mesin Multimodal}
  \fancyhead[R]{\small Tugas Individu 09}
  \fancyfoot[C]{\thepage}
---

\thispagestyle{empty}

# Tugas Individu 09: Menyejajarkan Ruang Embedding — InfoNCE, Penyelarasan, dan Model Pra-latih

**Mata Kuliah:** IF25-40304 — Pembelajaran Mesin Multimodal

**Topik:** Arsitektur Transformer Multimodal (Pertemuan 09)

**Bentuk:** Laporan singkat + kode Python (Jupyter Notebook / `.py`)

**Batas Waktu:** 1 minggu setelah pertemuan 09

**Pengerjaan:** Individu

---

## Pendahuluan

Tugas ini melengkapi materi Pertemuan 09 tentang arsitektur Transformer multimodal. Anda akan mengukur sendiri apa yang dimaksud dengan "menyelaraskan dua modalitas", lalu menilai batas arsitektur *dual-encoder* seperti CLIP. Dua gagasan utama yang diverifikasi:

1. Penyelarasan **terukur** — matriks kesamaan, nilai *InfoNCE*, dan *Recall@K* berubah secara dramatis sebelum dan sesudah ruang diselaraskan.
2. Model pra-latih **sudah menyelaraskan untuk kita** — CLIP berhasil mencocokkan gambar dan teks tanpa *cross-attention*, tetapi tetap memiliki batas yang harus dibuktikan.

### Lingkungan yang Diperlukan

- Python 3.8+
- Paket wajib: `numpy` (Soal 1–4), `torch`, `transformers`, `pillow` (Soal 5b)
- Data: sintetis untuk Soal 1–4; satu gambar pilihan sendiri untuk Soal 5b
- Perangkat: CPU memadai untuk Soal 1–4; Soal 5b disarankan memakai GPU bila tersedia (bukan syarat)

```bash
pip install numpy torch transformers pillow
```

> **Batasan cakupan:** Soal 1–4 memakai data multimodal **sintetis**. Kedua modalitas memandang faktor laten yang sama, tetapi modalitas kedua melihatnya melalui rotasi ortogonal. Konstruksi ini membuat penyelarasan dapat dihitung dalam **bentuk tertutup**, sehingga Anda dapat memisahkan persoalan *alignment* dari persoalan pelatihan jaringan.

> **Bobot pra-latih tidak boleh diubah.** Seluruh Soal 5b bersifat **inferensi**. Mengubah atau melatih ulang model dinilai sebagai kesalahan prosedur.

### Ekspektasi Hasil

Dengan `SEED = 42` dan data sintetis pada tugas ini, hasil yang wajar adalah:

- Sebelum penyelarasan: *InfoNCE* di kisaran **10–11** dan *Recall@1* sekitar **1/6**.
- Sesudah penyelarasan: *InfoNCE* turun di bawah **0,2** dan *Recall@1* mencapai **6/6**.
- Suhu mengecil pada data yang sudah selaras menurunkan *loss*, tetapi suhu yang terlalu kecil membuat pelatihan tidak stabil.

Bila hasil Anda menyimpang jauh (misalnya *Recall@1* tetap 1/6 setelah penyelarasan), periksa hal berikut sebelum menyimpulkan:

- data belum dipusatkan sebelum dekomposisi nilai singular;
- sumbu matriks kesamaan tertukar;
- vektor belum dinormalisasi sebelum dihitung kesamaan kosinus.

\newpage

## Pernyataan Masalah

Sebuah katalog berisi ratusan ribu foto produk. Pelanggan mengetik deskripsi bebas, dan sistem harus mengembalikan foto yang paling sesuai. Tidak tersedia data berpasangan berlabel, dan latensi pencarian harus di bawah satu detik.

Ini adalah persoalan **penyejajaran lintas modal**: bagaimana membuat satu gambar dan satu kalimat yang membicarakan hal yang sama berada pada titik yang berdekatan di ruang vektor. Pertemuan 09 menunjukkan bahwa model *dual-encoder* seperti CLIP melakukannya tanpa pernah mempertemukan lapisan kedua modalitas. Anda akan membuktikan mekanismenya dengan angka.

## Soal 1 — Pasangan Sintetis dan Baseline InfoNCE

Sebelum menyelaraskan apa pun, kita harus mengukur seberapa buruk keadaan awalnya. Inilah *baseline* yang menjadi pembanding sepanjang tugas.

### Instruksi

**(a)** Bangkitkan faktor laten bersama `z`, lalu bentuk dua modalitas yang memandang faktor tersebut melalui proyeksi berbeda. Pusatkan `z` terhadap rata-ratanya.

**(b)** Hitung matriks kesamaan kosinus antara kedua modalitas, lalu tampilkan nilai diagonalnya (pasangan benar) dan rerata di luar diagonal.

**(c)** Hitung nilai *InfoNCE* dan *Recall@1* pada keadaan ini.

**(d)** Jawab dalam 3–5 kalimat: mengapa matriks kesamaan tampak acak sebelum penyelarasan, meskipun kedua modalitas sebenarnya mengandung informasi yang sama?

### Contoh Kerangka Kode

```{.python .numberLines startFrom=1}
import numpy as np

SEED, N, DIM, TAU = 42, 6, 4, 0.10
rng = np.random.default_rng(SEED)

# Faktor laten bersama, dipusatkan
z = rng.normal(0.0, 1.0, size=(N, DIM))
z = z - z.mean(axis=0, keepdims=True)

# Modalitas kedua melihat faktor yang sama lewat rotasi ortogonal Q
Q, _ = np.linalg.qr(rng.normal(0.0, 1.0, size=(DIM, DIM)))

gambar = z + 0.10 * rng.normal(size=(N, DIM))
teks = z @ Q.T + 0.10 * rng.normal(size=(N, DIM))

def normalisasi(X):
    return X / np.linalg.norm(X, axis=1, keepdims=True)

def matriks_kesamaan(A, B):
    return normalisasi(A) @ normalisasi(B).T

def infonce(S, tau=TAU):
    Z = S / tau
    Z = Z - Z.max(axis=1, keepdims=True)          # stabilkan secara numerik
    log_softmax = Z - np.log(np.exp(Z).sum(axis=1, keepdims=True))
    return -np.diag(log_softmax).mean()

def recall_at_1(S):
    return int(np.mean(np.argmax(S, axis=1) == np.arange(len(S))) * len(S))

S0 = matriks_kesamaan(gambar, teks)
print("diagonal :", np.diag(S0))
print("rerata luar diagonal: %+.3f" % S0[~np.eye(N, dtype=bool)].mean())
print("InfoNCE  : %.4f" % infonce(S0))
print("Recall@1 : %d/%d" % (recall_at_1(S0), N))
```

\newpage

## Soal 2 — Penyelarasan Bentuk Tertutup

Sekarang kita selaraskan ruang teks terhadap ruang gambar. Karena hubungan antar keduanya ortogonal, penyelarasan optimal dapat dihitung langsung lewat dekomposisi nilai singular (SVD).

### Instruksi

**(a)** Hitung matriks rotasi optimal $\mathbf{R}$, lalu selaraskan vektor teks dengan $\mathbf{R}$ tersebut.

**(b)** Hitung ulang matriks kesamaan, *InfoNCE*, dan *Recall@1*.

**(c)** Sajikan perbandingan sebelum dan sesudah dalam satu tabel.

**(d)** Jawab dalam 4–6 kalimat: apa yang sesungguhnya berubah pada langkah ini, dan mengapa hal itu cukup untuk memperbaiki kinerja pencarian?

```{.python .numberLines startFrom=1}
M = teks.T @ gambar
U, s, Vt = np.linalg.svd(M)
R = U @ Vt
teks_selaras = teks @ R

S1 = matriks_kesamaan(gambar, teks_selaras)
print("diagonal :", np.diag(S1))
print("rerata luar diagonal: %+.3f" % S1[~np.eye(N, dtype=bool)].mean())
print("InfoNCE  : %.4f" % infonce(S1))
print("Recall@1 : %d/%d" % (recall_at_1(S1), N))
```

\newpage

## Soal 3 — Pengaruh Suhu

Suhu (*temperature*) menentukan seberapa tajam model membedakan kandidat.

### Instruksi

**(a)** Hitung *InfoNCE* pada data yang sudah selaras untuk setidaknya tiga nilai suhu, misalnya `0,05`, `0,10`, dan `0,50`.

**(b)** Tampilkan hasilnya dalam bentuk tabel.

**(c)** Jawab dalam 3–5 kalimat: mengapa suhu yang sangat kecil menurunkan *loss*, tetapi tetap tidak dianjurkan dipakai pada pelatihan?

```{.python .numberLines startFrom=1}
for t in (0.05, 0.10, 0.50):
    print("tau=%.2f: InfoNCE=%.4f" % (t, infonce(S1, tau=t)))
```

## Soal 4 — Retrieval dan Recall@K

Pada tugas nyata, yang diukur bukan *loss* melainkan peringkat hasil pencarian.

### Instruksi

**(a)** Untuk setiap kueri teks, tentukan peringkat gambar yang benar.

**(b)** Laporkan *Recall@1* dan jelaskan mengapa pada katalog besar angka ini dapat terlihat rendah meskipun modelnya baik.

**(c)** Sebutkan satu cara agar *Recall@K* tinggi tanpa melatih ulang model.

```{.python .numberLines startFrom=1}
for i in range(N):
    rank = np.argsort(-S1[i])
    pos = int(np.where(rank == i)[0][0]) + 1
    print("  teks %d: peringkat %d" % (i, pos))
```

\newpage

## Soal 5 — Analisis Kritis

Jawab pertanyaan berikut dalam bentuk paragraf singkat (masing-masing 5–8 kalimat).

### (a) Perbandingan Pola Arsitektur

Buat tabel yang membandingkan tiga pola arsitektur multimodal (*dual-stream*, *multi-encoder*, dan *dual-encoder*) pada tiga aspek: tempat modalitas bertemu, kedalaman interaksi yang mungkin dipelajari, dan kesesuaiannya untuk pencarian berskala besar. Pilih satu pola untuk pernyataan masalah di atas dan pertanggungjawabkan pilihan Anda secara eksplisit.

### (b) Uji Kegagalan Komposisional

Uji apakah model pra-latih benar-benar menangkap **relasi** antar objek atau hanya kehadiran objek. Gunakan satu gambar pilihan Anda dan empat kandidat teks yang memakai kata yang sama tetapi berbeda relasi atau negasi. Catat probabilitas setiap kandidat, lalu jawab: apakah kegagalan yang Anda amati disebabkan oleh kurangnya data, kurangnya kapasitas, atau tujuan pelatihannya? Jelaskan dasar penilaian Anda.

```{.python .numberLines startFrom=1}
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

NAMA = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(NAMA)
proc = CLIPProcessor.from_pretrained(NAMA)
model.eval()

gambar = Image.open("gambar_pilihan_anda.jpg").convert("RGB")
kandidat = [
    "sebuah sepeda di atas mobil",      # relasi benar
    "sebuah mobil di atas sepeda",      # relasi dibalik
    "sebuah sepeda dan sebuah mobil",   # tanpa relasi
    "sebuah mobil tanpa sepeda",        # negasi
]

inputs = proc(text=kandidat, images=gambar, return_tensors="pt", padding=True)
with torch.no_grad():
    out = model(**inputs)

probs = out.logits_per_image.softmax(dim=1)[0]
urut = torch.argsort(probs, descending=True)
for i in urut:
    print("%-32s %.4f" % (kandidat[int(i)], float(probs[int(i)])))
```

### (c) Kaitan dengan Teori

Hubungkan hasil Anda dengan dua gagasan dari perkuliahan: (i) pilar *alignment* beserta mekanisme *cross-attention* pada Pertemuan 7, dan (ii) pernyataan bahwa penambahan modalitas **tidak otomatis** meningkatkan kinerja. Apakah kasus pencarian produk pada tugas ini termasuk kasus yang menguntungkan bagi *dual-encoder*? Sebutkan satu syarat yang membuat pilihan Anda gagal.

## Format Pengumpulan

Seluruh artefak tugas dikemas ke dalam **satu berkas arsip** dengan format penamaan `mgg09_tugas_nim.zip`, dengan `nim` diganti oleh Nomor Induk Mahasiswa (NIM) masing-masing tanpa spasi.

| Item | Format |
|---|---|
| Notebook | `mgg09_tugas_NIM.ipynb` — wajib telah dijalankan sehingga seluruh output sel tersimpan |
| Skrip | `mgg09_tugas_NIM.py` — bila penyelesaian berbentuk skrip Python |
| Analisis tertulis | `mgg09_tugas_NIM.pdf` — bila analisis ditulis dalam dokumen terpisah |
| Catatan kandidat | `mgg09_tugas_xx.txt` — probabilitas kandidat teks pada Soal 5b; `xx` nomor urut |
| Visualisasi | `mgg09_tugas_xx.jpg` — plot atau gambar pendukung; `xx` nomor urut |

Semua berkas memakai awalan `mgg09_tugas_NIM` yang sama dan berada tepat di dalam satu arsip `.zip` tanpa struktur folder bertingkat yang tidak perlu.

## Kriteria Penilaian

| Aspek | Bobot | Deskripsi |
|---|:---:|---|
| **Kebenaran teknis** | 35% | Kode berjalan tanpa error, *InfoNCE* dan *Recall@K* dihitung dengan tepat, bobot pra-latih tidak diubah |
| **Kedalaman analisis** | 30% | Penjelasan menghubungkan hasil dengan konsep *alignment*, suhu, dan pola arsitektur multimodal |
| **Eksperimen** | 20% | Pengukuran baseline, perbandingan sebelum/sesudah penyelarasan, dan uji kegagalan komposisional |
| **Kualitas presentasi** | 15% | Tabel hasil rapi, laporan terstruktur, dan interpretasi jelas |

## Referensi

1. Radford, A., et al. (2021). *Learning Transferable Visual Models From Natural Language Supervision*. ICML. — sumber CLIP dan tujuan kontrastif *InfoNCE*.
2. Schönemann, P. H. (1966). *A Generalized Solution of the Orthogonal Procrustes Problem*. Psychometrika. — dasar penyelarasan bentuk tertutup pada Soal 2.
3. Vaswani, A., et al. (2017). *Attention Is All You Need*. NeurIPS. — arsitektur dasar yang mendasari sesi ini.
4. Liang, P., Zadeh, A., & Morency, L.-P. (2023). *Tutorial on Multimodal Machine Learning*. ICML. — bagian *multimodal transformers* dan *pre-training*.

---

**Estimasi waktu pengerjaan:** 3–4 jam

**Soal 1–4:** Wajib dikerjakan oleh semua mahasiswa. Soal 1 wajib dilaporkan lebih dulu sebagai baseline

**Soal 5:** Wajib dikerjakan; bagian (b) memerlukan kode, bagian (a) dan (c) bersifat analitis

**Bobot pra-latih tidak boleh diubah:** mengubah atau melatih ulang model akan dinilai sebagai kesalahan prosedur
