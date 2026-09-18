---
title: "Tugas Individu 03"
subtitle: "Representasi Gambar — Ekstraksi Fitur Visual dengan ResNet"
author: "IF25-40304 · Pembelajaran Mesin Multimodal · Institut Teknologi Sumatera"
date: "Pertemuan 03"
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
  \fancyhead[R]{\small Tugas Individu 03}
  \fancyfoot[C]{\thepage}
---

\thispagestyle{empty}

# Tugas Individu 03: Representasi Gambar — Ekstraksi Fitur Visual dengan ResNet

**Mata Kuliah:** IF25-40304 — Pembelajaran Mesin Multimodal

**Topik:** Representasi Modalitas II: Gambar (Pertemuan 03)

**Bentuk:** Laporan singkat + kode Python (Jupyter Notebook / `.py`)

**Batas Waktu:** 1 minggu setelah pertemuan 03

**Pengerjaan:** Individu

---

## Pendahuluan

Tugas ini melengkapi materi Pertemuan 03 tentang representasi gambar, CNN, ResNet, dan transfer learning. Anda akan melakukan eksperimen inferensi menggunakan model ResNet50 pra-latih untuk memverifikasi tiga gagasan utama:

1. Gambar memiliki struktur spasial dan tiga kanal warna RGB, bukan sekadar daftar angka independen.
2. Konvolusi dan pooling menyaring pola lokal (tepi, tekstur) dengan jumlah parameter yang jauh lebih sedikit daripada lapisan *fully connected*.
3. CNN membangun representasi hierarkis dari pola lokal menuju fitur visual yang lebih abstrak.
4. Backbone pra-latih dapat digunakan sebagai ekstraktor fitur visual tanpa melatih ulang model.

### Lingkungan yang Diperlukan

- Python 3.8+
- Paket wajib: `torch`, `torchvision`, `Pillow`, `matplotlib`, `scikit-learn`, `numpy` (Soal 2 memakai `numpy` untuk konvolusi manual)
- Dua atau lebih gambar dengan isi yang dapat dibandingkan secara visual
- Internet saat pertama kali mengunduh weights ResNet50

```bash
pip install torch torchvision pillow matplotlib scikit-learn
```

> **Batasan cakupan:** seluruh tugas menggunakan inferensi pada model ResNet50 pra-latih. Jangan melakukan `fit()`, `backward()`, atau pelatihan ulang classifier. Pada Soal 2 Anda **menghitung konvolusi secara manual** dan memverifikasinya dengan `torch.nn.functional.conv2d`; keduanya adalah operasi maju (*forward*), bukan pelatihan. Fokus tugas adalah mengamati dan menganalisis representasi visual.

\newpage

## Soal 1 — Gambar sebagai Tensor RGB

Gambar RGB dapat direpresentasikan sebagai tensor dengan bentuk $H \times W \times C$, dengan $H$ sebagai tinggi, $W$ sebagai lebar, dan $C=3$ sebagai kanal merah, hijau, dan biru.

### Instruksi

**(a)** Pilih dua gambar lokal dengan ukuran atau rasio aspek yang berbeda. Muat gambar menggunakan Pillow, lalu tampilkan:

- ukuran asli setiap gambar;
- mode warna;
- jumlah kanal;
- rasio aspek.

**(b)** Tampilkan kedua gambar menggunakan `matplotlib` dan jelaskan perbedaan visualnya secara singkat.

**(c)** Jawab dalam 3–5 kalimat:

- Mengapa gambar tidak cukup direpresentasikan sebagai daftar angka tanpa struktur spasial?
- Apa konsekuensi perbedaan ukuran dan rasio aspek sebelum gambar diproses CNN?
- Mengapa gambar RGB memiliki $C=3$?

### Contoh Kerangka Kode

```{.python .numberLines startFrom=1}
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

paths = [Path("data/image_a.jpg"), Path("data/image_b.jpg")]
images = [Image.open(path).convert("RGB") for path in paths]

for path, image in zip(paths, images):
    width, height = image.size
    print(path.name, image.size, image.mode)
    print("channels:", len(image.getbands()))
    print("aspect ratio:", round(width / height, 3))

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for axis, path, image in zip(axes, paths, images):
    axis.imshow(image)
    axis.set_title(path.name)
    axis.axis("off")
plt.tight_layout()
plt.show()
```

