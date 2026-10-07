# Threat model and operating controls

Assets: original documents, questions, plaintext chunks, embeddings and model outputs.
Trusted boundary: one user's machine, owned input folder, trusted installed runtime and
local Ollama service. Multiuser access and hostile local administrators are out of scope.

| Threat | Implemented control | Remaining work/limit |
| --- | --- | --- |
| External endpoint/proxy/redirect | Literal loopback validation, no proxy or redirects | OS firewall and observe Ollama egress |
| Secret publication | data/config/index/log exclusions; synthetic fixtures | Human review of every staged file |
| Prompt injection | Data in JSON evidence, fixed system instructions, no tools | Real model adversarial evaluation; answer can be manipulated |
| Fabricated citations | Validate each claim's IDs against retrieved evidence | Human entailment checks; valid ID can support a false claim |
| File traversal | Supported types, size limits, symlink rejection | Folder must not change concurrently; no hostile parser sandbox |
| Model drift | Check embedding digest before/after ingest and before retrieval | Validate generation model and runtime versions locally |
| Local data theft | No content logging in app | OS permissions, disk encryption, backup/cloud-sync review |
| Residual data | SQLite secure_delete and VACUUM on reset | SSD, backups and original documents remain separate |

Operational checklist before real customer data: verify model sources/licences and
versions; restrict OS access; block external traffic; use approved documents; review
test results; document retention/deletion. CLI stdout includes evidence and is sensitive.
Tests with fake models prove code paths only, not model security or network isolation.
