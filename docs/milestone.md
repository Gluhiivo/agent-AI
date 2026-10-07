# M1 implementation and acceptance

Implemented steps:
1. Project scaffold, configuration, local endpoint controls, README and development rules.
2. TXT/MD/PDF ingestion, overlapping chunks, local embeddings, transactional SQLite
   index, search, reindex-based removal and reset.
3. Local generation, structured citations, conservative refusal paths, synthetic tests,
   20-question evaluation runner and CI.

Completed verification: 16 synthetic tests on Python 3.12.14, no actual LLM used.
Acceptance pending: real installed models and versions, PDF extra, target Windows
environment, 20-question human grading (>=16 correct and all 5 unsupported refused),
adversarial tests, blocked-egress operation/monitoring, latency and peak memory.

Do not describe this as production-ready or fully accepted M1 until these pass.
After acceptance: compare user-approved real SLO/EN documents, calibrate retrieval,
then consider more file formats and a local UI. CRM actions require separate scope.
