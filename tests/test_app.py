import json
from http.client import HTTPConnection
from threading import Thread
from time import sleep

from educational_pdf_generator.server import run_server


def _start_server(port: int) -> Thread:
    thread = Thread(target=run_server, kwargs={"host": "127.0.0.1", "port": port}, daemon=True)
    thread.start()
    sleep(0.2)
    return thread


def test_health_endpoint() -> None:
    _start_server(8123)
    conn = HTTPConnection("127.0.0.1", 8123)
    conn.request("GET", "/health")
    response = conn.getresponse()
    body = response.read().decode("utf-8")

    assert response.status == 200
    assert json.loads(body) == {"status": "ok"}


def test_generate_pdf_endpoint() -> None:
    _start_server(8124)
    payload = {
        "title": "Introduction to Fractions",
        "subject": "Mathematics",
        "grade_level": "Grade 4",
        "difficulty": "beginner",
        "learning_objectives": ["Understand numerator and denominator"],
        "sections": [{"title": "Concept", "content": "Fractions represent equal parts of a whole."}],
        "questions": [{"prompt": "What is 1/2 of 10?", "answer": "5"}],
        "include_answer_key": True,
    }

    conn = HTTPConnection("127.0.0.1", 8124)
    conn.request(
        "POST",
        "/generate",
        body=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    response = conn.getresponse()
    body = response.read()

    assert response.status == 200
    assert response.getheader("Content-Type") == "application/pdf"
    assert body.startswith(b"%PDF")


def test_generate_pdf_validation_failure() -> None:
    _start_server(8125)
    payload = {
        "title": "Empty Lesson",
        "subject": "Science",
        "grade_level": "Grade 5",
        "learning_objectives": [],
        "sections": [],
        "questions": [],
    }

    conn = HTTPConnection("127.0.0.1", 8125)
    conn.request(
        "POST",
        "/generate",
        body=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    response = conn.getresponse()
    body = json.loads(response.read().decode("utf-8"))

    assert response.status == 400
    assert "At least one" in body["error"]
