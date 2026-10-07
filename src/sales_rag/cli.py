import argparse
import json
import sys
from .config import load
from .ollama import Ollama
from .index import ingest, retrieve, reset
from .answering import answer


def main():
    parser = argparse.ArgumentParser(description="Local sales RAG")
    parser.add_argument("--config", default="config.toml")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ingest")
    for name in ("ask", "search"):
        command = sub.add_parser(name)
        command.add_argument("question", nargs="?")
    command = sub.add_parser("reset")
    command.add_argument("--yes", action="store_true", required=True)
    args = parser.parse_args()
    try:
        config = load(args.config)
        client = Ollama(config.endpoint)
        if args.command == "reset":
            reset(config)
            result = {"status": "index cleared", "original_documents": "retained"}
        elif args.command == "ingest":
            result = {"chunks": ingest(config, client)}
        else:
            question = args.question if args.question is not None else input("Vprašanje: ")
            if not question.strip() or len(question) > 4000:
                raise ValueError("Question must contain 1-4000 characters")
            result = (answer(config, client, question) if args.command == "ask"
                      else retrieve(config, client, question))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception:
        # Avoid exposing document content, prompts or file names through tracebacks.
        print("Operacija ni uspela. Preverite lokalni model, konfiguracijo, format dokumentov in indeks. Brez cloud fallbacka.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
