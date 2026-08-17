"""fabric-cicd deployment driver.
Deploys the source-controlled workspace folder to the correct Fabric
workspace(s) for the target environment — including per-tenant Gold
workspaces resolved from the tenant registry. Zero secrets: authenticates
with GitLab's OIDC token via Entra Workload Identity Federation.
"""
import argparse, os, yaml
from azure.identity import ClientAssertionCredential
from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items


def credential() -> ClientAssertionCredential:
    def assertion() -> str:
        with open("/tmp/fed_token") as f:
            return f.read().strip()
    return ClientAssertionCredential(
        tenant_id=os.environ["ARM_TENANT_ID"],
        client_id=os.environ["ARM_CLIENT_ID"],
        func=assertion,
    )


def deploy(workspace_id: str, env: str, repo_dir: str, item_types: list[str], cred) -> None:
    ws = FabricWorkspace(
        workspace_id=workspace_id,
        environment=env,                # selects blocks in parameter.yml AND the
        repository_directory=repo_dir,  # Variable Library value set to activate
        item_type_in_scope=item_types,
        token_credential=cred,
    )
    publish_all_items(ws)
    unpublish_all_orphan_items(ws)      # workspace mirrors git exactly — no drift


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--environment", required=True)
    p.add_argument("--repo-dir", required=True)
    p.add_argument("--item-types", required=True)
    p.add_argument("--tenant-registry", required=True)
    a = p.parse_args()

    cred = credential()
    items = a.item_types.split(",")
    registry = yaml.safe_load(open(a.tenant_registry))

    # 1) shared platform workspace (Bronze/Silver) for this env
    deploy(registry["platform_workspaces"][a.environment], a.environment, a.repo_dir, items, cred)

    # 2) per-tenant Gold workspaces — same artifacts, tenant-scoped config
    for t in registry["tenants"]:
        if a.environment in t["envs"]:
            deploy(t["gold_workspaces"][a.environment], a.environment, a.repo_dir, items, cred)


if __name__ == "__main__":
    main()
