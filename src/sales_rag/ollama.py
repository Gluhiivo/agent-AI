import json
import math
from urllib.request import build_opener, ProxyHandler, HTTPRedirectHandler, Request
from .config import validate_endpoint


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("HTTP redirects are forbidden")


class Ollama:
    def __init__(self, endpoint):
        self.endpoint = validate_endpoint(endpoint)
        self.http = build_opener(ProxyHandler({}), NoRedirect())

    def call(self, route, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        request = Request(self.endpoint + route, data=data,
                          headers={"Content-Type": "application/json"})
        with self.http.open(request, timeout=180) as response:
            raw = response.read(8 * 1024 * 1024 + 1)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError("Model response too large")
        return json.loads(raw)

    def model_digest(self, name):
        for model in self.call("/api/tags").get("models", []):
            if name in (model.get("name"), model.get("model")):
                if not model.get("digest"):
                    raise ValueError("Missing model digest")
                return model["digest"]
        raise ValueError("Requested model is not installed locally")

    def embed(self, model, text):
        vectors = self.call("/api/embed", {"model": model, "input": text,
                                           "truncate": False})["embeddings"]
        if len(vectors) != 1 or not vectors[0]:
            raise ValueError("Invalid embedding response")
        vector = vectors[0]
        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in vector):
            raise ValueError("Invalid embedding values")
        if not any(vector):
            raise ValueError("Zero embedding")
        return vector

    def generate(self, model, system, prompt):
        return self.call("/api/generate", {
            "model": model, "system": system, "prompt": prompt,
            "stream": False, "format": "json", "think": False,
            "options": {"temperature": 0, "num_predict": 1200},
        })["response"]
