from __future__ import annotations

from datetime import datetime, timezone

from .models import GeneratePdfRequest


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_text(text: str, max_chars: int = 90) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_chars:
            current += f" {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _build_lines(request: GeneratePdfRequest) -> list[str]:
    lines: list[str] = [
        request.title,
        f"Subject: {request.subject} | Grade: {request.grade_level} | Difficulty: {request.difficulty}",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]

    if request.learning_objectives:
        lines.append("Learning Objectives")
        for item in request.learning_objectives:
            lines.extend(_wrap_text(f"- {item}"))
        lines.append("")

    if request.sections:
        lines.append("Lesson Content")
        for idx, section in enumerate(request.sections, start=1):
            lines.append(f"{idx}. {section.title}")
            lines.extend(_wrap_text(section.content))
            lines.append("")

    if request.questions:
        lines.append("Worksheet Questions")
        for idx, question in enumerate(request.questions, start=1):
            lines.extend(_wrap_text(f"{idx}. {question.prompt}"))
            lines.append("Answer: __________________________")
            lines.append("")

    if request.include_answer_key and any(q.answer for q in request.questions):
        lines.append("Answer Key")
        for idx, question in enumerate(request.questions, start=1):
            if question.answer:
                lines.extend(_wrap_text(f"{idx}. {question.answer}"))

    return lines


def build_pdf(request: GeneratePdfRequest) -> bytes:
    lines = _build_lines(request)
    y = 760
    content_lines = ["BT", "/F1 12 Tf"]
    for line in lines:
        if y < 40:
            break
        safe = _escape_pdf_text(line)
        content_lines.append(f"1 0 0 1 50 {y} Tm ({safe}) Tj")
        y -= 16
    content_lines.append("ET")
    content_stream = "\n".join(content_lines).encode("utf-8")

    objects: list[bytes] = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(
        b"5 0 obj << /Length " + str(len(content_stream)).encode("ascii") + b" >> stream\n"
        + content_stream
        + b"\nendstream endobj\n"
    )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        (
            "trailer\n"
            f"<< /Size {len(offsets)} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_pos}\n"
            "%%EOF"
        ).encode("ascii")
    )

    return bytes(pdf)
