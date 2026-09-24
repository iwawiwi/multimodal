# Proyek Akhir Multimodal

Perkakas untuk **Proyek Akhir Multimodal** (pengganti UAS, paruh kedua semester).

> TOR, rubrik, dan berkas tugas proyek **tidak** disimpan di sini — semuanya
> didistribusikan lewat LMS (lihat **D-A11** di `AGENTS.md`). Repositori ini
> publik, sehingga detail tantangan tidak boleh bocor ke angkatan berikutnya.
> Hanya **perkakas generik** yang tinggal di sini.

## Dataset

Tantangan semester ini memakai **SEA-VL Indonesian subset**
(`KORIKA-AI/sea-vl_crowdsourcing_id`, CC BY-SA 4.0) — pasangan gambar–teks
budaya Indonesia untuk tugas *cross-modal retrieval*.

## `scripts/build_dataset.py`

Membangun dataset dari sumber: unduh → filter lokasi → dedup → konversi RGB →
split terstratifikasi → manifest.

```bash
# sekali saja (butuh pyarrow + Pillow)
pip install -r proyek/scripts/requirements.txt

# periksa tanpa menulis apa pun
python3 proyek/scripts/build_dataset.py --verify-only

# bangun penuh (~1,6 GB unduhan sekali, ~2 menit, hasil ~480 MB)
python3 proyek/scripts/build_dataset.py --out proyek/data/sea-vl-id

# bundel untuk mahasiswa (hanya train + val; test ditahan)
python3 proyek/scripts/build_dataset.py --export /tmp/svl-dist
```

Keluaran:

```
proyek/data/sea-vl-id/
├── images/            satu gambar per baris, svl_<wikipedia_id>.jpg
├── manifest.csv       semua baris + kolom split
├── train.csv          split latih
├── val.csv            split validasi
├── test.csv           split uji  <-- PRIVAT, jangan dibagikan
├── ATTRIBUTION.md     kewajiban lisensi & sitasi
└── stats.json         ringkasan pipeline
```

Referensi (angka terverifikasi pada build pertama): 3.096 baris dibaca →
326 dibuang (lokasi) → 7 dibuang (duplikat) → **2.763 disimpan**;
split **train 2.072 / val 275 / test 416**.

> ⚠️ `proyek/data/` di-`.gitignore`. **`test.csv` beserta gambarnya adalah
> test set privat** dan baru boleh dibuka pada minggu evaluasi.
