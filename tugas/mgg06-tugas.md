---
title: "Tugas Individu 06"
subtitle: "Strategi Fusi Multimodal — Early, Late, dan Intermediate Fusion"
author: "IF25-40304 · Pembelajaran Mesin Multimodal · Institut Teknologi Sumatera"
date: "Pertemuan 06"
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
  \fancyhead[R]{\small Tugas Individu 06}
  \fancyfoot[C]{\thepage}
---

\thispagestyle{empty}

# Tugas Individu 06: Strategi Fusi Multimodal — Early, Late, dan Intermediate Fusion

**Mata Kuliah:** IF25-40304 — Pembelajaran Mesin Multimodal

**Topik:** Strategi Fusi Multimodal II: Intermediate & Hybrid Fusion (Pertemuan 06)

**Bentuk:** Laporan singkat + kode Python (Jupyter Notebook / `.py`)

**Batas Waktu:** 1 minggu setelah pertemuan 06

**Pengerjaan:** Individu

---

## Pendahuluan

Tugas ini melengkapi materi Pertemuan 05 dan 06 tentang strategi fusi multimodal. Anda akan menguji secara empiris tiga strategi fusi pada data sintetis yang dirancang khusus, lalu memilih dan mempertanggungjawabkan salah satunya. Tiga gagasan utama yang diverifikasi:

1. Satu modalitas saja tidak cukup — pengukuran *baseline* unimodal membuktikannya.
2. Titik penggabungan menentukan seberapa banyak interaksi antar modalitas yang dapat dipelajari.
3. Penambahan modalitas **tidak otomatis** meningkatkan kinerja; ketangguhan terhadap modalitas hilang juga harus diuji.

### Lingkungan yang Diperlukan

- Python 3.8+
- Paket wajib: `numpy`, `torch`, `scikit-learn`, `matplotlib`
- Data: dibangkitkan sendiri (sintetis) — tidak ada unduhan dataset
- Perangkat: CPU sudah memadai; GPU tidak diperlukan

```bash
pip install numpy torch scikit-learn matplotlib
```

> **Batasan cakupan:** tugas ini memakai data multimodal **sintetis** yang dirancang agar setiap modalitas hanya membawa **separuh** informasi. Akibatnya, satu modalitas saja tidak pernah melampaui akurasi kebetulan, sedangkan penggabungan yang tepat dapat mencapainya. Konstruksi ini membuat perbedaan Early, Late, dan Intermediate Fusion terlihat jelas, tanpa memerlukan dataset eksternal.

> **Encoder dibekukan.** Seluruh encoder modalitas sudah disediakan dan **tidak boleh dilatih**. Fokus tugas adalah lapisan fusi. Gunakan `torch` untuk model dan `scikit-learn` untuk pembagian data serta metrik.

### Ekspektasi Hasil

Dengan encoder `tanh` yang beku, hasil yang wajar adalah: kedua model unimodal sekitar **50%**, *Early Fusion* di atas **95%**, *Intermediate Fusion* sedikit di bawahnya, dan *Late Fusion* sekitar **85–90%**.

Perhatikan bahwa urutan ini berlaku untuk label yang bersifat **aditif** (seperti pada tugas ini). Untuk label yang menuntut **interaksi** antar modalitas (misalnya paritas/XOR), *Late Fusion* akan jatuh ke sekitar 50% sementara *Early* dan *Intermediate* tetap tinggi — inilah inti Soal 5. Bila hasil Anda menyimpang jauh (misalnya Early di bawah 80%), periksa hal berikut sebelum menyimpulkan:

- encoder memakai `ReLU` sehingga dimensi informatif mati (gunakan `Tanh`);
- label salah digabung;
- encoder tanpa sengaja ikut terlatih.

\newpage

## Pernyataan Masalah

Sebuah sistem diminta memprediksi **empat kelas emosi** dari dua modalitas: fitur visual (wajah) dan fitur audio (suara). Setiap modalitas hanya membawa satu dari dua faktor laten yang menentukan kelas, sehingga:

1. Model unimodal visual paling tinggi mencapai akurasi sekitar 50% — ia tahu separuh jawaban.
2. Model unimodal audio juga paling tinggi sekitar 50%.
3. Hanya penggabungan yang tepat dapat melampaui 95%.

Anda akan menguji ketiga strategi fusi pada kondisi ini, kemudian memilih yang paling tepat beserta alasannya.

