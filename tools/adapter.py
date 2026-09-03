#!/usr/bin/env python3
"""Penyesuai laporan berpusat — tukar output setiap PBT ke skema sepunya.

Skema sepunya (satu fail = satu larian):
{
  "id": "<pbt>-<env>-<timestamp>",
  "pbt": "MBPG", "env": "production", "app_version": "2.1.23",
  "generated_at": "...", "tester": "...", "device_model": "...",
  "duration_seconds": 0.0,
  "summary": {"passed": 0, "failed": 0, "skipped": 0, "lain": 0},
  "results": {"<TC>": {"status": "...", "nama": "", "sebab": ""}},
  "sumber": "path asal"
}

Status dinormalkan: PASSED / FAILED / SKIPPED / NO_EVIDENCE / NEEDS_EYE /
ERROR / NOT_RUN.

Guna:
  python adapter.py --history <fail.json> --out <dir>          # MBIP/MBJB
  python adapter.py --mbpg-html <LAPORAN.html> --out <dir>     # MBPG
"""
import argparse
import html as html_mod
import json
import os
import re

STATUS_MAP = {
    "PASSED": "PASSED", "LULUS": "PASSED",
    "FAILED": "FAILED", "GAGAL": "FAILED",
    "SKIPPED": "SKIPPED", "TIDAK DIUJI": "SKIPPED", "DILANGKAU": "SKIPPED",
    "TIADA BUKTI": "NO_EVIDENCE",
    "PERLU-MATA": "NEEDS_EYE", "PERLU MATA": "NEEDS_EYE",
    "ERROR": "ERROR", "NOT_RUN": "NOT_RUN", "GAGAL-AWAL": "FAILED",
}


def norm_status(s):
    return STATUS_MAP.get(str(s).strip().upper(), str(s).strip().upper())


def ringkas(results):
    r = {"passed": 0, "failed": 0, "skipped": 0, "lain": 0}
    for v in results.values():
        st = v["status"]
        if st == "PASSED":
            r["passed"] += 1
        elif st in ("FAILED", "ERROR"):
            r["failed"] += 1
        elif st == "SKIPPED":
            r["skipped"] += 1
        else:
            r["lain"] += 1
    return r


def dari_history(path):
    """MBIP / MBJB history JSON -> skema sepunya."""
    d = json.load(open(path, encoding="utf-8"))
    reasons = d.get("reasons") or {}
    results = {}
    for tc, st in (d.get("results") or {}).items():
        results[tc] = {"status": norm_status(st), "nama": "",
                       "sebab": str(reasons.get(tc, ""))[:300]}
    ts = str(d.get("generated_at", "")).replace(":", "-")
    return {
        "id": f"{d.get('pbt', '?').lower()}-{d.get('env', '?')}-{ts}",
        "pbt": d.get("pbt"), "env": d.get("env"),
        "app_version": d.get("app_version"),
        "generated_at": d.get("generated_at"),
        "tester": d.get("tester"), "device_model": d.get("device_model"),
        "duration_seconds": d.get("duration_seconds"),
        "summary": ringkas(results), "results": results,
        "sumber": os.path.basename(path),
    }


def dari_mbpg_html(path):
    """LAPORAN-LARIAN-*.html MBPG -> skema sepunya.

    Jadual 'Status setiap TC' dibaca terus dari HTML. Regex longgar
    sengaja: sel = <td>TC</td><td>nama</td><td class=...>STATUS</td>
    <td>sebab</td>."""
    t = open(path, encoding="utf-8", errors="replace").read()
    teks = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    baris = re.findall(
        r"<tr[^>]*>\s*<td[^>]*>\s*([A-Z]{1,3}-\d{3})\s*</td>\s*"
        r"<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>",
        teks, flags=re.S)
    results = {}
    for tc, nama, st, sebab in baris:
        bersih = lambda x: html_mod.unescape(re.sub(r"<[^>]+>", "", x)).strip()
        results[f"MBPG-TC-{tc}"] = {
            "status": norm_status(bersih(st)),
            "nama": bersih(nama)[:120],
            "sebab": bersih(sebab)[:300],
        }
    m_dur = re.search(r"(\d+)m\s+(\d+)s", teks)
    dur = int(m_dur.group(1)) * 60 + int(m_dur.group(2)) if m_dur else None
    m_ver = re.search(r"MBPG\s+([\d.]+)", teks)
    m_tarikh = re.search(r"Larian\s+(\d{4}-\d{2}-\d{2}),\s*([\d:]+)", teks)
    gen = (f"{m_tarikh.group(1)}T{m_tarikh.group(2)}"
           if m_tarikh else "")
    return {
        "id": f"mbpg-production-{gen.replace(':', '-') or 'tanpa-tarikh'}",
        "pbt": "MBPG", "env": "production",
        "app_version": m_ver.group(1) if m_ver else None,
        "generated_at": gen, "tester": "mrsai",
        "device_model": "Ulefone Armor 27",
        "duration_seconds": dur,
        "summary": ringkas(results), "results": results,
        "sumber": os.path.basename(path),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", nargs="*", default=[])
    ap.add_argument("--mbpg-html", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    for p in a.history:
        d = dari_history(p)
        tulis(d, a.out)
    for p in a.mbpg_html:
        d = dari_mbpg_html(p)
        tulis(d, a.out)


def tulis(d, out_root):
    folder = os.path.join(out_root, d["pbt"], "runs")
    os.makedirs(folder, exist_ok=True)
    laluan = os.path.join(folder, d["id"] + ".json")
    with open(laluan, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    s = d["summary"]
    print(f"  {d['pbt']:<5} {d['generated_at']}: {len(d['results'])} TC "
          f"(P{s['passed']}/F{s['failed']}/S{s['skipped']}/L{s['lain']}) "
          f"-> {laluan}")


if __name__ == "__main__":
    main()
