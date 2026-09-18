---
title: "Tugas Individu 04"
subtitle: "Representasi Audio & Video — Dari Gelombang Suara ke Pemodelan Temporal"
author: "IF25-40304 · Pembelajaran Mesin Multimodal · Institut Teknologi Sumatera"
date: "Pertemuan 04"
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
  \fancyhead[R]{\small Tugas Individu 04}
  \fancyfoot[C]{\thepage}
---

\thispagestyle{empty}

# Tugas Individu 04: Representasi Audio & Video — Dari Gelombang Suara ke Pemodelan Temporal

**Mata Kuliah:** IF25-40304 — Pembelajaran Mesin Multimodal

**Topik:** Representasi Modalitas III: Audio & Video (Pertemuan 04)

**Bentuk:** Laporan singkat + kode Python (Jupyter Notebook / `.py`)

**Batas Waktu:** 1 minggu setelah pertemuan 04

**Pengerjaan:** Individu

---

## Pendahuluan

Tugas ini melengkapi materi Pertemuan 04 tentang representasi audio dan video. Anda akan melakukan eksperimen komputasi berbasis sinyal sintetis untuk memverifikasi tiga gagasan utama:

1. Audio adalah sinyal sekuensial dan temporal — representasi mentahnya berupa deretan sampel amplitudo terhadap waktu.
2. Transformasi STFT mengubah sinyal 1D menjadi spektrogram 2D (waktu $\times$ frekuensi) yang dapat diproses CNN.
3. Video adalah sekuens frame gambar — memproses tiap frame secara terpisah mengabaikan dimensi temporal (gerakan).

### Lingkungan yang Diperlukan

- Python 3.8+
- Paket wajib: `numpy`, `librosa`, `matplotlib`
- Data: sinyal sintetis yang dibangkitkan secara programatik (nada murni dan campurannya)
- Video: sekuens frame sintetis (misal objek bergerak sederhana) yang dibangkitkan dengan NumPy

```bash
pip install numpy librosa matplotlib
```

> **Batasan cakupan:** seluruh tugas menggunakan sinyal audio dan video **sintetis**. Tujuannya mengamati rantai representasi dari prinsip pertama — dari raw waveform ke spektrogram/MFCC, dan dari frame statis ke pemodelan temporal — tanpa ketergantungan pada dataset eksternal. Gunakan `librosa` untuk STFT/spektrogram/MFCC; jangan menulis ulang implementasi Fourier secara manual.

\newpage

## Soal 1 — Raw Waveform dan Teorema Sampling

Sinyal audio mentah adalah deretan sampel amplitudo terhadap waktu. Teorema Nyquist–Shannon mensyaratkan laju pencuplikan memenuhi $f_s > 2\,f_{\max}$ agar sinyal asli dapat direkonstruksi tanpa *aliasing*.

### Instruksi

**(a)** Bangkitkan nada murni 440 Hz (nada A4) berdurasi 2 detik dengan *sampling rate* $f_s = 22050$ Hz. Plot 500 sampel pertamanya.

**(b)** Campurkan nada 440 Hz dan 880 Hz, lalu turunkan *sampling rate* menjadi 1000 Hz untuk mensimulasikan *aliasing*. Plot hasilnya.

**(c)** Jawab dalam 3–5 kalimat:

- Mengapa sinyal berdurasi 2 detik pada $f_s = 22050$ Hz menghasilkan 44100 sampel?
- Mengapa 880 Hz yang dicuplik pada 1000 Hz tidak lagi menyerupai gelombang aslinya?
- Apa konsekuensi *aliasing* terhadap model pembelajaran mesin?

### Contoh Kerangka Kode

```{.python .numberLines startFrom=1}
import numpy as np
import matplotlib.pyplot as plt

SR, DURASI = 22050, 2.0
n_sampel = int(SR * DURASI)
t = np.linspace(0, DURASI, n_sampel, endpoint=False)

freq = 440.0
sinyal = 0.5 * np.sin(2 * np.pi * freq * t)

plt.figure(figsize=(10, 3))
plt.plot(t[:500], sinyal[:500], color="#1e66f5")
plt.xlabel("Waktu (detik)")
plt.ylabel("Amplitudo")
plt.title("Gelombang Suara 440 Hz")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
```

