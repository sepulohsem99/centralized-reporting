#!/usr/bin/env python3
"""JANA STATIK — bina folder public/ untuk Cloudflare Pages.

Cloudflare Pages hosting statik sahaja, jadi:
  - data run dibakar terus ke dalam index.html (tiada /api/data)
  - zip skrip PRA-JANA ke public/skrip/ (KREDENTIAL PBT di dalam —
    Cloudflare Access WAJIB dipasang, lihat SETUP-CLOUDFLARE-BERPUSAT.md)
  - PDF manual disalin ke public/manual/
  - tab Ganti Nilai dimatikan (perlu server localhost)

Guna:  python jana_statik.py     (dari folder laporan/)
Kemudian: publish.bat
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUB = HERE / "public"

# Guna fungsi sebenar serve.py (collect, zip_skrip, TERMINAL_PBT).
ns = {"__file__": str(HERE / "serve.py"), "__name__": "serve_statik"}
exec(compile((HERE / "serve.py").read_text(encoding="utf-8"),
             str(HERE / "serve.py"), "exec"), ns)


def main():
    PUB.mkdir(exist_ok=True)

    # 0) Rekod production —jana semula dari jsonl (jangan taip tangan).
    try:
        ns2 = {"__file__": str(HERE / "jana_rekod.py"), "__name__": "jana_rekod"}
        exec(compile((HERE / "jana_rekod.py").read_text(encoding="utf-8"),
                     str(HERE / "jana_rekod.py"), "exec"), ns2)
        ns2["main"]()  # noqa: E501  (fungsi dari skrip yang diexec)
    except Exception as e:                                       # noqa: BLE001
        print(f"[STATIK] AMARAN: jana_rekod.py gagal ({type(e).__name__}: {e})")

    # 1) Data run dibakar.
    data = ns["collect"]()
    # Muatkan rekod production ke dalam DATA (klik tab di papan pemuka).
    data["rekod"] = {}
    for pbt in ("MBPG", "MBIP", "MBJB"):
        f = HERE / "data" / pbt / "rekod.json"
        if f.is_file():
            try:
                data["rekod"][pbt] = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:                               # noqa: BLE001
                print(f"[STATIK] AMARAN: rekod.json {pbt} rosak ({e})")
    html = (HERE / "index.html").read_text(encoding="utf-8")

    ganti = [
        # fetch data -> data terbakar; tiada polling.
        ("const r=await fetch('/api/data',{cache:'no-store'});\n"
         "    DATA=await r.json();",
         "DATA=window.__DATA__;"),
        ("setInterval(refresh,5000); refresh();", "refresh();"),
        ("document.getElementById('feed').textContent='LIVE';",
         "document.getElementById('feed').textContent="
         "window.__STATIK__?'STATIC':'LIVE';"),
        # pautan zip -> fail statik pra-jana.
        ('href="/api/skrip/${pbt}"', 'href="skrip/${pbt}-skrip.zip"'),
        # pautan PDF -> laluan relatif.
        ('href="/manual/MANUAL-USER-${pbt}.pdf"',
         'href="manual/MANUAL-USER-${pbt}.pdf"'),
    ]
    for a, b in ganti:
        if a not in html:
            sys.exit("JANA STATIK GAGAL — corak tak jumpa: " + a[:60])
        html = html.replace(a, b)

    # Ganti Nilai perlukan server — mesej jelas pada versi statik.
    sasar = "async function renderGanti(){\n  const w=document.getElementById('gantiWrap'); if(!w) return;"
    if sasar not in html:
        sys.exit("JANA STATIK GAGAL — renderGanti tak jumpa")
    html = html.replace(sasar, sasar + "\n  if(window.__STATIK__){"
        "w.innerHTML='<div class=\"empty\">'+tr("
        "'Ganti Nilai hanya tersedia pada versi localhost "
        "(python serve.py).',"
        "'Replace Values is only available on the localhost version "
        "(python serve.py).')+'</div>';return;}")

    # Suntik data sebelum skrip utama.
    suntik = ("<script>window.__STATIK__=true;window.__DATA__="
              + json.dumps(data, ensure_ascii=False) + ";</script>\n<script>")
    html = html.replace("<script>", suntik, 1)
    (PUB / "index.html").write_text(html, encoding="utf-8")
    print(f"[STATIK] index.html ({len(html):,} aksara, "
          f"{sum(len(v) for v in data['runs'].values())} run)")

    # 2) Zip skrip pra-jana (KREDENTIAL — mesti di sebalik Access).
    (PUB / "skrip").mkdir(exist_ok=True)
    for pbt in ns["TERMINAL_PBT"]:
        try:
            z = ns["zip_skrip"](pbt)
            (PUB / "skrip" / f"{pbt}-skrip.zip").write_bytes(z)
            print(f"[STATIK] skrip/{pbt}-skrip.zip "
                  f"({len(z)/1024/1024:.1f} MB)")
        except Exception as e:                               # noqa: BLE001
            print(f"[STATIK] AMARAN: zip {pbt} gagal "
                  f"({type(e).__name__}: {e}) — dilangkau")

    # 3) PDF manual.
    (PUB / "manual").mkdir(exist_ok=True)
    for f in (HERE / "manual").glob("*.pdf"):
        shutil.copy2(f, PUB / "manual" / f.name)
        print(f"[STATIK] manual/{f.name}")

    # 4) _headers — jangan diindeks enjin carian.
    (PUB / "_headers").write_text(
        "/*\n  X-Robots-Tag: noindex\n", encoding="utf-8")
    print("[STATIK] _headers (noindex)")

    # 5) Bukti tangkapan skrin kegagalan — disalin untuk tab Gap Analysis.
    #    Gambar diambil automasi pada saat peringkat GAGAL; tanpa langkah
    #    ini ia tinggal di mesin ujian dan tab itu hanya menunjuk laluan
    #    mati.
    SRC_BUKTI = HERE / "bukti"
    if SRC_BUKTI.is_dir():
        # Kosongkan dahulu — kalau tidak, gambar lama yang telah ditukar nama
        # akan terus hidup dalam public/ dan menyesatkan (fail bertindih).
        # FIX#24(b): terima .png DAN .jpg — tangkapan bukti baharu ditukar
        # ke JPEG (kualiti 78) supaya halaman kekal ringan; corak *.png
        # sahaja bermakna ia tidak pernah sampai ke public/ dan tab
        # padanan menunjuk gambar yang tiada.
        dst = PUB / "bukti"
        dst.mkdir(exist_ok=True)
        corak = ("*.png", "*.jpg", "*.jpeg")
        if dst.is_dir():
            for pat in corak:
                for old in dst.glob(pat):
                    old.unlink()
        n = 0
        for pat in corak:
            for f in sorted(SRC_BUKTI.glob(pat)):
                shutil.copy2(f, dst / f.name)
                n += 1
        print(f"[STATIK] bukti/ ({n} gambar)")
    else:
        print("[STATIK] AMARAN: folder bukti/ tiada — tab Gap Analysis "
              "akan tunjuk 'tiada bukti'")

    print("[STATIK] SIAP -> public/  |  seterusnya: publish.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
