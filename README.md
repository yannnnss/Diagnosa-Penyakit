# Sahabat Sehat — Diagnosa Penyakit

Aplikasi pemeriksaan gejala berbasis dataset. Pengguna memilih gejala yang dirasakan,
aplikasi menghitung kecocokan terhadap contoh di dataset, lalu menampilkan kemungkinan
penyakit teratas beserta skor kecocokannya.

> ⚠️ Data di repo ini adalah **data simulasi untuk pembelajaran**. Skor menunjukkan
> kemiripan gejala, **bukan** probabilitas atau diagnosis medis. Konsultasikan keluhan
> kepada tenaga kesehatan.

## Cara kerja

- **20 gejala (S01–S20):** demam tinggi, sakit kepala, nyeri otot/sendi, bintik merah
  di kulit, mual/muntah, batuk, pilek, sakit tenggorokan, bersin-bersin, sering haus,
  sering buang air kecil, berat badan turun, luka sulit sembuh, BAB cair, perut
  kembung/sakit perut, tanda dehidrasi, lemas dan lesu, nafsu makan turun, penglihatan
  kabur, kesemutan tangan/kaki.
- **5 kategori penyakit**, masing-masing 6 contoh: DBD, Influenza, Diabetes, Diare,
  Tifus.
- **Dataset:** `dataset/diagnosa_penyakit.csv` — 30 baris, kolom `id_data`, `S01`–`S20`
  berisi `0`/`1`, dan `diagnosa`.
- **Skor** dihitung dengan kemiripan Jaccard: irisan gejala yang dipilih dengan gejala
  contoh, dibagi gabungannya. Diambil skor tertinggi per penyakit, lalu diurutkan.

## Menjalankan

Tidak butuh library tambahan — cukup Python 3 (pustaka standar, plus `tkinter` untuk
versi desktop yang sudah bawaan di instalasi Python Windows).

```bash
# Versi desktop
python app.py

# Versi web (server lokal di http://127.0.0.1:8000/)
python web_app.py
```

Di Windows, versi web juga bisa dijalankan dengan dobel-klik `jalankan_web.bat` —
server dinyalakan lalu browser otomatis terbuka. Dari aplikasi desktop, tombol
**"Buka versi web"** menjalankan server lokal yang sama.

## Struktur

- `app.py` — aplikasi desktop (Tkinter): pilih gejala, cari gejala, hasil pemeriksaan
- `web_app.py` — server web lokal (`http.server`) dengan API `/api/gejala` dan
  `/api/diagnosa`
- `dataset/diagnosa_penyakit.csv` — data contoh (30 baris)
- `jalankan_web.bat` — peluncur versi web di Windows
