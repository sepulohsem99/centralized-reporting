#!/usr/bin/env python3
"""PASANG CLOUDFLARE — Pages + Access untuk Laporan Berpusat.

Dijalankan di Windows pemilik (via jambatan). Baca token dari .cf_token.
1. Sahkan token.
2. Cipta projek Pages `centralized-reporting` (idempoten).
3. Deploy folder public/ (npx wrangler, direct upload).
4. Zero Trust Access: cari app MBIP sedia ada, SALIN senarai emel
   invited users, cipta app + policy sama untuk domain baharu.
Token tidak dicetak.
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

for _s in (sys.stdout, sys.stderr):      # konsol Windows cp1252 vs emoji
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                        # noqa: BLE001
        pass

LAPORAN = Path(r"C:\Users\mrsai\Desktop"
               r"\CENTRALIZED REPORTING AI CENTRIC TESTING\laporan")
AKAUN = "7f38c6d79bdbab93d66afc7cae2c7646"
PROJEK = "centralized-reporting"
DOMAIN = f"{PROJEK}.pages.dev"
API = "https://api.cloudflare.com/client/v4"

TOKEN = (LAPORAN / ".cf_token").read_text(encoding="utf-8").strip()


def api(method, path, body=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": "Bearer " + TOKEN,
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


def main():
    print("== PASANG CLOUDFLARE ==")
    v = api("GET", "/user/tokens/verify")
    if not v.get("success"):
        print("[GAGAL] token tidak sah:", v.get("errors"))
        return 1
    print("[TOKEN] sah, status:", v["result"]["status"])

    # 2) Projek Pages.
    r = api("POST", f"/accounts/{AKAUN}/pages/projects",
            {"name": PROJEK, "production_branch": "main"})
    if r.get("success"):
        print(f"[PAGES] projek {PROJEK} dicipta")
    else:
        err = (r.get("errors") or [{}])[0]
        if "already" in str(err).lower() or err.get("code") == 8000007:
            print(f"[PAGES] projek {PROJEK} sudah wujud — teruskan")
        else:
            print("[GAGAL] cipta projek:", r.get("errors"))
            return 1

    # 3) Deploy public/ melalui wrangler (direct upload).
    env = dict(os.environ,
               CLOUDFLARE_API_TOKEN=TOKEN,
               CLOUDFLARE_ACCOUNT_ID=AKAUN)
    p = subprocess.run(
        ["npx.cmd" if os.name == "nt" else "npx", "--yes", "wrangler",
         "pages", "deploy", "public", "--project-name", PROJEK,
         "--commit-dirty=true", "--branch", "main"],
        cwd=str(LAPORAN), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace")
    keluar = (p.stdout + p.stderr)
    for ln in keluar.splitlines():
        if any(k in ln for k in ("Success", "Deployment", "http", "✨",
                                 "Error", "error")):
            print("[WRANGLER]", ln.strip()[:160])
    if p.returncode != 0:
        print("[GAGAL] wrangler deploy — lihat di atas")
        return 1

    # 4) Access — salin invited users dari app MBIP.
    apps = api("GET", f"/accounts/{AKAUN}/access/apps?per_page=50")
    if not apps.get("success"):
        print("[GAGAL] senarai access apps:", apps.get("errors"))
        return 1
    senarai = apps["result"] or []
    print("[ACCESS] app sedia ada:",
          [(a.get("name"), a.get("domain")) for a in senarai])
    sumber = next((a for a in senarai
                   if "mbip" in str(a.get("domain", "")).lower()
                   or "mbip" in str(a.get("name", "")).lower()
                   or "pipeline" in str(a.get("domain", "")).lower()),
                  None)
    if sumber is None and senarai:
        sumber = senarai[0]
        print("[ACCESS] tiada app 'mbip' — guna app pertama sebagai "
              "rujukan:", sumber.get("name"))
    if sumber is None:
        print("[GAGAL] tiada app Access untuk disalin — buat manual")
        return 1

    pol = api("GET",
              f"/accounts/{AKAUN}/access/apps/{sumber['id']}/policies")
    polisi = (pol.get("result") or [])
    if not polisi:
        print("[GAGAL] app sumber tiada policy")
        return 1
    include = polisi[0].get("include") or []
    emel = [i["email"]["email"] for i in include if "email" in i]
    print(f"[ACCESS] invited users disalin dari "
          f"'{sumber.get('name')}': {emel or include}")

    # app baharu — kalau sudah wujud, langkau cipta.
    sedia = next((a for a in senarai
                  if str(a.get("domain", "")).startswith(DOMAIN)), None)
    if sedia:
        app = sedia
        print("[ACCESS] app untuk", DOMAIN, "sudah wujud")
    else:
        r = api("POST", f"/accounts/{AKAUN}/access/apps", {
            "name": "Centralized Reporting",
            "domain": DOMAIN,
            "self_hosted_domains": [DOMAIN, f"*.{DOMAIN}"],
            "type": "self_hosted",
            "session_duration": sumber.get("session_duration", "24h"),
        })
        if not r.get("success"):
            print("[GAGAL] cipta access app:", r.get("errors"))
            return 1
        app = r["result"]
        print("[ACCESS] app dicipta:", app.get("domain"))

    pol_sedia = api(
        "GET", f"/accounts/{AKAUN}/access/apps/{app['id']}/policies")
    if not (pol_sedia.get("result") or []):
        r = api("POST",
                f"/accounts/{AKAUN}/access/apps/{app['id']}/policies", {
                    "name": "invited users",
                    "decision": "allow",
                    "precedence": 1,
                    "include": include,
                })
        if not r.get("success"):
            print("[GAGAL] cipta policy:", r.get("errors"))
            return 1
        print("[ACCESS] policy allow dicipta (include disalin verbatim)")
    else:
        print("[ACCESS] policy sudah wujud — tiada perubahan")

    print(f"== SIAP: https://{DOMAIN} — hanya invited users boleh "
          f"akses ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
