import csv
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


APP_DIR = Path(__file__).resolve().parent
DATASET_PATH = APP_DIR / "dataset" / "diagnosa_penyakit.csv"

GEJALA = {
    "S01": "Demam tinggi",
    "S02": "Sakit kepala",
    "S03": "Nyeri otot / sendi",
    "S04": "Bintik merah di kulit",
    "S05": "Mual atau muntah",
    "S06": "Batuk",
    "S07": "Pilek",
    "S08": "Sakit tenggorokan",
    "S09": "Bersin-bersin",
    "S10": "Sering haus",
    "S11": "Sering buang air kecil",
    "S12": "Berat badan turun",
    "S13": "Luka sulit sembuh",
    "S14": "Buang air besar cair",
    "S15": "Perut kembung / sakit perut",
    "S16": "Tanda dehidrasi",
    "S17": "Lemas dan lesu",
    "S18": "Nafsu makan turun",
    "S19": "Penglihatan kabur",
    "S20": "Kesemutan tangan / kaki",
}

WARNA = {
    "latar": "#F5F7FA",
    "putih": "#FFFFFF",
    "teks": "#162A3A",
    "redup": "#718096",
    "utama": "#087F8C",
    "utama_gelap": "#066875",
    "aksen": "#E5F5F3",
    "garis": "#E6EBF0",
    "peringatan": "#FFF8E8",
    "header": "#102B3F",
    "terpilih": "#F0FAF8",
}


def baca_dataset():
    """Muat dan validasi data contoh dari folder dataset."""
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(f"File dataset tidak ditemukan:\n{DATASET_PATH}")

    kolom_gejala = list(GEJALA)
    wajib = {"id_data", "diagnosa", *kolom_gejala}
    with DATASET_PATH.open("r", encoding="utf-8-sig", newline="") as file_csv:
        pembaca = csv.DictReader(file_csv)
        if not pembaca.fieldnames or not wajib.issubset(pembaca.fieldnames):
            raise ValueError(
                "Kolom CSV tidak sesuai. Pastikan ada id_data, diagnosa, "
                "dan kolom S01 sampai S20."
            )

        baris_data = []
        for nomor_baris, baris in enumerate(pembaca, start=2):
            if not baris.get("diagnosa"):
                raise ValueError(f"Label diagnosa kosong pada baris {nomor_baris}.")
            fitur = {}
            for kode in kolom_gejala:
                nilai = (baris.get(kode) or "").strip()
                if nilai not in {"0", "1"}:
                    raise ValueError(
                        f"Nilai kolom {kode} pada baris {nomor_baris} "
                        "harus 0 atau 1."
                    )
                fitur[kode] = nilai == "1"
            baris_data.append({
                "id_data": baris.get("id_data", ""),
                "diagnosa": baris["diagnosa"].strip(),
                "fitur": fitur,
            })

    if not baris_data:
        raise ValueError("Dataset tidak memiliki data.")
    return baris_data


def hitung_kecocokan(gejala_dipilih, baris_data):
    """Urutkan diagnosis berdasarkan kecocokan Jaccard dengan contoh dataset."""
    dipilih = set(gejala_dipilih)
    skor_per_penyakit = {}

    for baris in baris_data:
        gejala_contoh = {
            kode for kode, aktif in baris["fitur"].items() if aktif
        }
        irisan = len(dipilih & gejala_contoh)
        gabungan = len(dipilih | gejala_contoh)
        skor = irisan / gabungan if gabungan else 0.0
        skor_per_penyakit.setdefault(baris["diagnosa"], []).append(skor)

    ringkasan = [
        (penyakit, max(skor_list))
        for penyakit, skor_list in skor_per_penyakit.items()
    ]
    return sorted(ringkasan, key=lambda item: item[1], reverse=True)


