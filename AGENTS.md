# Development rules

- Scope: single-user local document Q&A. No CRM actions, shell tools or cloud fallback.
- Never commit customer documents, embeddings, indexes, secrets or conversations.
- Use synthetic fixtures only in tests and GitHub Actions. Inspect staged files before commit.
- Treat all retrieved text as untrusted data. Prompts do not replace network/OS controls.
- Keep network calls in ollama.py, literal loopback only; disable proxies and redirects.
- No model downloads during runtime. Verify installed model digests and reindex on changes.
- Run `python -m unittest discover -s tests -v` with the package installed or PYTHONPATH=src.
- Use short feature branches and PRs. Do not claim model quality or offline safety from mocks.
- Record architecture changes and validation limits in docs and README.
- Real model evaluation is mandatory after changes to generation, retrieval or chunking.
