---
title: "Tugas Individu 02"
subtitle: "Representasi Teks — Dari One-Hot ke Contextual Embeddings"
author: "IF25-40304 · Pembelajaran Mesin Multimodal · Institut Teknologi Sumatera"
date: "Pertemuan 02"
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
  \fancyhead[R]{\small Tugas Individu 02}
  \fancyfoot[C]{\thepage}
---

\thispagestyle{empty}

# Tugas Individu 02: Representasi Teks — Dari One-Hot ke Contextual Embeddings

**Mata Kuliah:** IF25-40304 — Pembelajaran Mesin Multimodal

**Topik:** Representasi Modalitas I: Teks (Pertemuan 02)

**Bentuk:** Laporan singkat + kode Python (Jupyter Notebook / `.py`)

**Batas Waktu:** 1 minggu setelah pertemuan 02

**Pengerjaan:** Individu

---

## Pendahuluan

Tugas ini melengkapi materi Pertemuan 02 tentang representasi teks untuk *deep learning*. Anda akan melakukan eksperimen komputasi dan analisis tertulis untuk memverifikasi tiga klaim yang dibahas pada slide kuliah:

1. One-hot encoding bersifat **ortogonal** — tidak menangkap kemiripan makna antarkata.
2. Word embeddings bersifat **dense dan semantik** — kata bermakna mirip berdekatan dalam ruang vektor.
3. Embeddings statis memiliki limitasi terhadap **polisemi** — satu kata yang sama selalu mendapat vektor yang identik, terlepas dari konteks.

### Lingkungan yang Diperlukan

- Python 3.8+
- Paket wajib: `numpy`, `matplotlib`, `scikit-learn`, `gensim`
- Paket opsional (untuk Soal 5 bagian bonus): `transformers`, `torch`
- Model pra-latih: fastText bahasa Indonesia (`cc.id.300.vec.gz`, ±1 GB)

```bash
pip install numpy matplotlib scikit-learn gensim
```

