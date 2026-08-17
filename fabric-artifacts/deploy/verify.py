#!/usr/bin/env python3
"""T2 gate: run the smoke_test notebook in every deployed workspace via the
Fabric Job Scheduler API and assert completion. Proves the deployment WORKS,
not just that it uploaded. Reads the same tenants.yaml as deploy.py (DRY)."""
import argparse, sys, time, requests, yaml
from deploy import credential   # same OIDC ClientAssertionCredential

FABRIC = "https://api.fabric.microsoft.com/v1"

def run_smoke(ws_id: str, headers: dict) -> str:
    items = requests.get(f"{FABRIC}/workspaces/{ws_id}/items?type=Notebook",
                         headers=headers, timeout=30).json().get("value", [])
    nb = next((i for i in items if i["displayName"] == "smoke_test"), None)
    if nb is None:
        return "smoke_test notebook missing"
    run = requests.post(f"{FABRIC}/workspaces/{ws_id}/items/{nb['id']}"
                        f"/jobs/instances?jobType=RunNotebook",
                        headers=headers, timeout=30)
    loc = run.headers["Location"]
    for _ in range(60):
        time.sleep(10)
        status = requests.get(loc, headers=headers, timeout=30).json().get("status")
        if status in ("Completed", "Failed", "Cancelled"):
            return "" if status == "Completed" else f"status={status}"
    return "timeout"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--environment", required=True)
    ap.add_argument("--tenant-registry", required=True)
    a = ap.parse_args()
    reg = yaml.safe_load(open(a.tenant_registry))
    tok = credential().get_token("https://api.fabric.microsoft.com/.default").token
    headers = {"Authorization": f"Bearer {tok}"}

    targets = {"platform": reg["platform_workspaces"][a.environment]}
    targets |= {t["id"]: t["gold_workspaces"][a.environment]
                for t in reg["tenants"] if a.environment in t["envs"]}

    failures = {name: err for name, ws in targets.items()
                if (err := run_smoke(ws, headers))}
    if failures:
        print(f"T2 VERIFY FAILED: {failures}"); sys.exit(1)
    print(f"T2 verify passed for: {', '.join(targets)}")

if __name__ == "__main__":
    main()