\newpage

## Soal 2 — Konvolusi 2D dan Pooling

Slide 8 menuliskan operasi konvolusi sebagai $y(i,j) = \sum_{u,v} x(i+u, j+v)\, k(u,v)$, sedangkan slide 9 menjelaskan *stride* dan *padding*. Keduanya sering dipahami sebagai rumus hafalan. Soal ini menuntutnya dihitung pada satu contoh kecil sehingga terlihat bahwa setiap nilai *feature map* hanyalah penjumlahan hasil kali piksel lokal dengan kernel.

Perhatikan tambalan (*patch*) abu-abu $6 \times 6$ berikut. Baris atas bernilai 0 (gelap) dan baris bawah bernilai 1 (terang), sehingga terdapat satu **tepi horizontal** di antara baris ketiga dan keempat.

```text
patch =
[[0 0 0 0 0 0]
 [0 0 0 0 0 0]
 [0 0 0 0 0 0]
 [1 1 1 1 1 1]
 [1 1 1 1 1 1]
 [1 1 1 1 1 1]]
```

Gunakan dua kernel Sobel $3 \times 3$:

$$k_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}, \qquad k_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}$$

### Instruksi

**(a)** Hitung **satu** nilai keluaran $y(1,0)$ secara manual: ambil jendela $3 \times 3$ dari `patch[1:4, 0:3]`, kalikan elemen demi elemen dengan $k_y$, lalu jumlahkan. Tuliskan langkah aritmetikanya, bukan hanya hasil akhirnya.

**(b)** Hitung seluruh *feature map* untuk $k_y$ dengan perulangan bersarang (`for` ganda), lalu bandingkan dengan hasil `torch.nn.functional.conv2d`. Tampilkan kedua matriks dan selisih maksimumnya.

**(c)** Untuk masukan $6 \times 6$ dan kernel $3 \times 3$, hitung ukuran keluaran dengan rumus

$$H_{out} = \left\lfloor \frac{H - K + 2P}{S} \right\rfloor + 1$$

untuk tiga konfigurasi: $(P{=}0, S{=}1)$, $(P{=}1, S{=}1)$, dan $(P{=}1, S{=}2)$. Verifikasi setiap nilai dengan memeriksa `.shape` hasil `conv2d`.

**(d)** Terapkan max pooling $2 \times 2$ pada *feature map* $k_y$. Laporkan bentuk sebelum dan sesudahnya, serta nilai yang bertahan.

**(e)** Jalankan langkah (b) dengan $k_x$ sebagai ganti $k_y$. Jelaskan mengapa hasilnya nol di seluruh posisi, padahal pada (b) tidak demikian. Kaitkan jawaban Anda dengan gagasan bahwa kernel **memilih** pola tertentu.

**(f)** Bandingkan jumlah parameter sebuah *fully connected layer* yang memetakan masukan $64 \times 64 \times 3$ ke 64 unit dengan sebuah lapisan konvolusi yang memakai 64 filter $3 \times 3$ (abaikan bias). Jelaskan mengapa *parameter sharing* membuat konvolusi lebih layak dipakai pada gambar.

### Contoh Kerangka Kode

```python
import numpy as np
import torch
import torch.nn.functional as F

patch = np.array([[0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1]], dtype=np.float32)

kernel_y = np.array([[-1, -2, -1],
                     [ 0,  0,  0],
                     [ 1,  2,  1]], dtype=np.float32)

# (a) satu nilai secara manual
window = patch[1:4, 0:3]
print(window)
print("y(1,0) =", (window * kernel_y).sum())

# (b) seluruh feature map + verifikasi
H, W = patch.shape
K = kernel_y.shape[0]
feature = np.zeros((H - K + 1, W - K + 1), dtype=np.float32)

for i in range(feature.shape[0]):
    for j in range(feature.shape[1]):
        feature[i, j] = (patch[i:i+K, j:j+K] * kernel_y).sum()

tensor = torch.from_numpy(patch)[None, None]
weight = torch.from_numpy(kernel_y)[None, None]
library = F.conv2d(tensor, weight)[0, 0].numpy()

print(feature)
print(library)
print("selisih maks:", np.abs(feature - library).max())
```

