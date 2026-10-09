#!/usr/bin/env python3
"""Laporan Berpusat — server tempatan baca-sahaja.

    python serve.py            # http://localhost:8898
    python serve.py --port N

Membaca folder di sebelahnya:
    data/manifest.json           senarai PBT (tambah PBT baharu di sini)
    data/<PBT>/runs/*.json       satu fail = satu larian (skema sepunya)

/api/data mengagregat semuanya pada SETIAP permintaan — letak fail larian
baharu ke dalam folder dan refresh browser sahaja.

GANTI NILAI (Fasa 5): kini PBT-aware — MBPG (oracle_n001/oracle_pk) dan
MBIP (testdata/excel_data.py + trafik_v2.py, disambung 2026-09-02 atas
arahan CEO). MBJB menyusul selepas enjin skripnya siap.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

import datetime
import re
import urllib.request
import urllib.error
import urllib.parse

# ---------------------------------------------------------------- config --
CFG_PATH = HERE / "config.json"
CFG_DEFAULT = {
    "mbpg_path": r"C:\Users\mrsai\Documents\antigravity\keen-lovelace\MBPG-testing",
    "mbip_path": r"C:\Users\mrsai\Documents\antigravity\keen-lovelace\mbip-testing\v3",
}
AI_PATH = HERE / "ai_config.json"
MODELS = ["glm-5.1", "glm-5.2", "glm-5.3", "kimi-k2.7", "kimi-k3",
          "deepseek-v4-flash", "deepseek-v4-pro", "minimax-m3",
          "hy3-tencent", "gpt-5.6-sol", "gpt-5.6-terra"]

MARK_MULA = "# === OVERRIDE TERMINAL GANTI-NILAI (dijana automatik) ==="
MARK_TAMAT = "# === TAMAT OVERRIDE TERMINAL ==="

# Medan rantaian dropdown — mesti sah bersama-sama.
RANTAIAN = ("keterangan_kod_kompaun", "kod_akta", "kesalahan_kompaun")

# PBT yang enjin Ganti Nilai sudah disambung.
TERMINAL_PBT = ("MBPG", "MBIP")


def cfg():
    try:
        return {**CFG_DEFAULT, **json.loads(CFG_PATH.read_text())}
    except Exception:
        return dict(CFG_DEFAULT)


def suite_path(pbt):
    kunci = {"MBPG": "mbpg_path", "MBIP": "mbip_path"}[pbt]
    return Path(cfg()[kunci])


def mbpg():
    return suite_path("MBPG")


def ai_cfg():
    try:
        return json.loads(AI_PATH.read_text())
    except Exception:
        return {"base_url": "", "api_key": "", "model": MODELS[0]}


# ---------------------------------------------------------------- oracle --
def _exec_fail(p):
    """Laksana fail testdata dalam namespace bersih; pulangkan namespace.
    (import biasa akan cache; exec segar membaca override terkini.)"""
    ns = {}
    exec(compile(p.read_text(encoding="utf-8"), str(p), "exec"), ns)
    return ns


def _exec_oracle(nama_fail):
    return _exec_fail(mbpg() / "testdata" / nama_fail)


def baca_nilai(pbt="MBPG"):
    if pbt == "MBPG":
        n = _exec_oracle("oracle_n001.py")
        pk = _exec_oracle("oracle_pk.py")
        return {
            "N-001": dict(n["SEMUA"]),
            "P-001": dict(pk["P001"]),
            "K-001": dict(pk["K001"]),
        }
    # MBIP: excel_data.py (TC_DATA) + trafik_v2.py (TRAFIK_V2 menimpa
    # K-001 pada waktu ujian — jadi paparan gabung kedua-duanya).
    td = suite_path("MBIP") / "testdata"
    ed = _exec_fail(td / "excel_data.py")
    tv = _exec_fail(td / "trafik_v2.py")
    tc = ed["TC_DATA"]
    return {
        "N-001": dict(tc["MBIP-TC-N-001"]),
        "P-001": dict(tc["MBIP-TC-P-001"]),
        "K-001": {**tc["MBIP-TC-K-001"], **tv["TRAFIK_V2"]},
    }


def baca_pokok(pbt="MBPG"):
    calon = sorted((suite_path(pbt) / "testdata" / "mapping")
                   .glob("POKOK-SAH-PRODUCTION-*.json"))
    if not calon:
        return {"pokok": []}
    return json.loads(calon[-1].read_text(encoding="utf-8"))


def _padan_ci(a, b):
    """Padanan gaya dropdown app: tak peka huruf, substring dua hala."""
    a = str(a or "").strip().casefold()
    b = str(b or "").strip().casefold()
    return bool(a) and bool(b) and (a == b or a in b or b in a)


def sah_rantaian(nilai, pokok):
    """Pulangkan senarai ralat validasi rantaian dropdown ([] = sah).
    Padanan tak peka huruf + substring dua hala (perangai live-search
    app disahkan pada peranti; DB MBIP simpan sesetengah teks huruf
    kecil). kesalahan None/kosong = 'pilih baris pertama' — dilangkau."""
    ralat = []
    kompaun = str(nilai.get("keterangan_kod_kompaun", "") or "").strip()
    akta = str(nilai.get("kod_akta", "") or "").strip()
    kes_mentah = nilai.get("kesalahan_kompaun")
    kes = "" if kes_mentah in (None, "None") else \
        str(kes_mentah).strip().rstrip(" .,;:")
    node = next((p for p in pokok
                 if str(p["kompaun"]).strip().casefold()
                 == kompaun.casefold()), None) \
        or next((p for p in pokok if _padan_ci(p["kompaun"], kompaun)),
                None)
    if node is None:
        ralat.append(f"kompaun {kompaun!r} TIADA dalam pokok production")
        return ralat
    # DB boleh ada akta seakan sama (cth. 'UUK 7 UNDANG-UNDANG KECIL
    # TAMAN...' dan 'UNDANG-UNDANG KECIL TAMAN...') — padanan tepat
    # diutamakan, dan kesalahan disemak merentas SEMUA akta yang padan
    # (pengguna app akan pilih baris yang betul dari senarai).
    calon = [a for a in node["akta"] if _padan_ci(a["akta"], akta)]
    calon.sort(key=lambda a: 0 if str(a["akta"]).strip().casefold()
               == akta.casefold() else 1)
    if not calon:
        sah = [a["akta"] for a in node["akta"]]
        ralat.append(f"akta {akta!r} tiada di bawah {node['kompaun']!r}. "
                     f"Pilihan sah: {sah}")
        return ralat
    if kes and not any(
            _padan_ci(str(k["kesalahan"]).rstrip(" .,;:"), kes)
            for a in calon for k in a["kesalahan"]):
        npil = sum(a["bil_kesalahan"] for a in calon)
        ralat.append(f"kesalahan {kes[:60]!r}... tiada di bawah akta "
                     f"{calon[0]['akta']!r} ({npil} pilihan)")
    return ralat


def _backup(p):
    bdir = p.parent / "_backup_terminal"
    bdir.mkdir(exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    (bdir / f"{p.name}.{ts}.bak").write_text(
        p.read_text(encoding="utf-8"), encoding="utf-8")
    return bdir


def _buang_blok(teks):
    pat = re.compile(re.escape(MARK_MULA) + r".*?" + re.escape(MARK_TAMAT)
                     + r"\n?", re.S)
    return pat.sub("", teks).rstrip() + "\n\n"


def _blok_override(var, override, subdik=None):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris = [MARK_MULA,
             f"# Dijana {ts} oleh terminal ganti-nilai. Baris asal di atas",
             "# TIDAK diubah; padam blok ini untuk kembali kepada asal.",
             "_TERMINAL_OVERRIDE = " + json.dumps(override, ensure_ascii=False,
                                                  indent=4),
             f"{var}.update(_TERMINAL_OVERRIDE)"]
    for s in (subdik or []):
        baris.append(f"{s}.update({{k: v for k, v in "
                     f"_TERMINAL_OVERRIDE.items() if k in {s}}})")
    baris.append(MARK_TAMAT)
    return "\n".join(baris) + "\n"


def _tulis_override(nama_fail, var, override, subdik=None):
    p = mbpg() / "testdata" / nama_fail
    teks = p.read_text(encoding="utf-8")
    bdir = _backup(p)                                        # noqa: F841
    teks = _buang_blok(teks)
    if override:
        teks += _blok_override(var, override, subdik)
    p.write_text(teks, encoding="utf-8")


def _jana_mbpg(ringkasan):
    n_over = ringkasan.get("N-001") or {}
    _tulis_override("oracle_n001.py", "SEMUA", n_over,
                    subdik=["PESALAH", "NOTIS", "PENERIMA"])
    p_over = ringkasan.get("P-001") or {}
    k_over = ringkasan.get("K-001") or {}
    # oracle_pk: dua dict dalam satu fail — satu blok, dua update.
    p_fail = mbpg() / "testdata" / "oracle_pk.py"
    teks = p_fail.read_text(encoding="utf-8")
    bdir = _backup(p_fail)
    teks = _buang_blok(teks)
    if p_over or k_over:
        ts2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blok = [MARK_MULA,
                f"# Dijana {ts2} oleh terminal ganti-nilai.",
                "_TERMINAL_OVERRIDE_P = " + json.dumps(
                    p_over, ensure_ascii=False, indent=4),
                "P001.update(_TERMINAL_OVERRIDE_P)",
                "_TERMINAL_OVERRIDE_K = " + json.dumps(
                    k_over, ensure_ascii=False, indent=4),
                "K001.update(_TERMINAL_OVERRIDE_K)",
                MARK_TAMAT]
        teks += "\n".join(blok) + "\n"
    p_fail.write_text(teks, encoding="utf-8")
    return bdir


def _jana_mbip(ringkasan):
    """MBIP v3: N/P -> excel_data.py (TC_DATA[...]); K -> trafik_v2.py
    (TRAFIK_V2 — ia menimpa TC_DATA K-001 pada waktu ujian, jadi
    SEMUA override K diletak di sini supaya sentiasa menang)."""
    td = suite_path("MBIP") / "testdata"
    n_over = ringkasan.get("N-001") or {}
    p_over = ringkasan.get("P-001") or {}
    k_over = ringkasan.get("K-001") or {}

    ed = td / "excel_data.py"
    teks = _buang_blok(ed.read_text(encoding="utf-8"))
    bdir = _backup(ed)
    if n_over or p_over:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blok = [MARK_MULA,
                f"# Dijana {ts} oleh terminal ganti-nilai (Laporan "
                f"Berpusat). Baris asal di atas TIDAK diubah;",
                "# padam blok ini untuk kembali kepada asal. Jalankan "
                "tools/check_vs_excel.py untuk melihat",
                "# medan mana yang kini menyimpang daripada Excel "
                "(sengaja — keputusan pengguna terminal).",
                "_TERMINAL_OVERRIDE_N = " + json.dumps(
                    n_over, ensure_ascii=False, indent=4),
                'TC_DATA["MBIP-TC-N-001"].update(_TERMINAL_OVERRIDE_N)',
                "_TERMINAL_OVERRIDE_P = " + json.dumps(
                    p_over, ensure_ascii=False, indent=4),
                'TC_DATA["MBIP-TC-P-001"].update(_TERMINAL_OVERRIDE_P)',
                MARK_TAMAT]
        teks += "\n".join(blok) + "\n"
    ed.write_text(teks, encoding="utf-8")

    tv = td / "trafik_v2.py"
    teks = _buang_blok(tv.read_text(encoding="utf-8"))
    _backup(tv)
    if k_over:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blok = [MARK_MULA,
                f"# Dijana {ts} oleh terminal ganti-nilai. TRAFIK_V2 "
                f"menimpa TC_DATA K-001 pada waktu",
                "# ujian, jadi override K diletak di sini supaya "
                "sentiasa menang. Padam blok untuk asal.",
                "_TERMINAL_OVERRIDE_K = " + json.dumps(
                    k_over, ensure_ascii=False, indent=4),
                "TRAFIK_V2.update(_TERMINAL_OVERRIDE_K)",
                MARK_TAMAT]
        teks += "\n".join(blok) + "\n"
    tv.write_text(teks, encoding="utf-8")
    return bdir


def jana(perubahan, pbt="MBPG"):
    """perubahan = {"N-001": {medan: nilai}, ...} — hanya medan yang
    BERBEZA daripada nilai semasa ditulis. Pulangkan ringkasan."""
    if pbt not in TERMINAL_PBT:
        return {"ok": False,
                "ralat": {"pbt": [f"{pbt} belum disambung"]}}
    semasa = baca_nilai(pbt)
    pokok = baca_pokok(pbt).get("pokok", [])
    ringkasan, ralat_semua = {}, {}
    for borang in ("N-001", "P-001", "K-001"):
        baru = dict(perubahan.get(borang) or {})
        beza = {k: v for k, v in baru.items()
                if k in semasa[borang] and str(v) != str(semasa[borang][k])}
        # validasi rantaian: gabung nilai semasa + perubahan
        gabung = {**semasa[borang], **beza}
        r = sah_rantaian(gabung, pokok)
        if r:
            ralat_semua[borang] = r
            continue
        ringkasan[borang] = beza
    if ralat_semua:
        return {"ok": False, "ralat": ralat_semua}
    bdir = _jana_mbpg(ringkasan) if pbt == "MBPG" \
        else _jana_mbip(ringkasan)
    # sahkan fail masih valid python + nilai terpakai
    selepas = baca_nilai(pbt)
    return {"ok": True, "diubah": ringkasan,
            "backup": str(bdir),
            "sah_selepas": all(
                str(selepas[b][k]) == str(v)
                for b, d in ringkasan.items() for k, v in d.items())}


# -------------------------------------------------------------------- AI --
def ai_test():
    a = ai_cfg()
    if not a.get("base_url") or not a.get("api_key"):
        return {"ok": False, "mesej": "base URL / API key belum diisi"}
    url = a["base_url"].rstrip("/") + "/models"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + a["api_key"]})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        n = len(data.get("data", data if isinstance(data, list) else []))
        return {"ok": True, "mesej": f"Sambungan OK — {n} model tersedia"}
    except urllib.error.HTTPError as e:
        return {"ok": False, "mesej": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:                                    # noqa: BLE001
        return {"ok": False, "mesej": f"{type(e).__name__}: {e}"}


def ai_cadang(borang, medan, nilai_semasa):
    a = ai_cfg()
    if not a.get("base_url") or not a.get("api_key"):
        return {"ok": False, "mesej": "base URL / API key belum diisi"}
    url = a["base_url"].rstrip("/") + "/chat/completions"
    prompt = (f"Konteks: skrip ujian e2e app penguatkuasaan PBT Malaysia. "
              f"Borang {borang}, medan '{medan}', nilai semasa "
              f"'{nilai_semasa}'. Cadangkan SATU nilai ujian alternatif "
              f"yang realistik dan selamat (data ujian, bukan PII sebenar). "
              f"Jawab nilai itu SAHAJA, tiada penjelasan.")
    body = json.dumps({"model": a.get("model", MODELS[0]),
                       "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 100}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": "Bearer " + a["api_key"],
        "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        teks = data["choices"][0]["message"]["content"].strip()
        return {"ok": True, "cadangan": teks[:200]}
    except Exception as e:                                    # noqa: BLE001
        return {"ok": False, "mesej": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------- muat turun --
# Folder/fail yang TIDAK dimasukkan dalam zip skrip (cache, dump besar,
# artifak binaan — bukan sebahagian skrip).
SKRIP_ABAI_DIR = {"__pycache__", ".git", "node_modules", "ui_dumps",
                  "_backup_terminal", ".pytest_cache", "public", "data"}
# Imej/screenshot dikecualikan: zip skrip = KOD sahaja. Cloudflare Pages
# tolak mana-mana fail >25 MiB (MBPG-skrip.zip cecah 40MB kerana PNG
# forensik/e2e-screenshots -> wrangler deploy abort, 2026-10-02).
SKRIP_ABAI_EXT = {".apk", ".zip", ".bak", ".pyc", ".db",
                  ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4"}
SKRIP_HAD_SAIZ = 10 * 1024 * 1024      # >10MB per fail: langkau


def zip_skrip(pbt):
    """Zip suite penuh PBT (in-memory) — skrip, testdata, tools, docs.
    PERINGATAN: testdata mengandungi kredential ujian PBT; zip ini
    untuk kegunaan dalaman pemilik sahaja (server terikat 127.0.0.1)."""
    import io
    import zipfile
    root = suite_path(pbt)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(root.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(root)
            if any(bhg in SKRIP_ABAI_DIR for bhg in rel.parts):
                continue
            if f.suffix.lower() in SKRIP_ABAI_EXT:
                continue
            try:
                if f.stat().st_size > SKRIP_HAD_SAIZ:
                    continue
            except OSError:
                continue
            z.write(f, f"{pbt}-skrip/{rel.as_posix()}")
    return buf.getvalue()


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def collect():
    manifest = _read(DATA / "manifest.json") or {"pbt": []}
    keluar = {"manifest": manifest, "runs": {}}
    for p in manifest.get("pbt", []):
        kod = p.get("kod")
        runs = []
        folder = DATA / kod / "runs"
        if folder.is_dir():
            for f in sorted(folder.glob("*.json")):
                d = _read(f)
                if isinstance(d, dict):
                    runs.append(d)
        runs.sort(key=lambda r: str(r.get("generated_at", "")), reverse=True)
        keluar["runs"][kod] = runs
    # Rekod production — senarai rekod HIDUP untuk pembatalan PM (tab baharu).
    keluar["rekod"] = {}
    for p in manifest.get("pbt", []):
        f = DATA / p.get("kod") / "rekod.json"
        d = _read(f)
        if isinstance(d, dict):
            keluar["rekod"][p.get("kod")] = d
    return keluar


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def do_POST(self):
        try:
            b = self._body()
            if self.path == "/api/terminal/jana":
                self._send(200, json.dumps(
                    jana(b.get("perubahan") or {},
                         pbt=str(b.get("pbt") or "MBPG")),
                    ensure_ascii=False).encode("utf-8"),
                    "application/json")
            elif self.path == "/api/terminal/ai_config":
                a = ai_cfg()
                for k in ("base_url", "model"):
                    if k in b:
                        a[k] = str(b[k]).strip()
                if b.get("api_key"):
                    a["api_key"] = str(b["api_key"]).strip()
                AI_PATH.write_text(json.dumps(a, indent=1))
                self._send(200, b'{"ok": true}', "application/json")
            elif self.path == "/api/terminal/ai_test":
                self._send(200, json.dumps(ai_test()).encode("utf-8"),
                           "application/json")
            elif self.path == "/api/terminal/ai_cadang":
                self._send(200, json.dumps(
                    ai_cadang(b.get("borang"), b.get("medan"),
                              b.get("nilai", ""))).encode("utf-8"),
                           "application/json")
            else:
                self._send(404, b"not found", "text/plain")
        except Exception as e:
            self._send(500, json.dumps(
                {"ralat": f"{type(e).__name__}: {e}"}).encode("utf-8"),
                "application/json")

    def do_GET(self):
        if self.path.startswith("/api/terminal/data"):
            try:
                q = urllib.parse.parse_qs(
                    urllib.parse.urlsplit(self.path).query)
                pbt = (q.get("pbt") or ["MBPG"])[0].upper()
                if pbt not in TERMINAL_PBT:
                    self._send(400, json.dumps(
                        {"ralat": f"{pbt} belum disambung"}).encode("utf-8"),
                        "application/json")
                    return
                a = ai_cfg()
                out = {"pbt": pbt, "suite_path": str(suite_path(pbt)),
                       "mbpg_path": str(mbpg()),
                       "borang": baca_nilai(pbt),
                       "pokok": baca_pokok(pbt).get("pokok", []),
                       "models": MODELS,
                       "ai": {"base_url": a.get("base_url", ""),
                              "model": a.get("model", MODELS[0]),
                              "key_set": bool(a.get("api_key"))}}
                self._send(200, json.dumps(out, ensure_ascii=False,
                                           default=str)
                           .encode("utf-8"), "application/json")
            except Exception as e:
                self._send(500, json.dumps(
                    {"ralat": f"{type(e).__name__}: {e}"}).encode("utf-8"),
                    "application/json")
        elif self.path.startswith("/api/skrip/"):
            try:
                pbt = self.path.rsplit("/", 1)[-1].split("?")[0].upper()
                if pbt not in TERMINAL_PBT:
                    self._send(404, f"{pbt} tiada".encode("utf-8"),
                               "text/plain")
                    return
                data = zip_skrip(pbt)
                ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
                nama = f"{pbt}-skrip-{ts}.zip"
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{nama}"')
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self._send(500, json.dumps(
                    {"ralat": f"{type(e).__name__}: {e}"}).encode("utf-8"),
                    "application/json")
        elif self.path.startswith("/manual/"):
            # PDF manual statik: laporan/manual/MANUAL-USER-<PBT>.pdf
            nama = Path(self.path.split("?")[0]).name
            f = HERE / "manual" / nama
            if nama.lower().endswith(".pdf") and f.is_file():
                data = f.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{nama}"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self._send(404, b"manual tiada", "text/plain")
        elif self.path.startswith("/api/data"):
            self._send(200, json.dumps(collect()).encode("utf-8"),
                       "application/json")
        elif self.path in ("/", "/index.html"):
            f = HERE / "index.html"
            if f.is_file():
                self._send(200, f.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(404, b"index.html not found", "text/plain")
        else:
            self._send(404, b"not found", "text/plain")

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8898)
    args = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Laporan Berpusat di http://localhost:{args.port}  (Ctrl+C untuk henti)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
