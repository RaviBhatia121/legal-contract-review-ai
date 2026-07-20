"""OllamaAdapter tests against a local stdlib mock HTTP server — no real
Ollama instance, no new test-only HTTP-mocking dependency."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from app.model_adapter.base import ClassifiedClause, TextBlock
from app.model_adapter.errors import ModelOutputInvalidError, ProviderUnavailableError
from app.model_adapter.ollama_adapter import OllamaAdapter

pytestmark = pytest.mark.asyncio


class _Handler(BaseHTTPRequestHandler):
    responses: list[dict] = []
    call_count = 0
    tags_ok = True

    def do_GET(self):
        if self.path == "/api/tags":
            if not self.tags_ok:
                self.send_response(500)
                self.end_headers()
                return
            self._write({"models": []})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        json.loads(self.rfile.read(length))  # validate the request is JSON
        idx = min(_Handler.call_count, len(_Handler.responses) - 1)
        payload = _Handler.responses[idx]
        _Handler.call_count += 1
        self._write(payload)

    def _write(self, payload: dict):
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture
def mock_server():
    _Handler.responses = []
    _Handler.call_count = 0
    _Handler.tags_ok = True
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


def _envelope(body: dict) -> dict:
    return {"model": "test-model", "message": {"role": "assistant", "content": json.dumps(body)}, "done": True}


async def test_classify_blocks_success(mock_server):
    port = mock_server.server_address[1]
    _Handler.responses = [
        _envelope(
            {
                "clauses": [
                    {
                        "clause_id": "c1",
                        "clause_type": "data_handling",
                        "title": "Data Handling",
                        "section_reference": "Section 6.2",
                        "page_start": 2,
                        "page_end": 2,
                        "extracted_text": "sample evidence",
                        "classification_confidence": 0.9,
                    }
                ]
            }
        )
    ]
    adapter = OllamaAdapter(base_url=f"http://127.0.0.1:{port}", model_name="test-model")
    result = await adapter.classify_blocks([TextBlock("b0", "text", 2, 2)], ["data_handling"])
    assert len(result) == 1
    assert result[0].clause_type == "data_handling"
    assert result[0].classification_confidence == 0.9


async def test_extract_attributes_success(mock_server):
    port = mock_server.server_address[1]
    _Handler.responses = [
        _envelope({"values": [{"attribute": "present", "value": True, "evidence_spans": ["x"]}]})
    ]
    adapter = OllamaAdapter(base_url=f"http://127.0.0.1:{port}", model_name="test-model")
    clause = ClassifiedClause("c1", "data_handling", "Data", "Section 6", 1, 1, "text", 0.9)
    result = await adapter.extract_attributes(clause, ["present"])
    assert result.raw_attributes == {"present": True}


async def test_repair_succeeds_on_second_attempt(mock_server):
    port = mock_server.server_address[1]
    _Handler.responses = [
        {"model": "test-model", "message": {"role": "assistant", "content": "not valid json {{{"}, "done": True},
        _envelope({"clauses": []}),
    ]
    adapter = OllamaAdapter(base_url=f"http://127.0.0.1:{port}", model_name="test-model")
    result = await adapter.classify_blocks([TextBlock("b0", "text", 1, 1)], ["data_handling"])
    assert result == []
    assert _Handler.call_count == 2


async def test_repair_fails_twice_raises_model_output_invalid(mock_server):
    port = mock_server.server_address[1]
    _Handler.responses = [
        {"model": "test-model", "message": {"role": "assistant", "content": "not valid json {{{"}, "done": True},
        {"model": "test-model", "message": {"role": "assistant", "content": "still not valid {{{"}, "done": True},
    ]
    adapter = OllamaAdapter(base_url=f"http://127.0.0.1:{port}", model_name="test-model")
    with pytest.raises(ModelOutputInvalidError):
        await adapter.classify_blocks([TextBlock("b0", "text", 1, 1)], ["data_handling"])
    assert _Handler.call_count == 2


async def test_unreachable_host_raises_provider_unavailable():
    adapter = OllamaAdapter(base_url="http://127.0.0.1:1", model_name="test-model", timeout_s=2.0)
    with pytest.raises(ProviderUnavailableError):
        await adapter.classify_blocks([TextBlock("b0", "text", 1, 1)], ["data_handling"])


async def test_ping_success(mock_server):
    port = mock_server.server_address[1]
    adapter = OllamaAdapter(base_url=f"http://127.0.0.1:{port}", model_name="test-model")
    result = await adapter.ping()
    assert result.ok is True


async def test_ping_failure_raises_provider_unavailable(mock_server):
    _Handler.tags_ok = False
    port = mock_server.server_address[1]
    adapter = OllamaAdapter(base_url=f"http://127.0.0.1:{port}", model_name="test-model")
    with pytest.raises(ProviderUnavailableError):
        await adapter.ping()