> **Catatan:** Model fastText Indonesia (`cc.id.300.vec.gz`) berukuran ±1 GB. Unduh dari [fasttext.cc/docs/en/crawl-vectors.html](https://fasttext.cc/docs/en/crawl-vectors.html). Jika terkendala bandwidth, gunakan model GloVe 50-dimensi (`glove-wiki-gigaword-50`) via `gensim.downloader` sebagai alternatif — namun kosakata akan berbahasa Inggris.

\newpage

## Soal 1 — One-Hot Encoding & Keterbatasannya

Representasi teks paling sederhana adalah one-hot encoding, di mana setiap kata direpresentasikan sebagai vektor biner berdimensi = ukuran kosakata. Vektor ini bersifat *ortogonal*: setiap pasang kata berbeda menghasilkan kemiripan kosinus nol.

### Instruksi

**(a)** Diberikan kosakata berikut:

```{.python .numberLines startFrom=1}
vocab = ["presiden", "teknologi", "musik", "indonesia", "sains"]
```

Bangun fungsi `one_hot(kata, vocab)` yang mengembalikan vektor one-hot untuk sebuah kata. Tampilkan vektor untuk setiap kata dalam kosakata.

**(b)** Implementasikan fungsi `cosine_similarity(a, b)` secara manual:

$$\text{sim}(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \cdot \|\mathbf{b}\|}$$

Hitung dan tampilkan **matriks kemiripan kosinus (5×5)** antar semua pasang kata.

**(c)** Jawab secara tertulis (3–5 kalimat):

- Mengapa semua kemiripan antar kata berbeda bernilai **0.0**?
- Apa implikasinya terhadap model ML yang menerima input one-hot?
- Secara intuitif, pasangan kata mana yang *seharusnya* lebih mirip secara semantik? Mengapa one-hot tidak bisa menangkap ini?

### Contoh Kerangka Kode

```{.python .numberLines startFrom=1}
import numpy as np

def one_hot(kata, vocab, word_to_id):
    """Mengembalikan vektor one-hot untuk sebuah kata."""
    vektor = np.zeros(len(vocab))
    vektor[word_to_id[kata]] = 1
    return vektor

def cosine_similarity(a, b):
    """Kemiripan kosinus antara dua vektor: (a·b) / (||a|| ||b||)."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

\newpage

## Soal 2 — Word Embeddings: Vektor Dense & Kemiripan Semantik

Word embeddings menggantikan vektor one-hot yang panjang dan *sparse* dengan vektor *dense* berdimensi rendah yang merepresentasikan makna. Kata yang bermakna mirip akan saling berdekatan dalam ruang vektor.

### Instruksi

**(a)** Muat model pra-latih fastText bahasa Indonesia:

```{.python .numberLines startFrom=1}
from gensim.models import KeyedVectors

model = KeyedVectors.load_word2vec_format("cc.id.300.vec.gz", binary=False)
```

Untuk setiap kata berikut, tampilkan **5 kata paling mirip** beserta skor kemiripan kosinus:

- `"presiden"`, `"teknologi"`, `"musik"`

```{.python .numberLines startFrom=5}
for kata in ["presiden", "teknologi", "musik"]:
    print(f"\n5 kata paling mirip dengan '{kata}':")
    for kata_mirip, skor in model.most_similar(kata, topn=5):
        print(f"  {kata_mirip:<16} {skor:.4f}")
```

**(b)** Hitung dan tampilkan secara numerik:

```{.python .numberLines startFrom=11}
sim_presiden_indonesia = model.similarity("presiden", "indonesia")
sim_presiden_musik     = model.similarity("presiden", "musik")

print(f"sim(presiden, indonesia) = {sim_presiden_indonesia:.4f}")
print(f"sim(presiden, musik)     = {sim_presiden_musik:.4f}")
```

**(c)** Jawab dalam 3–5 kalimat:

- Apakah `"presiden"` lebih dekat ke `"indonesia"` atau ke `"musik"` di ruang embedding?
- Bandingkan secara eksplisit dengan hasil Soal 1: apa yang berubah ketika berpindah dari one-hot ke embeddings?
- Bagaimana embeddings mengatasi keterbatasan ortogonalitas?

\newpage

## Soal 3 — Analogi Vektor dalam Bahasa Indonesia

Sifat penting word embeddings adalah kemampuannya merepresentasikan *relasi semantik* melalui operasi aritmetika vektor. Operasi seperti `raja - pria + wanita = ratu` menunjukkan bahwa embeddings menangkap hubungan gender, geografi, dan peran secara geometris.

### Instruksi

Uji analogi vektor berikut menggunakan `model.most_similar(positive=..., negative=...)` pada fastText Indonesia:

| No | Rumus Analogi | Harapan |
|----|---|---|
| (a) | `raja - pria + wanita = ?` | ratu |
| (b) | `jepang - asia + eropa = ?` | jerman / perancis |
| (c) | `jakarta - indonesia + jepang = ?` | tokyo |

```{.python .numberLines startFrom=1}
# (a) raja - pria + wanita
hasil_a = model.most_similar(
    positive=["wanita", "raja"], negative=["pria"], topn=3
)
print("raja - pria + wanita =")
for kata, skor in hasil_a:
    print(f"  {kata:<16} {skor:.4f}")

# (b) jepang - asia + eropa
hasil_b = model.most_similar(
    positive=["eropa", "jepang"], negative=["asia"], topn=3
)
print("\njepang - asia + eropa =")
for kata, skor in hasil_b:
    print(f"  {kata:<16} {skor:.4f}")

# (c) jakarta - indonesia + jepang
hasil_c = model.most_similar(
    positive=["jepang", "jakarta"], negative=["indonesia"], topn=3
)
print("\njakarta - indonesia + jepang =")
for kata, skor in hasil_c:
    print(f"  {kata:<16} {skor:.4f}")
```

Tampilkan hasil **top-3** untuk setiap analogi, lalu jawab:

- Apakah ketiga analogi menghasilkan kata yang masuk akal?
- Jika hasilnya tidak sempurna, hipotesiskan mengapa (misal: bias korpus, frekuensi kata, ambiguitas).

**(d) Bonus:** Buat **satu analogi kreatif** Anda sendiri dalam bahasa Indonesia. Pilih kata-kata yang memiliki hubungan semantik jelas. Tampilkan hasil dan evaluasi keberhasilannya dalam 2–3 kalimat.

\newpage

## Soal 4 — Visualisasi Ruang Vektor Kata Indonesia

Untuk mengamati sifat "kata bermakna mirip berdekatan", vektor embedding diproyeksikan ke dua dimensi menggunakan PCA (*Principal Component Analysis*).

### Instruksi

Pilih **12 kata** dari fastText Indonesia yang terdiri dari **3–4 kelompok semantik**. Berikut contoh; Anda boleh memilih kelompok dan kata lain sesuai minat:

| Kelompok | Contoh Kata |
|---|---|
| Negara | `indonesia`, `jepang`, `brasil` |
| Hewan | `kucing`, `anjing`, `burung` |
| Profesi | `dokter`, `guru`, `insinyur` |
| Makanan | `nasi`, `rendang`, `sate` |

**(a)** Ekstrak vektor 300-dimensi untuk 12 kata tersebut dan reduksi ke 2D menggunakan PCA:

```{.python .numberLines startFrom=1}
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

kata_pilihan = [
    "indonesia", "jepang", "brasil",
    "kucing", "anjing", "burung",
    "dokter", "guru", "insinyur",
    "nasi", "rendang", "sate",
]

kelompok = {
    "indonesia": "Negara",   "jepang": "Negara",   "brasil": "Negara",
    "kucing": "Hewan",       "anjing": "Hewan",     "burung": "Hewan",
    "dokter": "Profesi",     "guru": "Profesi",     "insinyur": "Profesi",
    "nasi": "Makanan",       "rendang": "Makanan",  "sate": "Makanan",
}

warna = {
    "Negara": "#1e66f5", "Hewan": "#40a02b",
    "Profesi": "#8839ef", "Makanan": "#fe640b",
}

# Ekstrak vektor
vektor = np.array([model[k] for k in kata_pilihan])

# Reduksi dimensi ke 2D
pca = PCA(n_components=2)
koordinat_2d = pca.fit_transform(vektor)
```

**(b)** Buat scatter plot dengan label dan warna per kelompok:

```{.python .numberLines startFrom=34}
plt.figure(figsize=(8, 6))
sudah_label = set()

for i, kata in enumerate(kata_pilihan):
    k = kelompok[kata]
    lbl = k if k not in sudah_label else ""
    sudah_label.add(k)

    plt.scatter(
        koordinat_2d[i, 0], koordinat_2d[i, 1],
        c=warna[k], s=100, label=lbl,
    )
    plt.annotate(
        kata, (koordinat_2d[i, 0], koordinat_2d[i, 1]),
        textcoords="offset points", xytext=(8, 4),
        fontsize=10, fontweight="bold",
    )

plt.title("Proyeksi 2D Vektor Kata Indonesia (PCA)")
plt.xlabel("Komponen Utama 1")
plt.ylabel("Komponen Utama 2")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("visualisasi_embeddings.png", dpi=150)
plt.show()
```

**(c)** Analisis (3–5 kalimat):

- Apakah kluster yang terbentuk sesuai intuisi Anda?
- Kata mana yang paling "tercampur" atau berjauhan dari klompoknya?
- Mengapa menurut Anda hal tersebut terjadi?

\newpage

## Soal 5 — Polisemi: Limitasi Embeddings Statis

Word embeddings klasik memberikan **satu vektor tetap per kata**, sehingga tidak dapat membedakan makna kata yang bergantung pada konteks. Kata **"tahu"** dalam bahasa Indonesia memiliki dua makna yang benar-benar berbeda: makanan dari kedelai (nomina) dan mengetahui (verba).

### Instruksi

**(a)** Dari fastText Indonesia, ambil vektor kata `"tahu"`. Tampilkan 5 kata terdekat:

```{.python .numberLines startFrom=1}
print("5 kata paling mirip dengan 'tahu':")
for kata, skor in model.most_similar("tahu", topn=5):
    print(f"  {kata:<16} {skor:.4f}")
```

**(b)** Kata `"tahu"` memiliki **2 makna yang berbeda**:

- **Makanan:** "Ibu membeli **tahu** goreng di pasar." (makanan dari kedelai)
- **Mengetahui:** "Saya **tahu** jawaban soal itu." (kata kerja: mengetahui)

Jawab dalam 3–5 kalimat:

- Apakah 5 kata terdekat dari fastText mencerminkan **kedua** makna tersebut, atau hanya salah satu?
- Apakah makna yang terwakili cenderung ke makanan atau ke pengetahuan? Mengapa?
- Mengapa hal ini menjadi keterbatasan fundamental embeddings statis?

**(c) (Opsional — Bonus)** Jika lingkungan mendukung `transformers` dan `torch`:

```bash
pip install transformers torch
```

```{.python .numberLines startFrom=1}
from transformers import AutoTokenizer, AutoModel
import torch

# Muat IndoBERT pra-latih (inferensi saja, tanpa pelatihan)
name = "indobenchmark/indobert-base-p1"
tokenizer = AutoTokenizer.from_pretrained(name)
model_bert = AutoModel.from_pretrained(name)
model_bert.eval()

def vektor_kata(kalimat, kata):
    """Vektor kontekstual sebuah kata dari hidden state BERT."""
    enc = tokenizer(kalimat, return_tensors="pt")
    with torch.no_grad():
        out = model_bert(**enc)
    hidden = out.last_hidden_state[0]          # [seq_len, 768]
    ids = tokenizer.encode(kata, add_special_tokens=False)
    pos = (enc["input_ids"][0] == ids[0]).nonzero()[0].item()
    return hidden[pos]

# Konteks makanan
s1 = "Ibu membeli tahu goreng di pasar."
# Konteks pengetahuan
s2 = "Saya tahu jawaban soal itu."

v1 = vektor_kata(s1, "tahu")
v2 = vektor_kata(s2, "tahu")

cos = torch.nn.functional.cosine_similarity(
    v1.unsqueeze(0), v2.unsqueeze(0)
).item()

print(f"Kemiripan vektor 'tahu' antar dua konteks: {cos:.4f}")
print("Nilai jauh dari 1.0 membuktikan embeddings kontekstual berbeda.")
```

Bandingkan hasil IndoBERT dengan fastText. Tulis kesimpulan:

- Seberapa berbeda vektor kontekstual `"tahu"` di dua kalimat tersebut?
- Bagaimana hal ini membuktikan keunggulan contextual embeddings?

\newpage

## Soal 6 — Refleksi: Evolusi Arsitektur Sekuensial

Representasi teks yang baik memerlukan arsitektur yang mampu menangkap **ketergantungan sekuensial**. Bagian ini menguji pemahaman konseptual terhadap evolusi arsitektur dari RNN ke Transformer.

### Instruksi

Jawab **dua** pertanyaan berikut dalam bentuk paragraf singkat (masing-masing **5–8 kalimat**):

**(a) Vanishing Gradient & Mekanisme LSTM**

RNN memiliki masalah *vanishing gradient*: saat memproses sekuens panjang, informasi dari kata-kata awal menghilang sebelum mencapai kata akhir. Jelaskan secara intuitif:

- Mengapa masalah ini muncul? (Kaitkan dengan propagasi gradien melalui banyak langkah waktu.)
- Bagaimana LSTM mengatasinya melalui mekanisme *gates* (forget gate, input gate, output gate)?
- Gunakan **analogi sederhana** untuk memperjelas penjelasan Anda.

**(b) RNN/LSTM vs Transformer: Trade-off**

Transformer kini mendominasi NLP melalui mekanisme *self-attention* yang memproses seluruh sekuens secara paralel. Namun, RNN/LSTM masih relevan di beberapa skenario.

- Sebutkan **satu contoh konkret** skenario di mana RNN/LSTM mungkin lebih unggul atau lebih praktis daripada Transformer.
- Jelaskan alasannya dengan merujuk pada **sifat arsitektur** keduanya (misal: kompleksitas komputasi, ukuran model, panjang sekuens, real-time streaming).

\newpage

## Format Pengumpulan

| Item | Format |
|---|---|
| Kode | Jupyter Notebook (`.ipynb`) atau Python script (`.py`) |
| Analisis tertulis | Markdown cell dalam notebook atau dokumen PDF terpisah |
| Visualisasi | Plot tersimpan atau di-embed dalam notebook |

## Kriteria Penilaian

| Aspek | Bobot | Deskripsi |
|---|:---:|---|
| **Kebenaran teknis** | 40% | Kode berjalan tanpa error, output benar, penggunaan library tepat |
| **Kedalaman analisis** | 30% | Penjelasan tertulis mendalam, bukan sekadar mendeskripsikan output |
| **Eksplorasi kreatif** | 15% | Pemilihan kata/kelompok menarik (Soal 4), analogi kreatif (Soal 3d) |
| **Kualitas presentasi** | 15% | Laporan rapi, terstruktur, visualisasi informatif dan berlabel |

## Referensi

1. Mikolov, T., et al. (2013). *Efficient Estimation of Word Representations in Vector Space*.
2. Vaswani, A., et al. (2017). *Attention Is All You Need*.
3. Devlin, J., et al. (2019). *BERT: Pre-training of Deep Bidirectional Transformers*.
4. Bojanowski, P., et al. (2017). *Enriching Word Vectors with Subword Information* (fastText).
5. Wilie, B., et al. (2020). *IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding*.

---

**Estimasi waktu pengerjaan:** 3–4 jam

**Soal 1–5:** Wajib dikerjakan oleh semua mahasiswa

**Soal 5(c):** Opsional / Bonus — memerlukan `transformers` + `torch` (~400 MB)

**Soal 6:** Dapat dikerjakan tanpa kode — murni pemahaman konseptual