def buat_aplikasi(root, data_dataset):
    root.title("Sahabat Sehat | Pemeriksaan Gejala")
    root.geometry("1180x800")
    root.minsize(920, 680)
    root.configure(bg=WARNA["latar"])

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Treeview", background=WARNA["putih"], fieldbackground=WARNA["putih"],
        foreground=WARNA["teks"], rowheight=40, font=("Segoe UI", 10),
        borderwidth=0, relief="flat",
    )
    style.configure(
        "Treeview.Heading", background="#F4F7F9", foreground=WARNA["redup"],
        font=("Segoe UI", 9, "bold"), relief="flat", padding=(12, 10),
    )
    style.map("Treeview", background=[("selected", WARNA["aksen"])],
              foreground=[("selected", WARNA["teks"])])

    def buka_tampilan_web():
        from web_app import buka_web

        try:
            url = buka_web(data_dataset)
        except OSError as error:
            messagebox.showerror(
                "Web tidak dapat dijalankan",
                f"Server web lokal gagal dijalankan:\n{error}",
                parent=root,
            )
            return
        messagebox.showinfo(
            "Versi web dibuka",
            f"Aplikasi dapat dibuka di browser melalui alamat:\n{url}",
            parent=root,
        )

    header = tk.Frame(root, bg=WARNA["header"], padx=36, pady=25)
    header.pack(fill="x")
    header.grid_columnconfigure(0, weight=1)
    brand = tk.Frame(header, bg=WARNA["header"])
    brand.grid(row=0, column=0, sticky="w")
    tk.Label(
        brand, text="✚", bg=WARNA["header"], fg="#63D6C7",
        font=("Segoe UI", 25, "bold"),
    ).pack(side="left", padx=(0, 12))
    brand_text = tk.Frame(brand, bg=WARNA["header"])
    brand_text.pack(side="left")
    tk.Label(
        brand_text, text="Sahabat Sehat", bg=WARNA["header"], fg="white",
        font=("Segoe UI", 22, "bold"),
    ).pack(anchor="w")
    tk.Label(
        brand_text, text="Pemeriksaan gejala berbasis dataset",
        bg=WARNA["header"], fg="#BDD0D9", font=("Segoe UI", 10),
    ).pack(anchor="w", pady=(2, 0))
    tk.Button(
        header, text="Buka versi web", command=buka_tampilan_web,
        bg=WARNA["utama"], fg="white", activebackground=WARNA["utama_gelap"],
        activeforeground="white", relief="flat", cursor="hand2",
        font=("Segoe UI", 9, "bold"), padx=14, pady=9, bd=0,
    ).grid(row=0, column=1, sticky="e", padx=(12, 14))
    tk.Label(
        header, text="●  DATASET AKTIF", bg="#1C4053", fg="#8BE0D3",
        font=("Segoe UI", 9, "bold"), padx=13, pady=9,
    ).grid(row=0, column=2, sticky="e")

    konten = tk.Frame(root, bg=WARNA["latar"], padx=22, pady=18)
    konten.pack(fill="both", expand=True)
    konten.grid_columnconfigure(0, weight=3, uniform="kolom")
    konten.grid_columnconfigure(1, weight=2, uniform="kolom")
    konten.grid_rowconfigure(0, weight=1)

    kartu_gejala = tk.Frame(
        konten, bg=WARNA["putih"], padx=20, pady=18,
        highlightthickness=1, highlightbackground=WARNA["garis"],
    )
    kartu_gejala.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    kartu_gejala.grid_rowconfigure(3, weight=1)
    kartu_gejala.grid_columnconfigure(0, weight=1)
    tk.Label(
        kartu_gejala, text="Pilih gejala",
        bg=WARNA["putih"], fg=WARNA["teks"],
        font=("Segoe UI", 17, "bold"),
    ).grid(row=0, column=0, sticky="w")
    header_gejala = tk.Frame(kartu_gejala, bg=WARNA["putih"])
    header_gejala.grid(row=1, column=0, sticky="ew", pady=(4, 14))
    header_gejala.grid_columnconfigure(0, weight=1)
    tk.Label(
        header_gejala, text="Pilih semua yang sesuai dengan kondisi Anda.",
        bg=WARNA["putih"], fg=WARNA["redup"], font=("Segoe UI", 10),
    ).grid(row=0, column=0, sticky="w")
    label_jumlah = tk.Label(
        header_gejala, text="0 dipilih", bg=WARNA["aksen"],
        fg=WARNA["utama_gelap"], font=("Segoe UI", 9, "bold"),
        padx=10, pady=5,
    )
    label_jumlah.grid(row=0, column=1, sticky="e")

    cari_var = tk.StringVar()
    kolom_cari = tk.Frame(
        kartu_gejala, bg="#F7F9FB", highlightthickness=1,
        highlightbackground=WARNA["garis"],
    )
    kolom_cari.grid(row=2, column=0, sticky="ew", pady=(0, 12))
    tk.Label(
        kolom_cari, text="⌕", bg="#F7F9FB", fg=WARNA["redup"],
        font=("Segoe UI", 16),
    ).pack(side="left", padx=(10, 4))
    entry_cari = tk.Entry(
        kolom_cari, textvariable=cari_var, relief="flat", bd=0,
        bg="#F7F9FB", fg=WARNA["teks"], insertbackground=WARNA["utama"],
        font=("Segoe UI", 10),
    )
    entry_cari.pack(side="left", fill="x", expand=True, ipady=10, padx=(2, 10))
    entry_cari.insert(0, "")

    area = tk.Frame(kartu_gejala, bg=WARNA["putih"])
    area.grid(row=3, column=0, sticky="nsew")
    area.grid_columnconfigure(0, weight=1)
    area.grid_columnconfigure(1, weight=1)
    canvas = tk.Canvas(area, bg=WARNA["putih"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
    isi_gejala = tk.Frame(canvas, bg=WARNA["putih"])
    isi_gejala.bind(
        "<Configure>",
        lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    window_id = canvas.create_window((0, 0), window=isi_gejala, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    pilihan = {}
    kartu_item = {}

    def perbarui_jumlah(*_args):
        terpilih = sum(var.get() for var in pilihan.values())
        label_jumlah.config(text=f"{terpilih} dipilih")

    for urutan, (kode, nama) in enumerate(GEJALA.items()):
        variabel = tk.BooleanVar(value=False)
        pilihan[kode] = variabel
        tile = tk.Frame(
            isi_gejala, bg=WARNA["putih"], padx=5, pady=3,
            highlightthickness=1, highlightbackground=WARNA["garis"],
        )
        tile.grid(row=urutan // 2, column=urutan % 2, sticky="ew", padx=4, pady=4)
        check = tk.Checkbutton(
            tile, text=nama, variable=variabel, anchor="w",
            bg=WARNA["putih"], fg=WARNA["teks"], activebackground=WARNA["putih"],
            selectcolor=WARNA["aksen"], activeforeground=WARNA["utama"],
            font=("Segoe UI", 9), wraplength=195, justify="left",
            padx=7, pady=8, cursor="hand2",
        )
        check.pack(fill="both", expand=True)
        kartu_item[kode] = tile

        def ubah_tampilan(_var, _index, _mode, kode_gejala=kode, tile_gejala=tile):
            dipilih = pilihan[kode_gejala].get()
            warna = WARNA["terpilih"] if dipilih else WARNA["putih"]
            garis = WARNA["utama"] if dipilih else WARNA["garis"]
            tile_gejala.configure(bg=warna, highlightbackground=garis)
            for widget in tile_gejala.winfo_children():
                widget.configure(bg=warna, activebackground=warna)
            perbarui_jumlah()

        variabel.trace_add("write", ubah_tampilan)

    def cari_gejala(*_args):
        kueri = cari_var.get().strip().casefold()
        for kode, nama in GEJALA.items():
            if kueri in nama.casefold() or kueri in kode.casefold():
                kartu_item[kode].grid()
            else:
                kartu_item[kode].grid_remove()

    def atur_lebar_daftar(event):
        canvas.itemconfigure(window_id, width=event.width)

    canvas.bind("<Configure>", atur_lebar_daftar)
    cari_var.trace_add("write", cari_gejala)

    kartu_hasil = tk.Frame(
        konten, bg=WARNA["putih"], padx=20, pady=18,
        highlightthickness=1, highlightbackground=WARNA["garis"],
    )
    kartu_hasil.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    kartu_hasil.grid_columnconfigure(0, weight=1)
    kartu_hasil.grid_rowconfigure(5, weight=1)
    tk.Label(
        kartu_hasil, text="Hasil pemeriksaan",
        bg=WARNA["putih"], fg=WARNA["teks"],
        font=("Segoe UI", 15, "bold"),
    ).grid(row=0, column=0, sticky="w")

    hasil_utama = tk.Frame(kartu_hasil, bg=WARNA["aksen"], padx=16, pady=14)
    hasil_utama.grid(row=1, column=0, sticky="ew", pady=(14, 18))
    tk.Label(
        hasil_utama, text="KEMUNGKINAN TERATAS",
        bg=WARNA["aksen"], fg=WARNA["utama_gelap"],
        font=("Segoe UI", 8, "bold"),
    ).pack(anchor="w")
    label_diagnosa = tk.Label(
        hasil_utama, text="Belum ada hasil", bg=WARNA["aksen"],
        fg=WARNA["teks"], font=("Segoe UI", 18, "bold"),
        wraplength=300, justify="left",
    )
    label_diagnosa.pack(anchor="w", pady=(5, 2))
    label_skor = tk.Label(
        hasil_utama, text="Pilih gejala lalu tekan Periksa.",
        bg=WARNA["aksen"], fg=WARNA["redup"], font=("Segoe UI", 9),
    )
    label_skor.pack(anchor="w")

    tk.Label(
        kartu_hasil, text="Urutan kecocokan",
        bg=WARNA["putih"], fg=WARNA["teks"],
        font=("Segoe UI", 11, "bold"),
    ).grid(row=2, column=0, sticky="w", pady=(0, 8))
    tabel = ttk.Treeview(
        kartu_hasil, columns=("penyakit", "skor"), show="headings", height=5,
    )
    tabel.heading("penyakit", text="KATEGORI")
    tabel.heading("skor", text="SKOR")
    tabel.column("penyakit", width=165, anchor="w")
    tabel.column("skor", width=75, anchor="center")
    tabel.grid(row=3, column=0, sticky="ew")

    info_dataset = tk.Label(
        kartu_hasil, text="", bg=WARNA["putih"], fg=WARNA["redup"],
        font=("Segoe UI", 9), justify="left",
    )
    info_dataset.grid(row=4, column=0, sticky="w", pady=(12, 0))
    tk.Label(
        kartu_hasil,
        text=(
            "Catatan: dataset ini merupakan data simulasi untuk pembelajaran. "
            "Skor menunjukkan kemiripan gejala, bukan probabilitas atau "
            "diagnosis medis. Konsultasikan keluhan kepada tenaga kesehatan."
        ),
        bg=WARNA["peringatan"], fg="#7C4A03", font=("Segoe UI", 9),
        wraplength=340, justify="left", padx=12, pady=10,
    ).grid(row=5, column=0, sticky="new", pady=(16, 0))

    tombol = tk.Frame(kartu_gejala, bg=WARNA["putih"])
    tombol.grid(row=4, column=0, sticky="ew", pady=(14, 0))

    def periksa():
        dipilih = [kode for kode, var in pilihan.items() if var.get()]
        if not dipilih:
            messagebox.showinfo(
                "Pilih gejala", "Pilih setidaknya satu gejala terlebih dahulu."
            )
            return

        hasil = hitung_kecocokan(dipilih, data_dataset)
        if not hasil or hasil[0][1] == 0:
            label_diagnosa.config(text="Belum ada kecocokan")
            label_skor.config(text="Gejala pilihan tidak cocok dengan contoh dataset.")
            tabel.delete(*tabel.get_children())
            return

        penyakit, skor = hasil[0]
        label_diagnosa.config(text=penyakit)
        label_skor.config(text=f"Kecocokan tertinggi: {skor:.0%}")
        tabel.delete(*tabel.get_children())
        for nama, nilai in hasil:
            tabel.insert("", "end", values=(nama, f"{nilai:.0%}"))

    def reset():
        for var in pilihan.values():
            var.set(False)
        label_diagnosa.config(text="Belum ada hasil")
        label_skor.config(text="Pilih gejala lalu tekan Periksa.")
        tabel.delete(*tabel.get_children())

    tk.Button(
        tombol, text="Periksa gejala", command=periksa,
        bg=WARNA["utama"], fg="white", activebackground=WARNA["utama_gelap"],
        activeforeground="white", relief="flat", cursor="hand2",
        font=("Segoe UI", 10, "bold"), padx=20, pady=11, bd=0,
    ).pack(side="left")
    tk.Button(
        tombol, text="Reset", command=reset, bg="#EEF2F7", fg=WARNA["teks"],
        activebackground="#E2E8F0", relief="flat", cursor="hand2",
        font=("Segoe UI", 10), padx=20, pady=11, bd=0,
    ).pack(side="left", padx=(9, 0))

    info_dataset.config(
        text=f"Dataset aktif: {len(data_dataset)} contoh • {len(GEJALA)} gejala"
    )


if __name__ == "__main__":
    try:
        data_dataset = baca_dataset()
    except (OSError, ValueError, csv.Error) as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Dataset bermasalah", str(error))
        root.destroy()
        raise

    root = tk.Tk()
    buat_aplikasi(root, data_dataset)
    root.mainloop()