### Pemeriksaan Mandiri

Tiga nilai berikut hanya untuk memeriksa apakah kode Anda berjalan benar. **Ukuran keluaran pada (c) dan penjelasan pada (e) sengaja tidak dicantumkan** karena keduanya termasuk yang dinilai.

| Pemeriksaan | Nilai yang benar |
|---|---|
| Hasil (a) | $y(1,0) = 4$ |
| *Feature map* $k_y$ | bernilai $4$ pada dua baris tengah; nol pada baris teratas dan terbawah |
| Hasil (d) | $4 \times 4$ menjadi $2 \times 2$, seluruh nilainya $4$ |
| Selisih manual vs `conv2d` | $0.0$ |

Jika selisih maksimum pada (b) tidak nol, periksa urutan indeks jendela (`patch[i:i+K, j:j+K]`) dan pastikan kernel tidak dibalik secara tidak sengaja.

\newpage

## Soal 3 — ResNet50 sebagai Feature Extractor

ResNet50 yang telah dilatih pada ImageNet dapat digunakan sebagai backbone untuk menghasilkan embedding visual. Classifier terakhir dilepas sehingga keluaran model berupa vektor fitur berdimensi 2048.

### Instruksi

**(a)** Muat weights ResNet50 dan ubah classifier terakhir menjadi `torch.nn.Identity()`.

**(b)** Gunakan transformasi resmi dari weights model. Jalankan inferensi pada dua gambar yang dipilih pada Soal 1.

**(c)** Tampilkan bentuk keluaran setiap gambar. Pastikan hasilnya berupa vektor `(2048,)` setelah dimensi batch dihilangkan.

```{.python .numberLines startFrom=1}
import torch
from torchvision.models import ResNet50_Weights, resnet50

weights = ResNet50_Weights.DEFAULT
backbone = resnet50(weights=weights)
backbone.fc = torch.nn.Identity()
backbone.eval()

preprocess = weights.transforms()

features = []
with torch.inference_mode():
    for image in images:
        tensor = preprocess(image).unsqueeze(0)
        feature = backbone(tensor).squeeze(0)
        features.append(feature)
        print("feature shape:", tuple(feature.shape))
```

**(d)** Jawab dalam 3–5 kalimat:

- Mengapa classifier terakhir dilepas?
- Mengapa mode `eval()` dan `torch.inference_mode()` sesuai untuk tugas ini?
- Mengapa keluaran backbone berupa vektor, bukan lagi matriks piksel?

\newpage

## Soal 4 — Kemiripan Kosinus Antar-Gambar

Dua gambar dapat dibandingkan melalui arah vektor embedding. Kemiripan kosinus dihitung dengan:

$$
\operatorname{sim}(\mathbf{a}, \mathbf{b}) =
\frac{\mathbf{a} \cdot \mathbf{b}}
{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}
$$

### Instruksi

**(a)** Hitung kemiripan kosinus antara dua embedding.

```{.python .numberLines startFrom=1}
import torch.nn.functional as F

similarity = F.cosine_similarity(
    features[0].unsqueeze(0),
    features[1].unsqueeze(0),
).item()

print(f"cosine similarity: {similarity:.4f}")
```

**(b)** Ulangi eksperimen dengan pasangan gambar kedua. Pilih satu pasangan yang secara visual mirip dan satu pasangan yang berbeda.

**(c)** Sajikan hasil dalam tabel:

| Pasangan | Deskripsi visual | Cosine similarity | Interpretasi |
|---|---|---:|---|
| A | ... | ... | ... |
| B | ... | ... | ... |

**(d)** Analisis dalam 3–5 kalimat:

- Apakah pasangan yang lebih mirip secara visual selalu memiliki nilai cosine lebih tinggi?
- Informasi visual apa yang kemungkinan besar memengaruhi nilai tersebut?
- Mengapa nilai cosine bukan probabilitas bahwa dua gambar berasal dari kelas yang sama?

\newpage

