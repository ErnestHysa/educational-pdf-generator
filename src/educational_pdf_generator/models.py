from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LessonSection:
    title: str
    content: str


@dataclass
class WorksheetQuestion:
    prompt: str
    answer: str | None = None


@dataclass
class GeneratePdfRequest:
    title: str
    subject: str
    grade_level: str
    difficulty: str = "beginner"
    learning_objectives: list[str] = field(default_factory=list)
    sections: list[LessonSection] = field(default_factory=list)
    questions: list[WorksheetQuestion] = field(default_factory=list)
    include_answer_key: bool = True

    @classmethod
    def from_dict(cls, payload: dict) -> "GeneratePdfRequest":
        required = ["title", "subject", "grade_level"]
        for key in required:
            if not isinstance(payload.get(key), str) or not payload[key].strip():
                raise ValueError(f"{key} is required and must be a non-empty string")

        difficulty = payload.get("difficulty", "beginner")
        if difficulty not in {"beginner", "intermediate", "advanced"}:
            raise ValueError("difficulty must be one of: beginner, intermediate, advanced")

        learning_objectives = payload.get("learning_objectives", [])
        if not isinstance(learning_objectives, list) or any(
            not isinstance(item, str) or not item.strip() for item in learning_objectives
        ):
            raise ValueError("learning_objectives must be a list of non-empty strings")

        sections_payload = payload.get("sections", [])
        if not isinstance(sections_payload, list):
            raise ValueError("sections must be a list")
        sections: list[LessonSection] = []
        for section in sections_payload:
            if not isinstance(section, dict):
                raise ValueError("each section must be an object")
            title = section.get("title", "")
            content = section.get("content", "")
            if not isinstance(title, str) or not title.strip() or not isinstance(content, str) or not content.strip():
                raise ValueError("section title/content must be non-empty strings")
            sections.append(LessonSection(title=title.strip(), content=content.strip()))

        questions_payload = payload.get("questions", [])
        if not isinstance(questions_payload, list):
            raise ValueError("questions must be a list")
        questions: list[WorksheetQuestion] = []
        for question in questions_payload:
            if not isinstance(question, dict):
                raise ValueError("each question must be an object")
            prompt = question.get("prompt", "")
            answer = question.get("answer")
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("question prompt must be a non-empty string")
            if answer is not None and not isinstance(answer, str):
                raise ValueError("question answer must be a string when provided")
            questions.append(WorksheetQuestion(prompt=prompt.strip(), answer=answer.strip() if isinstance(answer, str) else None))

        if not learning_objectives and not sections and not questions:
            raise ValueError("At least one of learning_objectives, sections, or questions must be provided")

        return cls(
            title=payload["title"].strip(),
            subject=payload["subject"].strip(),
            grade_level=payload["grade_level"].strip(),
            difficulty=difficulty,
            learning_objectives=[item.strip() for item in learning_objectives],
            sections=sections,
            questions=questions,
            include_answer_key=bool(payload.get("include_answer_key", True)),
        )
