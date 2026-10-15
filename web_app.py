import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from app import GEJALA, hitung_kecocokan


HOST = "127.0.0.1"
HTML = r"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#102b3f">
  <title>Sahabat Sehat | Pemeriksaan Gejala</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #162a3a; --muted: #718096; --teal: #087f8c;
      --teal-dark: #066875; --line: #e6ebf0; --canvas: #f5f7fa;
      --mint: #e5f5f3; --white: #fff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; background: var(--canvas); color: var(--ink);
      font: 15px/1.5 "Segoe UI", Inter, system-ui, -apple-system, sans-serif;
    }
    header { background: #102b3f; color: white; }
    .topbar {
      max-width: 1180px; margin: auto; padding: 24px 28px;
      display: flex; align-items: center; justify-content: space-between; gap: 20px;
    }
    .brand { display: flex; align-items: center; gap: 14px; }
    .brand-icon {
      color: #63d6c7; font-size: 32px; font-weight: 800;
      width: 48px; height: 48px; display: grid; place-items: center;
      border: 1px solid #315064; border-radius: 15px;
    }
    h1 { margin: 0; font-size: 23px; line-height: 1.2; letter-spacing: -.4px; }
    .subtitle { color: #bdd0d9; font-size: 13px; margin-top: 5px; }
    .status {
      white-space: nowrap; border-radius: 99px; padding: 9px 13px;
      color: #8be0d3; background: #1c4053; font-size: 11px; font-weight: 750;
      letter-spacing: .5px;
    }
    main {
      max-width: 1180px; margin: auto; padding: 26px 28px 38px;
      display: grid; grid-template-columns: minmax(0, 1.18fr) minmax(320px, .82fr);
      gap: 20px; align-items: stretch;
    }
    .card {
      background: var(--white); border: 1px solid var(--line); border-radius: 18px;
      padding: 23px; box-shadow: 0 8px 24px rgba(22, 42, 58, .035);
    }
    .card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
    h2 { margin: 0; font-size: 19px; letter-spacing: -.3px; }
    .hint { color: var(--muted); font-size: 13px; margin: 5px 0 0; }
    .count {
      color: var(--teal-dark); background: var(--mint); border-radius: 99px;
      padding: 7px 11px; white-space: nowrap; font-size: 12px; font-weight: 700;
    }
    .search {
      width: 100%; margin: 18px 0 13px; padding: 12px 14px;
      color: var(--ink); background: #f7f9fb; border: 1px solid var(--line);
      border-radius: 11px; font: inherit; outline: none;
    }
    .search:focus { border-color: #58b9b2; box-shadow: 0 0 0 3px rgba(8,127,140,.1); }
    .symptoms {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px; max-height: 432px; overflow: auto; padding: 1px 3px 4px 1px;
    }
    .symptom {
      display: flex; align-items: flex-start; gap: 10px; min-height: 52px;
      padding: 12px 11px; border: 1px solid var(--line); border-radius: 11px;
      cursor: pointer; transition: background .15s, border-color .15s, transform .15s;
    }
    .symptom:hover { border-color: #9acfc9; transform: translateY(-1px); }
    .symptom:has(input:checked) { border-color: var(--teal); background: #f0faf8; }
    .symptom input { accent-color: var(--teal); margin: 3px 0 0; }
    .symptom span { font-size: 13px; line-height: 1.35; }
    .actions { display: flex; gap: 10px; margin-top: 19px; }
    button {
      border: 0; border-radius: 10px; padding: 12px 18px; cursor: pointer;
      font: 700 13px inherit; font-family: inherit; font-size: 13px;
      transition: background .15s, transform .15s;
    }
    button:hover { transform: translateY(-1px); }
    .primary { background: var(--teal); color: white; }
    .primary:hover { background: var(--teal-dark); }
    .secondary { color: var(--ink); background: #eef2f7; }
    .results { display: flex; flex-direction: column; gap: 18px; }
    .hero-result {
      background: linear-gradient(135deg, #e5f5f3, #f2faf8);
      border: 1px solid #d7eeea; border-radius: 14px; padding: 18px;
    }
    .eyebrow { color: var(--teal-dark); font-size: 10px; font-weight: 800; letter-spacing: 1px; }
    .diagnosis { margin: 8px 0 3px; font-size: 24px; letter-spacing: -.5px; }
    .score-line { color: var(--muted); font-size: 13px; }
    .section-title { margin: 0 0 3px; font-size: 14px; }
    .ranking { display: grid; gap: 13px; }
    .rank-head { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }
    .rank-score { color: var(--muted); font-variant-numeric: tabular-nums; }
    .track { height: 7px; margin-top: 7px; overflow: hidden; background: #edf1f4; border-radius: 99px; }
    .fill { height: 100%; background: var(--teal); border-radius: inherit; transition: width .25s; }
    .empty {
      border: 1px dashed #d6dfe7; border-radius: 12px; padding: 20px;
      color: var(--muted); text-align: center; font-size: 13px;
    }
    .note {
      margin-top: auto; padding: 13px 14px; border-radius: 11px;
      background: #fff8e8; color: #7c4a03; font-size: 12px;
    }
    .footer { max-width: 1180px; margin: -17px auto 0; padding: 0 28px 24px; color: var(--muted); font-size: 12px; }
    @media (max-width: 800px) {
      main { grid-template-columns: 1fr; padding: 18px 16px 30px; }
      .topbar { padding: 20px 16px; }
      .card { padding: 19px; }
      .symptoms { max-height: 360px; }
      .footer { padding-inline: 16px; }
    }
    @media (max-width: 480px) {
      h1 { font-size: 19px; }
      .brand-icon { width: 42px; height: 42px; }
      .status { font-size: 0; padding: 10px; }
      .status::after { content: "●"; font-size: 12px; }
      .symptoms { grid-template-columns: 1fr; }
      .card-head { align-items: center; }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div class="brand">
        <div class="brand-icon" aria-hidden="true">✚</div>
        <div><h1>Sahabat Sehat</h1><div class="subtitle">Pemeriksaan gejala berbasis dataset</div></div>
      </div>
      <div class="status">● DATASET AKTIF</div>
    </div>
  </header>
  <main>
    <section class="card">
      <div class="card-head">
        <div><h2>Pilih gejala</h2><p class="hint">Pilih semua yang sesuai dengan kondisi Anda.</p></div>
        <span class="count" id="count">0 dipilih</span>
      </div>
      <input class="search" id="search" type="search" placeholder="Cari gejala..." aria-label="Cari gejala">
      <div class="symptoms" id="symptoms" aria-label="Daftar gejala"></div>
      <div class="actions">
        <button class="primary" id="check">Periksa gejala</button>
        <button class="secondary" id="reset">Reset</button>
      </div>
    </section>
    <section class="card results">
      <div><h2>Hasil pemeriksaan</h2><p class="hint">Kemiripan dihitung dari contoh pada dataset.</p></div>
      <div class="hero-result" aria-live="polite">
        <div class="eyebrow">KEMUNGKINAN TERATAS</div>
        <div class="diagnosis" id="diagnosis">Belum ada hasil</div>
        <div class="score-line" id="score">Pilih gejala lalu tekan Periksa.</div>
      </div>
      <div><h3 class="section-title">Urutan kecocokan</h3></div>
      <div class="ranking" id="ranking"><div class="empty">Hasil pemeriksaan akan tampil di sini.</div></div>
      <div class="note">Data ini merupakan simulasi untuk pembelajaran. Skor adalah kemiripan gejala, bukan probabilitas atau diagnosis medis. Konsultasikan keluhan kepada tenaga kesehatan.</div>
    </section>
  </main>
  <div class="footer" id="dataset-info">Memuat dataset...</div>
  <script>
    const symptomsEl = document.querySelector("#symptoms");
    const countEl = document.querySelector("#count");
    const diagnosisEl = document.querySelector("#diagnosis");
    const scoreEl = document.querySelector("#score");
    const rankingEl = document.querySelector("#ranking");
    const selected = new Set();
    let symptoms = {};

    function renderSymptoms(query = "") {
      symptomsEl.replaceChildren();
      const normalized = query.trim().toLocaleLowerCase("id");
      for (const [code, name] of Object.entries(symptoms)) {
        if (!`${code} ${name}`.toLocaleLowerCase("id").includes(normalized)) continue;
        const label = document.createElement("label");
        label.className = "symptom";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = selected.has(code);
        checkbox.addEventListener("change", () => {
          checkbox.checked ? selected.add(code) : selected.delete(code);
          countEl.textContent = `${selected.size} dipilih`;
        });
        const text = document.createElement("span");
        text.textContent = name;
        label.append(checkbox, text);
        symptomsEl.append(label);
      }
    }

    function renderResults(items) {
      rankingEl.replaceChildren();
      if (!items.length || items[0].score === 0) {
        diagnosisEl.textContent = "Belum ada kecocokan";
        scoreEl.textContent = "Gejala yang dipilih tidak cocok dengan contoh dataset.";
        rankingEl.innerHTML = '<div class="empty">Coba pilih gejala lain.</div>';
        return;
      }
      diagnosisEl.textContent = items[0].disease;
      scoreEl.textContent = `Kecocokan tertinggi: ${Math.round(items[0].score * 100)}%`;
      for (const item of items) {
        const row = document.createElement("div");
        const head = document.createElement("div");
        head.className = "rank-head";
        const name = document.createElement("strong");
        name.textContent = item.disease;
        const percent = document.createElement("span");
        percent.className = "rank-score";
        percent.textContent = `${Math.round(item.score * 100)}%`;
        head.append(name, percent);
        const track = document.createElement("div");
        track.className = "track";
        const fill = document.createElement("div");
        fill.className = "fill";
        fill.style.width = `${Math.round(item.score * 100)}%`;
        track.append(fill);
        row.append(head, track);
        rankingEl.append(row);
      }
    }

    document.querySelector("#search").addEventListener("input", event => renderSymptoms(event.target.value));
    document.querySelector("#check").addEventListener("click", async () => {
      if (!selected.size) {
        diagnosisEl.textContent = "Pilih gejala terlebih dahulu";
        scoreEl.textContent = "Pilih minimal satu gejala untuk memulai pemeriksaan.";
        return;
      }
      const button = document.querySelector("#check");
      button.disabled = true;
      button.textContent = "Memeriksa...";
      try {
        const response = await fetch("/api/diagnosa", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ gejala: [...selected] })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Tidak dapat memproses pemeriksaan.");
        renderResults(data.hasil);
      } catch (error) {
        diagnosisEl.textContent = "Pemeriksaan gagal";
        scoreEl.textContent = error.message;
      } finally {
        button.disabled = false;
        button.textContent = "Periksa gejala";
      }
    });
    document.querySelector("#reset").addEventListener("click", () => {
      selected.clear();
      countEl.textContent = "0 dipilih";
      renderSymptoms(document.querySelector("#search").value);
      diagnosisEl.textContent = "Belum ada hasil";
      scoreEl.textContent = "Pilih gejala lalu tekan Periksa.";
      rankingEl.innerHTML = '<div class="empty">Hasil pemeriksaan akan tampil di sini.</div>';
    });

    fetch("/api/gejala")
      .then(response => {
        if (!response.ok) throw new Error("Dataset tidak dapat dimuat.");
        return response.json();
      })
      .then(data => {
        symptoms = data.gejala;
        renderSymptoms();
        document.querySelector("#dataset-info").textContent =
          `Dataset aktif: ${data.jumlah_data} contoh · ${Object.keys(symptoms).length} gejala · 5 kategori penyakit`;
      })
      .catch(error => {
        document.querySelector("#dataset-info").textContent = error.message;
      });
  </script>
</body>
</html>
"""


_server = None
_server_lock = threading.Lock()


def buat_server(data_dataset, port=0):
    """Buat server web localhost yang memakai data dan fungsi diagnosis aplikasi."""
    gejala_diizinkan = set(GEJALA)

    class RequestHandler(BaseHTTPRequestHandler):
        def _kirim_json(self, status, isi):
            body = json.dumps(isi, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/":
                body = HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif path == "/api/gejala":
                self._kirim_json(200, {
                    "gejala": GEJALA,
                    "jumlah_data": len(data_dataset),
                })
            else:
                self._kirim_json(404, {"error": "Halaman tidak ditemukan."})

        def do_POST(self):
            if urlparse(self.path).path != "/api/diagnosa":
                self._kirim_json(404, {"error": "Endpoint tidak ditemukan."})
                return
            try:
                panjang = int(self.headers.get("Content-Length", "0"))
                if panjang <= 0 or panjang > 16_384:
                    self._kirim_json(400, {"error": "Ukuran permintaan tidak valid."})
                    return
                payload = json.loads(self.rfile.read(panjang).decode("utf-8"))
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                self._kirim_json(400, {"error": "Isi permintaan harus berupa JSON yang valid."})
                return

            gejala = payload.get("gejala") if isinstance(payload, dict) else None
            if not isinstance(gejala, list) or not gejala:
                self._kirim_json(400, {"error": "Pilih minimal satu gejala."})
                return
            if any(not isinstance(kode, str) or kode not in gejala_diizinkan for kode in gejala):
                self._kirim_json(400, {"error": "Ada kode gejala yang tidak dikenal."})
                return

            hasil = hitung_kecocokan(gejala, data_dataset)
            self._kirim_json(200, {
                "hasil": [
                    {"disease": penyakit, "score": skor}
                    for penyakit, skor in hasil
                ],
            })

        def log_message(self, _format, *_args):
            return

    return ThreadingHTTPServer((HOST, port), RequestHandler)


def buka_web(data_dataset, open_browser=True):
    """Jalankan server web lokal sekali saja dan kembalikan URL aplikasinya."""
    global _server
    with _server_lock:
        if _server is None:
            _server = buat_server(data_dataset)
            thread = threading.Thread(target=_server.serve_forever, daemon=True)
            thread.start()
        url = f"http://{HOST}:{_server.server_address[1]}/"

    if open_browser:
        webbrowser.open(url)
    return url


if __name__ == "__main__":
    from app import baca_dataset

    dataset = baca_dataset()
    _server = buat_server(dataset, port=8000)
    url = f"http://{HOST}:{_server.server_address[1]}/"
    print(f"Aplikasi web berjalan di {url}")
    print("Tekan Ctrl+C untuk menghentikan server.")
    try:
        _server.serve_forever()
    except KeyboardInterrupt:
        _server.shutdown()
        _server.server_close()
