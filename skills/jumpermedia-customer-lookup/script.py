"""jumpermedia-customer-lookup — check Xano for returning/current customer status."""
import json
import os
import sys

import httpx


def main() -> None:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    base_url = (os.environ.get("JUMPERMEDIA_XANO_BASE_URL") or "").rstrip("/")
    auth_token = (os.environ.get("JUMPERMEDIA_XANO_AUTH_TOKEN") or "").strip()

    if not base_url:
        print(json.dumps({
            "ok": False,
            "error": "JUMPERMEDIA_XANO_BASE_URL not set. Attach via: oya agent skills update <agent_id> jumpermedia-customer-lookup --credentials-json '{\"JUMPERMEDIA_XANO_BASE_URL\":\"https://...\",\"JUMPERMEDIA_XANO_AUTH_TOKEN\":\"...\"}'",
        }))
        sys.exit(1)

    gmb_name = (inp.get("gmb_name") or "").strip()
    gmb_address = (inp.get("gmb_address") or "").strip()
    email = (inp.get("email") or "").strip()

    if not (gmb_name or email):
        print(json.dumps({
            "ok": False,
            "error": "Pass at least one of gmb_name or email.",
        }))
        sys.exit(1)

    payload = {
        "gmb_name": gmb_name,
        "gmb_address": gmb_address,
        "email": email,
    }

    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    url = f"{base_url}/customer-lookup"

    try:
        with httpx.Client(timeout=20) as client:
            r = client.post(url, json=payload, headers=headers)
        if r.status_code == 404:
            print(json.dumps({
                "ok": True,
                "found": False,
                "status": "none",
                "user": None,
            }))
            return
        if r.status_code >= 400:
            print(json.dumps({
                "ok": False,
                "error": f"Xano returned {r.status_code}",
                "details": r.text[:500],
            }))
            sys.exit(1)
        data = r.json() if r.text else {}

        found = bool(data.get("found", data.get("user") is not None))
        sub_status = (data.get("subscription_status") or data.get("status") or "").lower().strip()

        if not found or sub_status in ("", "none", "never"):
            status = "none"
        elif sub_status in ("active", "trial", "trialing", "paid"):
            status = "active"
        elif sub_status in ("inactive", "cancelled", "canceled", "expired", "paused", "lapsed"):
            status = "inactive"
        else:
            status = sub_status or "none"

        print(json.dumps({
            "ok": True,
            "found": found,
            "status": status,
            "user": data.get("user") or data.get("customer") or data,
        }))
    except httpx.HTTPError as e:
        print(json.dumps({"ok": False, "error": f"HTTP error: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
