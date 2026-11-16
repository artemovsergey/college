#!/usr/bin/env python3
"""Собирает plan.yml из syllabus/ktp.yml и заготовок занятий.

Запуск из корня репозитория предмета:
    python3 .agents/skills/build-course-plan/scripts/build_plan.py
    python3 .agents/skills/build-course-plan/scripts/build_plan.py --check
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def read_stub(path: Path) -> tuple[dict, str]:
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    front = yaml.safe_load(parts[1]) or {}
    return front, parts[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="только проверить, не писать plan.yml")
    args = parser.parse_args()

    root = Path.cwd()
    cfg_path = root / "course.yaml"
    ktp_path = root / "syllabus" / "ktp.yml"
    outcomes_path = root / "syllabus" / "outcomes.yml"

    for path in (cfg_path, ktp_path, outcomes_path):
        if not path.exists():
            print(f"ERROR: нет файла {path.relative_to(root)}", file=sys.stderr)
            return 1

    cfg = load_yaml(cfg_path)
    ktp = load_yaml(ktp_path)
    outcomes = load_yaml(outcomes_path)

    course = cfg.get("course", {})
    hours = cfg.get("hours", {})

    plan_course = {key: course.get(key) for key in
                   ("code", "title", "specialty", "group", "year", "teacher")}
    plan_hours = {
        "total": hours.get("total", 0),
        "theory": hours.get("theory", 0),
        "practice": hours.get("practice", 0),
        "course_design": hours.get("course_design", 0),
        "selfstudy": hours.get("selfstudy", 0),
    }
    plan_outcomes = [
        {"code": item.get("code"), "text": item.get("text")}
        for item in outcomes.get("outcomes", [])
    ]

    errors: list[str] = []
    sections: list[dict] = []
    ktp_sections = ktp.get("sections", [])

    for section in ktp_sections:
        lessons: list[dict] = []
        for lesson in section.get("lessons", []):
            file_name = lesson.get("file", "")
            stub, body = read_stub(root / file_name) if file_name else ({}, "")
            lessons.append({
                "id": lesson.get("id"),
                "kind": lesson.get("kind"),
                "number": lesson.get("number"),
                "title": lesson.get("topic") or lesson.get("title") or "",
                "hours": lesson.get("hours", 0),
                "prerequisites": stub.get("prerequisites", lesson.get("prerequisites", [])),
                "outcomes": lesson.get("outcomes", stub.get("outcomes", [])),
                "sources": stub.get("sources", lesson.get("sources", [])),
                "file": file_name,
                "slides": stub.get("slides", lesson.get("slides", "")),
                "planned": stub.get("planned", not bool(body.strip())),
            })
        sections.append({
            "number": section.get("number"),
            "title": section.get("title"),
            "goal": section.get("goal", ""),
            "lessons": lessons,
        })

    for index, section in enumerate(sections):
        section_hours = sum(lesson["hours"] for lesson in section["lessons"])
        expected = ktp_sections[index].get("hours")
        if expected is not None and section_hours != expected:
            errors.append(
                f"Раздел {section['number']}: {section_hours} ч, в КТП {expected} ч"
            )

    total_hours = sum(section["hours"] for section in ktp_sections)
    if total_hours != plan_hours["total"]:
        errors.append(f"Всего {total_hours} ч, в course.yaml {plan_hours['total']} ч")

    lesson_ids = [lesson["id"] for section in sections for lesson in section["lessons"]]
    duplicates = sorted({item for item in lesson_ids if lesson_ids.count(item) > 1})
    if duplicates:
        errors.append(f"Повторяются ID занятий: {', '.join(duplicates)}")

    positions = {item: index for index, item in enumerate(lesson_ids)}
    known_outcomes = {item.get("code") for item in plan_outcomes}
    for section in sections:
        for lesson in section["lessons"]:
            for prerequisite in lesson["prerequisites"]:
                if prerequisite not in positions:
                    errors.append(f"{lesson['id']}: неизвестный пререквизит {prerequisite}")
                elif positions[prerequisite] >= positions[lesson["id"]]:
                    errors.append(f"{lesson['id']}: пререквизит {prerequisite} идёт позже")
            for code in lesson["outcomes"]:
                if code not in known_outcomes:
                    errors.append(f"{lesson['id']}: неизвестный результат {code}")
            if not lesson["file"]:
                errors.append(f"{lesson['id']}: не указан file")
            elif not (root / lesson["file"]).exists():
                errors.append(f"{lesson['id']}: нет файла {lesson['file']}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    plan = {
        "schema": 1,
        "course": plan_course,
        "hours": plan_hours,
        "outcomes": plan_outcomes,
        "sections": sections,
    }

    text = (
        "# Сгенерировано скиллом build-course-plan; руками не править.\n"
        "# Источник: course.yaml, syllabus/ktp.yml, syllabus/outcomes.yml, заготовки занятий.\n"
        + yaml.safe_dump(plan, allow_unicode=True, sort_keys=False)
    )

    if not args.check:
        (root / "plan.yml").write_text(text, encoding="utf-8")

    lessons_total = sum(len(section["lessons"]) for section in sections)
    planned = sum(
        1 for section in sections for lesson in section["lessons"] if lesson["planned"]
    )
    print(
        f"OK: {len(sections)} разделов, {lessons_total} занятий, "
        f"{plan_hours['total']} ч, заготовок {planned}"
    )
    if args.check:
        print("CHECK: plan.yml не записан")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
