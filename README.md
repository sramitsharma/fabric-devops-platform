# Fabric Multi-Tenant DevOps Platform — Reference Implementation

Production-grade, zero-trust, multi-tenant pipeline for Microsoft Fabric +
Azure Event Hubs → S3, built on GitLab CI, Terraform, ArgoCD, **fabric-cicd**
and **Fabric Variable Libraries**.

## Repository Map

| Path | Role |
|------|------|
| `ci-templates/` | Versioned GitLab CI template library — the ONLY place pipeline logic lives (DRY). Consumers pin a tag (`ref: v3.0.0`). |
| `ci-templates/policy/` | OPA/Rego rules gating every `terraform plan` (T1). |
| `fabric-artifacts/` | Fabric items in Git-integration format + `deploy/deploy.py` (fabric-cicd driver) + `parameter.yml` + `Platform.VariableLibrary` with per-env value sets. |
| `streaming-replicator/` | Spark Structured Streaming EH→S3 app: source, hardened Dockerfile, Helm chart (SparkApplication CRD). |
| `infra-terraform/` | Modules + env dirs. Reads `tenants.yaml` via `yamldecode` → `for_each`. |
| `gitops/` | ArgoCD ApplicationSet (matrix: tenants × envs) + Kyverno zero-trust policies. |
| `tenant-registry/tenants.yaml` | **Single source of truth.** Onboarding a tenant = one reviewed MR here. Terraform, fabric-cicd and ArgoCD all fan out from it. |

## How each requirement is met

**DRY / modular / reusable** — consumer `.gitlab-ci.yml` files are ~12 lines of
`include:`. All stages, gates, auth and scanners live once in `ci-templates`,
versioned and upgraded by MR. Hidden jobs (`.oidc-azure`, `.env-*`, `.tf-*`,
`.fabric-deploy`) compose via `extends`, never copy-paste.

**Environments** — dev/test/preprod/prod as GitLab environments mapped to
separate subscriptions/capacities. Identical artifacts promote through them;
only Variable Library value sets, `parameter.yml` blocks and tfvars differ.
`preprod` and `prod` are Protected Environments with required approvers
(tollgates T4/T5) — approval is enforced by GitLab, not by convention.

**Zero trust** —
- CI→Azure: OIDC workload identity federation (`id_tokens`), no stored secrets;
  fabric-cicd authenticates with `ClientAssertionCredential` from the CI JWT.
- Runtime: per-tenant Kubernetes service accounts with Azure Workload Identity;
  Event Hubs `local_authentication_enabled = false` (Entra-only, no SAS).
- Supply chain: Kaniko reproducible builds, digest-pinned deploys, Syft SBOM,
  cosign keyless signing, Kyverno `verifyImages` refuses unsigned pods.
- Network: private endpoints, default-deny NetworkPolicy generated per namespace.

**Vulnerability-free as a gate (T1)** — gitleaks, Semgrep SAST, Trivy fs+image
(HIGH/CRITICAL → fail), Checkov IaC scan, Conftest/OPA on plan JSON. All blocking.

**Multi-tenancy** — hub-per-tenant (dedicated namespace for premium tier),
namespace-per-tenant on AKS with quotas + default-deny, prefix-per-tenant on S3,
workspace-per-tenant Gold in Fabric. All stamped from `tenants.yaml`.

**Fabric deployment (the two additions)** —
- `fabric-cicd` publishes items and prunes orphans (`unpublish_all_orphan_items`)
  so each workspace mirrors Git exactly — drift is impossible by construction.
- `Platform.VariableLibrary` holds env-specific values (S3 endpoints, EH
  namespaces, thresholds); `valueSets/{test,preprod,prod}.json` activate per
  stage. `parameter.yml` covers only workspace-scoped GUIDs.
- `deploy/verify.py` (T2) executes a smoke notebook via the Fabric Job
  Scheduler API in every workspace and fails the pipeline on anything but
  `Completed` — deployments are verified, never assumed.

## Tollgate map (enforced in `base.yml` stages + protected envs)
T0 MR gate → T1 security (all blocking) → deploy DEV → T2 smoke verify →
deploy TEST → T3 Soda DQ gate → T4 PREPROD (perf/soak + manual) →
T5 PROD (named approvers, release tags only) → T6 post-deploy SLO watch.

## One-time setup
1. Create Entra app registrations per env; add federated credentials with
   subject `project_path:data-platform/*:environment:{env}`.
2. Set protected, env-scoped CI variables: ARM_CLIENT_ID/TENANT_ID/SUBSCRIPTION_ID.
3. Mark `preprod`/`prod` as Protected Environments with approver groups.
4. Bootstrap ArgoCD app-of-apps pointing at `gitops/`; enable signature
   verification; install Kyverno + policies.
5. `terraform apply` dev first; write generated workspace IDs back into
   `tenants.yaml` via the infra pipeline's output step.
