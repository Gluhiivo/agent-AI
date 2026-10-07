import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sales_rag.config import load
from sales_rag.ollama import Ollama
from sales_rag.answering import answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = load(args.config)
    client = Ollama(config.endpoint)
    results = {"embedding_digest": client.model_digest(config.embedding_model),
               "generation_digest": client.model_digest(config.generation_model),
               "grading": "pending human review", "questions": []}
    questions = json.loads((Path(__file__).parent / "questions.json").read_text(encoding="utf-8"))
    for entry in questions:
        started = time.perf_counter()
        result = answer(config, client, entry["question"])
        results["questions"].append({**entry, "result": result,
                                     "seconds": time.perf_counter() - started})
        print(f"Completed {len(results['questions'])}/{len(questions)}", flush=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
