#!/usr/bin/env python3
"""JANA REKOD PRODUCTION — kumpul semua rekod MBPG yang dicipta & dihantar,
kelompokkan mengikut LARIAN, tulis data/<PBT>/rekod.json untuk papan pemuka.

Sumber kebenaran (bukan taip tangan):
  MBPG-testing/reports/REKOD-SEBENAR.jsonl   no_rekod, tc, borang, masa, jenis,
                                             status, asal
  MBPG-testing/reports/E2E.jsonl             cetak_dihantar, printer, pesalah

Pengelompokan larian: baris diisih ikut masa; jurang > 90 minit bermula
larian baharu. Setiap larian dinomborkan (#1, #2, ...) supaya boleh
dirujuk sebagai '1st run', '7th run'.
"""
import json
import datetime
from collections import OrderedDict
from pathlib import Path

LAP = Path(r"C:\Users\mrsai\Desktop\CENTRALIZED REPORTING AI CENTRIC TESTING\laporan")
MBPG = Path(r"C:\Users\mrsai\Documents\antigravity\keen-lovelace\MBPG-testing")
JURANG_MIN = 90

BORANG_NAMA = {"N": "Nombor Notis", "P": "Nombor Kompaun (Pelbagai)",
               "K": "Nombor Kompaun (Letak Kereta)"}


def baca_jsonl(p):
    if not p.is_file():
        return []
    out = []
    for l in p.read_text(encoding="utf-8").splitlines():
        l = l.strip()
        if not l:
            continue
        try:
            out.append(json.loads(l))
        except Exception:                                        # noqa: BLE001
            pass
    return out


def masa(s):
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(str(s), f)
        except Exception:                                        # noqa: BLE001
            pass
    return None


def main():
    rekod = baca_jsonl(MBPG / "reports" / "REKOD-SEBENAR.jsonl")
    e2e = baca_jsonl(MBPG / "reports" / "E2E.jsonl")

    # cetak: {no_rekod: {cetak_dihantar, printer, pesalah}}
    cetak = {}
    for r in e2e:
        no = r.get("no_rekod")
        if not no:
            continue
        d = cetak.setdefault(no, {})
        if r.get("cetak_dihantar"):
            d["cetak_dihantar"] = True
        if r.get("printer"):
            d["printer"] = r["printer"]
        if r.get("cetak_disahkan_fizikal"):
            d["cetak_disahkan_fizikal"] = True
        if r.get("pesalah"):
            d["pesalah"] = r["pesalah"]

    baris = []
    for r in rekod:
        t = masa(r.get("masa"))
        if t is None:
            continue
        no = r.get("no_rekod")
        c = cetak.get(no, {}) if no else {}
        baris.append({
            "no_rekod": no,
            "tc": r.get("tc"),
            "borang": r.get("borang"),
            "jenis": r.get("jenis"),
            "masa": r.get("masa"),
            "status": r.get("status"),
            "asal": r.get("asal") or "",
            "cetak_dihantar": bool(c.get("cetak_dihantar")),
            "printer": c.get("printer", ""),
            "_t": t,
        })
    baris.sort(key=lambda x: x["_t"])

    # ---- kelompokkan kepada larian ----
    runs = []
    semasa = None
    for b in baris:
        if semasa is None or (b["_t"] - semasa["akhir"]).total_seconds() > JURANG_MIN * 60:
            semasa = {"mula": b["_t"], "akhir": b["_t"], "rekod": []}
            runs.append(semasa)
        semasa["rekod"].append(b)
        semasa["akhir"] = b["_t"]

    keluar_runs = []
    for i, r in enumerate(runs, 1):
        recs = []
        for b in r["rekod"]:
            recs.append({k: v for k, v in b.items() if k != "_t"})
        ada_nombor = [x for x in recs if x["no_rekod"]]
        keluar_runs.append({
            "no_larian": i,
            "label": f"Larian #{i}",
            "mula": r["mula"].strftime("%Y-%m-%d %H:%M"),
            "tamat": r["akhir"].strftime("%Y-%m-%d %H:%M"),
            "tarikh": r["mula"].strftime("%Y-%m-%d"),
            "bilangan": len(recs),
            "bilangan_bernombor": len(ada_nombor),
            "bilangan_cetak": sum(1 for x in recs if x["cetak_dihantar"]),
            "no_rekod": [x["no_rekod"] for x in recs if x["no_rekod"]],
            "rekod": recs,
        })

    semua_nombor = sorted({x["no_rekod"] for b in baris
                           if (x := {"no_rekod": b["no_rekod"]})["no_rekod"]})

    keluar = {
        "pbt": "MBPG",
        "dijana": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "jumlah_rekod": len(semua_nombor),
        "jumlah_baris": len(baris),
        "jumlah_larian": len(keluar_runs),
        "nota": ("Setiap rekod di bawah ialah rekod HIDUP pada production MBPG "
                 "(113.211.155.174). Semua ialah data ujian: nama pesalah bermula "
                 "'UJIAN AUTOMASI E2E' dan catatan membawa 'AUTOMASI-CLEANUP-PM'. "
                 "Baris tanpa nombor = laluan kemaskini yang tidak menghasilkan "
                 "nombor gantian (diketahui). Pembatalan melalui portal ePBT oleh "
                 "PM — automasi TIDAK memadam apa-apa."),
        "runs": keluar_runs,
        "semua_nombor": semua_nombor,
    }

    out = LAP / "data" / "MBPG" / "rekod.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(keluar, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"[OK] {out}")
    print(f"     {len(keluar_runs)} larian · {len(semua_nombor)} nombor unik · "
          f"{len(baris)} baris")
    for r in keluar_runs:
        print(f"     {r['label']:<12} {r['mula']}  {r['bilangan_bernombor']:>3} nombor "
              f"({r['bilangan']} baris, {r['bilangan_cetak']} cetak)")


if __name__ == "__main__":
    main()