## Soal 5 — Visualisasi Embedding Gambar

Embedding 2048 dimensi sulit diamati secara langsung. Gunakan PCA untuk memproyeksikan beberapa embedding ke ruang dua dimensi.

### Instruksi

**(a)** Siapkan minimal **6 gambar** yang terbagi ke dalam **2 atau 3 kelompok visual**. Contoh kelompok: hewan, kendaraan, makanan, atau pemandangan.

**(b)** Ekstrak embedding setiap gambar menggunakan pipeline pada Soal 3.

**(c)** Reduksi embedding ke dua dimensi menggunakan PCA dan buat scatter plot berlabel.

```{.python .numberLines startFrom=1}
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# features: list tensor berdimensi 2048
matrix = torch.stack(features).numpy()
coordinates = PCA(n_components=2).fit_transform(matrix)

plt.figure(figsize=(8, 6))
for i, (x, y) in enumerate(coordinates):
    plt.scatter(x, y, s=100)
    plt.annotate(labels[i], (x, y), xytext=(7, 4),
                 textcoords="offset points", fontweight="bold")
plt.title("Proyeksi 2D Embedding Gambar")
plt.xlabel("Komponen Utama 1")
plt.ylabel("Komponen Utama 2")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("visualisasi_embedding_gambar.png", dpi=150)
plt.show()
```

**(d)** Analisis dalam 3–5 kalimat:

- Apakah gambar dalam kelompok yang sama cenderung berdekatan?
- Gambar mana yang paling jauh dari kelompoknya?
- Mengapa proyeksi PCA dua dimensi tidak selalu mempertahankan seluruh informasi embedding asli?

\newpage

## Soal 6 — Analisis Kritis Representasi Visual

Jawab pertanyaan berikut dalam bentuk paragraf singkat (masing-masing 5–8 kalimat):

**(a) Backbone dan Tugas Baru**

ResNet50 dilatih untuk klasifikasi ImageNet, tetapi pada tugas ini digunakan sebagai ekstraktor fitur. Jelaskan mengapa fitur dari model pra-latih dapat digunakan untuk tugas yang berbeda, dan kapan pendekatan ini mungkin kurang sesuai.

**(b) Struktur Lokal dan Abstraksi**

Hubungkan proses `convolution → pooling → feature map → embedding` dengan hierarki representasi dari piksel, tepi, tekstur, hingga bagian objek.

**(c) Keterbatasan Cosine Similarity**

Jelaskan mengapa dua gambar dapat memiliki nilai cosine yang tinggi meskipun manusia menilai keduanya tidak identik. Pertimbangkan pengaruh dataset ImageNet, preprocessing, latar belakang, dan bias backbone.

## Format Pengumpulan

| Item | Format |
|---|---|
| Kode | Jupyter Notebook (`.ipynb`) atau Python script (`.py`) |
| Analisis tertulis | Markdown cell dalam notebook atau dokumen PDF terpisah |
| Visualisasi | Plot tersimpan atau di-embed dalam notebook |

## Kriteria Penilaian

| Aspek | Bobot | Deskripsi |
|---|:---:|---|
| **Kebenaran teknis** | 35% | Kode berjalan tanpa error dan pipeline inferensi digunakan dengan tepat |
| **Kedalaman analisis** | 30% | Penjelasan menghubungkan output dengan konsep CNN dan representasi visual |
| **Eksperimen** | 20% | Pemilihan pasangan/kelompok gambar dan interpretasi hasil |
| **Kualitas presentasi** | 15% | Laporan rapi, terstruktur, dan visualisasi informatif |

## Referensi

1. He, K., Zhang, X., Ren, S., & Sun, J. (2016). *Deep Residual Learning for Image Recognition*. CVPR. https://doi.org/10.1109/CVPR.2016.90
2. PyTorch Contributors. *ResNet-50 — Torchvision documentation*. https://pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html
3. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*, Bab 9: Convolutional Networks. MIT Press.

---

**Estimasi waktu pengerjaan:** 2–3 jam

**Soal 1–5:** Wajib dikerjakan oleh semua mahasiswa

**Soal 6:** Wajib dikerjakan sebagai analisis konseptual tanpa pelatihan model