\newpage

## Soal 2 — Spektrogram (STFT)

STFT mengiris sinyal menjadi jendela waktu dan menghitung komponen frekuensi tiap jendela, menghasilkan peta 2D waktu $\times$ frekuensi yang disebut spektrogram.

### Instruksi

**(a)** Hitung STFT dari sinyal campuran 440 Hz + 880 Hz menggunakan `librosa.stft` dengan `n_fft=2048` dan `hop_length=512`. Tampilkan spektrogram dalam skala dB.

**(b)** Ulangi dengan dua ukuran jendela berbeda (`n_fft=4096` dan `n_fft=512`) dan bandingkan ketajaman frekuensi terhadap ketajaman waktu.

```{.python .numberLines startFrom=1}
import librosa
import librosa.display

D = librosa.stft(sinyal_campuran, n_fft=2048, hop_length=512)
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

plt.figure(figsize=(10, 5))
librosa.display.specshow(
    S_db, sr=SR, hop_length=512,
    x_axis="time", y_axis="hz"
)
plt.colorbar(format="%+2.0f dB")
plt.title("Spektrogram Campuran 440 Hz + 880 Hz")
plt.tight_layout()
plt.show()
```

**(c)** Jawab dalam 3–5 kalimat:

- Bagaimana spektrogram merepresentasikan dua nada yang bercampur?
- Apa *trade-off* antara jendela panjang dan jendela pendek?
- Mengapa spektrogram 2D lebih cocok diproses CNN dibanding raw waveform 1D?

\newpage

## Soal 3 — MFCC

MFCC memadatkan spektrum Mel menjadi vektor koefisien kecil yang menangkap *timbre*. Alurnya: framing $\to$ STFT $\to$ filterbank Mel $\to$ log $\to$ DCT.

### Instruksi

**(a)** Ekstrak 13 koefisien MFCC dari sinyal campuran menggunakan `librosa.feature.mfcc`. Tampilkan bentuk (shape) hasil dan visualisasikan.

```{.python .numberLines startFrom=1}
mfcc = librosa.feature.mfcc(y=sinyal_campuran, sr=SR, n_mfcc=13)

print("bentuk MFCC:", mfcc.shape)

plt.figure(figsize=(10, 5))
librosa.display.specshow(mfcc, sr=SR, hop_length=512, x_axis="time")
plt.colorbar(label="Koefisien")
plt.title("MFCC Campuran 440 Hz + 880 Hz")
plt.tight_layout()
plt.show()
```

**(b)** Jawab dalam 3–5 kalimat:

- Apa arti dimensi pada bentuk `(13, N)` hasil MFCC?
- Mengapa MFCC lebih ringkas daripada spektrogram mentah?
- Mengapa filterbank Mel lebih sesuai dengan persepsi pendengaran manusia?

\newpage

## Soal 4 — Video sebagai Sekuens Frame

Pendekatan paling sederhana adalah memperlakukan video sebagai urutan frame gambar. Namun, pendekatan *frame-by-frame* mengabaikan informasi temporal (gerakan, urutan, perubahan antar frame).

### Instruksi

**(a)** Bangkitkan "video" sintetis berupa kotak $8\times8$ yang bergerak horizontal melintasi 24 frame berukuran $48\times64$.

```{.python .numberLines startFrom=1}
frame_count = 24
h, w = 48, 64
frames = []

for i in range(frame_count):
    frame = np.zeros((h, w), dtype=np.uint8)
    posisi_x = int(i * (w - 8) / (frame_count - 1))
    frame[20:28, posisi_x:posisi_x + 8] = 255
    frames.append(frame)

fig, axes = plt.subplots(1, 4, figsize=(10, 2.5))
for ax, idx in zip(axes, [0, 8, 16, 23]):
    ax.imshow(frames[idx], cmap="gray")
    ax.set_title(f"t = {idx}")
    ax.axis("off")
plt.tight_layout()
plt.show()
```