## Soal 1 — Data Sintetis dan Baseline Unimodal

Sebelum menggabungkan apa pun, kita harus tahu seberapa jauh satu modalitas saja mampu menjangkau. Inilah *baseline* yang akan dibandingkan sepanjang tugas.

### Instruksi

**(a)** Bangkitkan data sintetis dengan dua faktor laten biner (valensi dari wajah, gairah dari suara). Label adalah gabungan keduanya sehingga menghasilkan empat kelas.

**(b)** Tampilkan distribusi kelas pada data. Pastikan keempat kelas berimbang.

**(c)** Latih dua model unimodal terpisah: satu hanya menerima fitur visual, satu hanya menerima fitur audio. Laporkan akurasi masing-masing di data uji.

**(d)** Jawab dalam 3–5 kalimat: mengapa akurasi kedua model unimodal berhenti di sekitar 50% dan tidak dapat melampauinya?

### Contoh Kerangka Kode

```{.python .numberLines startFrom=1}
import numpy as np
import torch
import torch.nn as nn

SEED, N, DIM = 42, 4000, 16
rng = np.random.default_rng(SEED)

def buat_data(n=N):
    """Dua faktor laten: visual (valensi) dan audio (gairah)."""
    z_visual = rng.integers(0, 2, size=n)   # separuh jawaban
    z_audio  = rng.integers(0, 2, size=n)   # separuh jawaban

    visual = rng.normal(0, 1.0, size=(n, DIM)).astype(np.float32)
    audio  = rng.normal(0, 1.0, size=(n, DIM)).astype(np.float32)

    # Dimensi 0 menandai faktor laten; sisanya derau tak informatif
    visual[:, 0] = z_visual * 2.0 - 1.0
    audio[:, 0]  = z_audio  * 2.0 - 1.0

    label = z_visual * 2 + z_audio          # 4 kelas gabungan
    return visual, audio, label

visual, audio, label = buat_data()
print("visual:", visual.shape, "| audio:", audio.shape)
print("distribusi kelas:", np.bincount(label))

def buat_encoder(fan_in=DIM, fan_out=32, seed=0):
    """Encoder BEKU dengan aktivasi tanh.

    Catatan: gunakan tanh, bukan ReLU. ReLU dapat mematikan
    dimensi yang membawa faktor laten, sehingga informasi hilang
    sebelum sempat digabungkan.
    """
    g = torch.Generator().manual_seed(seed)
    enc = nn.Sequential(
        nn.Linear(fan_in, fan_out), nn.Tanh(),
        nn.Linear(fan_out, fan_out), nn.Tanh(),
    )
    with torch.no_grad():                   # inisialisasi terkendali
        for p in enc.parameters():
            if p.dim() > 1:
                p.copy_(torch.randn(p.shape, generator=g) / p.shape[1] ** 0.5)
            else:
                p.zero_()
    enc.eval()
    for p in enc.parameters():
        p.requires_grad_(False)             # bekukan
    return enc

ENC_VISUAL = buat_encoder(seed=1)
ENC_AUDIO  = buat_encoder(seed=2)
print("parameter encoder visual:", sum(p.numel() for p in ENC_VISUAL.parameters()))
```

\newpage

## Soal 2 — Early Fusion

Early Fusion menggabungkan fitur tepat setelah encoder, lalu meneruskannya ke satu model bersama. Semua pembelajaran terjadi pada model gabungan tersebut.

### Instruksi

**(a)** Bentuk vektor gabungan $\mathbf{z} = [\,f_A(\mathbf{x}_A) ; f_B(\mathbf{x}_B)\,]$ dari keluaran kedua encoder beku.

**(b)** Latih satu model bersama (MLP) di atas $\mathbf{z}$, lalu laporkan akurasinya.

**(c)** Bandingkan dengan baseline unimodal Soal 1. Apakah fusi menambah nilai?

```{.python .numberLines startFrom=1}
class EarlyFusion(nn.Module):
    """Gabungkan fitur hasil encoder, lalu satu model bersama."""
    def __init__(self, dim_enc=32, n_kelas=4):
        super().__init__()
        self.head = nn.Sequential(
            nn.Linear(dim_enc * 2, 64), nn.Tanh(),
            nn.Linear(64, n_kelas),
        )

    def forward(self, x_visual, x_audio):
        with torch.no_grad():               # encoder beku
            f_a = ENC_VISUAL(x_visual)
            f_b = ENC_AUDIO(x_audio)
        z = torch.cat([f_a, f_b], dim=1)    # konkatenasi di lapisan awal
        return self.head(z)

model = EarlyFusion()
akurasi = latih_dan_uji(model, visual, audio, label)
print(f"Early Fusion accuracy: {akurasi:.4f}")
```

