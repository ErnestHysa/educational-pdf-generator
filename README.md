# Educational PDF Generator

A ready-to-run educational worksheet PDF generator service with no third-party runtime dependencies.

## What is included

- Input validation and clear error responses.
- `GET /health` endpoint for liveness checks.
- `POST /generate` endpoint that returns a valid PDF.
- Deterministic tests for core API behavior.

## Run locally

```bash
python -m educational_pdf_generator.server
```

Server starts on `http://127.0.0.1:8000`.

## API

### `GET /health`
Returns:

```json
{"status": "ok"}
```

### `POST /generate`
Returns a downloadable `application/pdf` file.

Example request body:

```json
{
  "title": "Introduction to Fractions",
  "subject": "Mathematics",
  "grade_level": "Grade 4",
  "difficulty": "beginner",
  "learning_objectives": ["Understand numerator and denominator"],
  "sections": [{"title": "Concept", "content": "Fractions represent equal parts of a whole."}],
  "questions": [{"prompt": "What is 1/2 of 10?", "answer": "5"}],
  "include_answer_key": true
}
```

## Test

```bash
PYTHONPATH=src pytest
```
