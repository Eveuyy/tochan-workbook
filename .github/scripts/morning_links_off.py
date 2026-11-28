#!/usr/bin/env python3
"""Deactivates the Black Friday payment links in Morning (status 20) at the end of the sale.
Credentials come from the environment (GitHub secrets MORNING_ID / MORNING_SECRET), never from the repo.
Idempotent: a link that is already off stays off. Exits non-zero if a link could not be verified off."""
import json, os, sys, urllib.request

LINKS = {
    "course 756": "8078e0f5-8532-4b8e-aefd-9b9a5fa79672",
    "bundle 952": "5b225043-c562-4509-a48a-79ad7a75f723",
}
API = "https://api.greeninvoice.co.il/api/v1"


def call(method, path, body=None, tok=None):
    h = {"content-type": "application/json"}
    if tok:
        h["authorization"] = "Bearer " + tok
    req = urllib.request.Request(API + path if path.startswith("/") else path, data=json.dumps(body).encode() if body is not None else None, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as f:
            return f.status, json.load(f)
    except urllib.error.HTTPError as e:
        return e.code, {}


def main():
    cid, sec = os.environ.get("MORNING_ID", ""), os.environ.get("MORNING_SECRET", "")
    if not cid or not sec:
        print("morning_links_off: MORNING_ID / MORNING_SECRET not set in the repo secrets, links NOT turned off (turn them off in Morning by hand)")
        return
    st, t = call("POST", "https://api.morning.co/idp/v1/oauth/token", {"grant_type": "client_credentials", "client_id": cid, "client_secret": sec})
    tok = t.get("accessToken")
    if not tok:
        sys.exit(f"morning_links_off: token failed ({st})")
    bad = []
    check_only = "--check" in sys.argv
    for name, lid in LINKS.items():
        st, l = call("GET", f"/payments/links/{lid}", None, tok)
        if check_only:
            print(name, "status", l.get("status"), "price", l.get("price")); continue
        if st == 200 and l.get("status") == 20:
            print(name, "already off"); continue
        call("PUT", f"/payments/links/{lid}", {"status": 20}, tok)
        st, l = call("GET", f"/payments/links/{lid}", None, tok)
        ok = st == 200 and l.get("status") == 20
        print(name, "off" if ok else "STILL ON")
        if not ok:
            bad.append(name)
    if bad:
        sys.exit("morning_links_off: not off: " + ", ".join(bad))


if __name__ == "__main__":
    main()