\newpage

## Soal 3 — Late Fusion

Late Fusion melatih model terpisah per modalitas, lalu menggabungkan *keputusan* masing-masing, bukan fiturnya.

### Instruksi

**(a)** Latih dua model unimodal terpisah di atas fitur encoder, masing-masing menghasilkan skor keyakinan untuk keempat kelas.

**(b)** Gabungkan kedua skor dengan rata-rata terbobot, lalu laporkan akurasinya.

**(c)** Jawab dalam 3–5 kalimat: mengapa strategi ini **masih dapat melampaui baseline unimodal** (~50%) meskipun encoder tidak boleh dilatih? Jelaskan peran rata-rata terbobot, lalu sebutkan satu kondisi di mana Late Fusion **akan gagal**.

```{.python .numberLines startFrom=1}
class LateFusion(nn.Module):
    """Dua kepala unimodal; keputusan digabung di akhir."""
    def __init__(self, dim_enc=32, n_kelas=4):
        super().__init__()
        self.head_a = nn.Sequential(nn.Linear(dim_enc, n_kelas))
        self.head_b = nn.Sequential(nn.Linear(dim_enc, n_kelas))
        self.w_a = nn.Parameter(torch.tensor(0.5))   # bobot modalitas
        self.w_b = nn.Parameter(torch.tensor(0.5))

    def forward(self, x_visual, x_audio):
        with torch.no_grad():
            f_a = ENC_VISUAL(x_visual)
            f_b = ENC_AUDIO(x_audio)
        p_a = torch.softmax(self.head_a(f_a), dim=1)
        p_b = torch.softmax(self.head_b(f_b), dim=1)
        return self.w_a * p_a + self.w_b * p_b      # fusi keputusan
```

\newpage

## Soal 4 — Intermediate Fusion

Intermediate Fusion menggabungkan representasi pada lapisan tengah: setelah tiap modalitas ditransformasi sedikit, tetapi sebelum keputusan akhir diambil.

### Instruksi

**(a)** Tambahkan transformasi kecil per modalitas (lapisan tengah), lalu gabungkan hasilnya. Anda boleh memakai konkatenasi atau *gating*.

**(b)** Latih dan laporkan akurasinya.

**(c)** Bandingkan dengan Early dan Late Fusion. Anda akan melihat Intermediate sedikit *di bawah* Early karena encoder bersifat beku: lapisan tengah tambahan hanya menambah transformasi sebelum informasi dari kedua modalitas bertemu. Tuliskan analisis Anda dalam 4–6 kalimat, dan sebutkan bagaimana hasilnya akan berbeda bila encoder boleh ikut dilatih (*fine-tuning*).

```{.python .numberLines startFrom=1}
class IntermediateFusion(nn.Module):
    """Fusi pada lapisan tengah, setelah transformasi per modalitas."""
    def __init__(self, dim_enc=32, dim_mid=32, n_kelas=4):
        super().__init__()
        self.mid_a = nn.Sequential(nn.Linear(dim_enc, dim_mid), nn.Tanh())
        self.mid_b = nn.Sequential(nn.Linear(dim_enc, dim_mid), nn.Tanh())
        self.gate = nn.Sequential(nn.Linear(dim_mid * 2, dim_mid), nn.Sigmoid())
        self.head = nn.Sequential(
            nn.Linear(dim_mid, 64), nn.ReLU(),
            nn.Linear(64, n_kelas),
        )

    def forward(self, x_visual, x_audio):
        with torch.no_grad():
            f_a = ENC_VISUAL(x_visual)
            f_b = ENC_AUDIO(x_audio)
        h_a, h_b = self.mid_a(f_a), self.mid_b(f_b)
        g = self.gate(torch.cat([h_a, h_b], dim=1))
        h = g * h_a + (1 - g) * h_b          # gerbang adaptif
        return self.head(h)
```

\newpage

## Soal 5 — Analisis Kritis dan Uji Modalitas Hilang

Jawab pertanyaan berikut dalam bentuk paragraf singkat (masing-masing 5–8 kalimat).

**(a) Perbandingan dan Pemilihan**

