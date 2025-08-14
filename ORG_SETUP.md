# Organization setup (green-hill-canarias)

Use this checklist to finish moving work into your org and enable bigger Codespaces for ingestion while keeping serve small.

## Links

- Org Codespaces billing: <https://github.com/organizations/green-hill-canarias/settings/codespaces>
- Org Codespaces secrets: <https://github.com/organizations/green-hill-canarias/settings/secrets/codespaces>
- Repo (app): <https://github.com/green-hill-canarias/green-hill-app>
- Repo (digital-roots): <https://github.com/green-hill-canarias/digital-roots>

## 1) Billing and limits

- In org Codespaces settings, set a non-zero spend limit.

## 2) Machine policies (recommendation)

- Create policy "ghc-ingest" (scope: green-hill-app)
  - Allow larger machines (≥ 8 cores, ≥ 16 GB RAM) for ingestion/build.
- Create policy "ghc-serve" (scope: green-hill-app)
  - Allow small/standard machines (2–4 cores, 4–8 GB RAM) for serving/demo.
- Optional: mirror similar policies for digital-roots if needed.

## 3) Secrets

- Add org Codespaces secret: OPENAI_API_KEY
  - Scope: all repositories (or at least green-hill-app and digital-roots)

- Add org/repo secret: ORG_PROJECT_TOKEN (for automation)
  - Create a fine-grained PAT owned by an org admin with scopes: project (read/write), repo (read), issues (write), pull requests (write). Store as an org secret named ORG_PROJECT_TOKEN.

## 4) Create Codespaces (billed to org)

- App (ingestion): open green-hill-app → Code → Create codespace on main → pick the large size allowed by policy.
- App (serve): create another codespace on main → pick the small/standard size.
- Digital-roots: repeat if you plan to use Codespaces there.

## 5) After Codespaces start

- Confirm repo remote is org-owned.
- Follow the repo README quick start to run services.

## Notes

- If larger sizes don’t appear, check: (a) you billed to the organization, (b) spend limit > 0, (c) policy allows the size.