**(b)** Jawab dalam 3–5 kalimat:

- Informasi apa yang hilang jika setiap frame diproses CNN 2D secara independen?
- Bagaimana arah dan kecepatan gerakan kotak bisa tertangkap oleh pemodelan temporal?
- Mengapa video bukan sekadar "tumpukan gambar"?

\newpage

## Soal 5 — Analisis Kritis Pilihan Arsitektur

Jawab pertanyaan berikut dalam bentuk paragraf singkat (masing-masing 5–8 kalimat):

**(a) 3D CNN vs CNN + RNN/LSTM**

Jelaskan perbedaan mendasar antara 3D CNN dan kombinasi 2D CNN + RNN/LSTM untuk pemodelan video. Kaitkan dengan konsep konvolusi 3D $y(i,j,t)=\sum_{u,v,w}x(i+u,j+v,t+w)\,k(u,v,w)$ dan kapan masing-masing pendekatan lebih unggul.

**(b) Transformer untuk Audio dan Video**

Jelaskan bagaimana mekanisme *self-attention* menangkap ketergantungan jarak jauh pada audio dan video tanpa pemrosesan sekuensial kata-per-kata. Sebutkan satu contoh penerapan untuk audio (misal ASR/TTS) dan satu untuk video (misal Video Transformer).

**(c) Tantangan Pemrosesan Video**

Pilih dua dari enam tantangan video yang dibahas pada slide (dimensi tinggi, redundansi temporal, variasi gerakan, ketergantungan jangka panjang, kualitas data, anotasi data) dan jelaskan bagaimana masing-masing memengaruhi pilihan arsitektur atau strategi pelatihan.

## Format Pengumpulan

Seluruh artefak tugas dikemas ke dalam **satu berkas arsip** dengan format penamaan `mgg04_tugas_nim.zip`, dengan `nim` diganti oleh Nomor Induk Mahasiswa (NIM) masing-masing tanpa spasi.

| Item | Format |
|---|---|
| Notebook | `mgg04_tugas_NIM.ipynb` — wajib telah dijalankan sehingga seluruh output sel tersimpan |
| Skrip | `mgg04_tugas_NIM.py` — bila penyelesaian berbentuk skrip Python |
| Analisis tertulis | `mgg04_tugas_NIM.pdf` — bila analisis ditulis dalam dokumen terpisah |
| Visualisasi | `mgg04_tugas_xx.jpg` — plot atau gambar pendukung; `xx` nomor urut (mis. `01`, `02`) |

Semua berkas memakai awalan `mgg04_tugas_NIM` yang sama dan berada tepat di dalam satu arsip `.zip` tanpa struktur folder bertingkat yang tidak perlu.

## Kriteria Penilaian

| Aspek | Bobot | Deskripsi |
|---|:---:|---|
| **Kebenaran teknis** | 35% | Kode berjalan tanpa error dan pipeline representasi digunakan dengan tepat |
| **Kedalaman analisis** | 30% | Penjelasan menghubungkan output dengan konsep sampling, STFT, MFCC, dan pemodelan temporal |
| **Eksperimen** | 20% | Pengamatan aliasing, *trade-off* jendela STFT, dan analisis frame video |
| **Kualitas presentasi** | 15% | Laporan rapi, terstruktur, dan visualisasi informatif |

## Referensi

1. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*, Bab 10: Sequence Modeling. MIT Press.
2. Tran, D., Bourdev, L., Fergus, R., Torresani, L., & Paluri, M. (2015). *Learning Spatiotemporal Features with 3D Convolutional Networks*. ICCV. https://doi.org/10.1109/ICCV.2015.510
3. McFee, B., et al. *librosa: Audio and Music Signal Analysis in Python*. https://librosa.org
4. Jurafsky, D., & Martin, J. H. (terbaru). *Speech and Language Processing* — bab pengenalan ucapan.

---

**Estimasi waktu pengerjaan:** 2–3 jam

**Soal 1–4:** Wajib dikerjakan oleh semua mahasiswa

**Soal 5:** Wajib dikerjakan sebagai analisis konseptual tanpa pelatihan model