Sajikan akurasi ketiga strategi beserta baseline unimodal dalam satu tabel. Pilih satu strategi untuk sistem ini dan pertanggungjawabkan pilihan Anda berdasarkan akurasi, kompleksitas, dan kemudahan implementasi.

**(b) Uji Modalitas Hilang**

Ulangi pengujian dengan salah satu modalitas dinolkan (misalkan fitur audio diisi nol). Catat penurunan akurasi tiap strategi. Strategi mana yang paling tangguh, dan mengapa?

```{.python .numberLines startFrom=1}
# Nolkan satu modalitas -> ukur ketangguhan tiap strategi
audio_kosong = torch.zeros_like(torch.as_tensor(audio))

for nama, model in [("Early", m_early),
                    ("Late", m_late),
                    ("Intermediate", m_inter)]:
    akurasi_normal = uji(model, visual, audio, label)
    akurasi_hilang = uji(model, visual, audio_kosong, label)
    print(f"{nama:14s} normal={akurasi_normal:.3f} "
          f"audio-hilang={akurasi_hilang:.3f}")
```

**(c) Kaitan dengan Teori**

Hubungkan hasil Anda dengan dua gagasan dari perkuliahan: (i) masalah *redundansi*, *konflik*, dan *dominasi modalitas*; serta (ii) peringatan bahwa penambahan modalitas **tidak otomatis** meningkatkan kinerja. Apakah data sintetis pada tugas ini termasuk kasus yang menguntungkan bagi fusi? Jelaskan.

## Format Pengumpulan

Seluruh artefak tugas dikemas ke dalam **satu berkas arsip** dengan format penamaan `mgg06_tugas_nim.zip`, dengan `nim` diganti oleh Nomor Induk Mahasiswa (NIM) masing-masing tanpa spasi.

| Item | Format |
|---|---|
| Notebook | `mgg06_tugas_NIM.ipynb` — wajib telah dijalankan sehingga seluruh output sel tersimpan |
| Skrip | `mgg06_tugas_NIM.py` — bila penyelesaian berbentuk skrip Python |
| Analisis tertulis | `mgg06_tugas_NIM.pdf` — bila analisis ditulis dalam dokumen terpisah |
| Visualisasi | `mgg06_tugas_xx.jpg` — plot atau gambar pendukung; `xx` nomor urut (mis. `01`, `02`) |

Semua berkas memakai awalan `mgg06_tugas_NIM` yang sama dan berada tepat di dalam satu arsip `.zip` tanpa struktur folder bertingkat yang tidak perlu.

## Kriteria Penilaian

| Aspek | Bobot | Deskripsi |
|---|:---:|---|
| **Kebenaran teknis** | 35% | Encoder tetap beku, kode berjalan tanpa error, ketiga strategi diimplementasikan dengan tepat |
| **Kedalaman analisis** | 30% | Penjelasan menghubungkan hasil dengan konsep fusi, baseline unimodal, dan masalah klasik fusi |
| **Eksperimen** | 20% | Pengukuran baseline, perbandingan ketiga strategi, dan uji modalitas hilang |
| **Kualitas presentasi** | 15% | Tabel hasil rapi, laporan terstruktur, dan interpretasi jelas |

## Referensi

1. Baltrusaitis, T., Ahuja, C., & Morency, L.-P. (2018). *Multimodal Machine Learning: A Survey and Taxonomy*. IEEE TPAMI, 40(2), 421–443. — taksonomi early/intermediate/late fusion.
2. Arevalo, J., Solorio, T., Montes-y-Gomez, M., & Gonzalez, F. A. (2017). *Gated Multimodal Units for Information Fusion*. ICLR Workshop. — dasar mekanisme *gating*.
3. Liang, P., Zadeh, A., & Morency, L.-P. (2023). *Tutorial on Multimodal Machine Learning*. ICML. — bagian strategi fusi.
4. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*, Bab 6–7: Deep Feedforward Networks. MIT Press.

---

**Estimasi waktu pengerjaan:** 3–4 jam

**Soal 1–4:** Wajib dikerjakan oleh semua mahasiswa. Soal 1 wajib dilaporkan lebih dulu sebagai baseline

**Soal 5:** Wajib dikerjakan; bagian (b) memerlukan kode, bagian (a) dan (c) bersifat analitis

**Encoder beku:** pengurangan akurasi akibat melatih encoder akan dinilai sebagai kesalahan prosedur
