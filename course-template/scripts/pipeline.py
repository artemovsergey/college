#!/usr/bin/env python3
"""Оркестратор пайплайна курса: проверка и статус занятий.

Запускается из корня репозитория предмета:
    python scripts/pipeline.py check
    python scripts/pipeline.py status
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path.cwd()
ERRORS: list[str] = []
WARNINGS: list[str] = []


def load(path: str) -> dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        return {}
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        ERRORS.append(f"{path}: не парсится ({exc})")
        return {}
    return data or {}


def error(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def lesson_key(lesson: dict[str, Any]) -> tuple[str, int]:
    return str(lesson.get("id", "")), int(lesson.get("number", 0))


def collect_codes() -> set[str]:
    data = load("syllabus/outcomes.yml")
    return {str(x.get("code")) for x in data.get("outcomes", []) if x.get("code")}


def check() -> int:
    plan = load("plan.yml")
    course = load("course.yaml")
    ktp = load("syllabus/ktp.yml")

    sections = plan.get("sections") or []
    if not sections:
        error("plan.yml: нет sections")
        print_report()
        return 1

    plan_hours = plan.get("hours") or {}
    total = sum(
        int(lesson.get("hours", 0))
        for section in sections
        for lesson in section.get("lessons") or []
    )
    if int(plan_hours.get("total", -1)) != total:
        error(f"plan.yml: hours.total={plan_hours.get('total')} != сумма разделов {total}")

    course_hours = (course.get("hours") or {}).get("total")
    if course_hours is not None and int(course_hours) != total:
        error(f"course.yaml: hours.total={course_hours} != plan {total}")

    known = collect_codes()
    ids: dict[str, int] = {}
    order: list[str] = []

    for section in sections:
        s_hours = 0
        for lesson in section.get("lessons") or []:
            lid = str(lesson.get("id", ""))
            if not lid:
                error(f"раздел {section.get('number')}: занятие без id")
                continue
            if lid in ids:
                error(f"plan.yml: повтор id {lid}")
            ids[lid] = len(order)
            order.append(lid)

            hours = int(lesson.get("hours", 0))
            s_hours += hours
            if hours <= 0:
                error(f"{lid}: hours={hours}")

            file = lesson.get("file")
            if not file:
                error(f"{lid}: нет file")
            elif not (ROOT / file).exists():
                error(f"{lid}: файл не найден: {file}")

            for code in lesson.get("outcomes") or []:
                if known and str(code) not in known:
                    error(f"{lid}: неизвестный outcome {code}")

            for pre in lesson.get("prerequisites") or []:
                if pre not in ids:
                    error(f"{lid}: пререквизит {pre} не существует или идёт позже")

        if "hours" in section and int(section.get("hours", 0)) != s_hours:
            error(f"раздел {section.get('number')}: hours={section.get('hours')} != {s_hours}")

    if ktp:
        ktp_sections = ktp.get("sections") or []
        ktp_total = int((ktp.get("hours") or {}).get("total", -1))
        if ktp_total != total:
            error(f"ktp.yml: hours.total={ktp_total} != plan {total}")
        ktp_ids = {
            str(lesson.get("id"))
            for section in ktp_sections
            for lesson in section.get("lessons") or []
        }
        missing = sorted(set(ids) - ktp_ids)
        extra = sorted(ktp_ids - set(ids))
        if missing:
            error(f"ktp.yml: нет занятий из plan: {', '.join(missing)}")
        if extra:
            error(f"ktp.yml: лишние занятия: {', '.join(extra)}")
    else:
        warn("syllabus/ktp.yml не найден — сверка с КТП пропущена")

    for lid in order:
        lesson = next(
            (l for s in sections for l in (s.get("lessons") or []) if str(l.get("id")) == lid),
            {},
        )
        file = lesson.get("file")
        if file and (ROOT / file).exists():
            text = (ROOT / file).read_text(encoding="utf-8", errors="ignore")
            if "TODO" in text or "{{" in text:
                error(f"{lid}: в файле остались TODO/плейсхолдеры")

    print_report()
    return 1 if ERRORS else 0


def status() -> int:
    plan = load("plan.yml")
    sections = plan.get("sections") or []
    if not sections:
        print("STATUS: plan.yml пуст")
        return 1

    counts = {"planned": 0, "draft": 0, "reviewed": 0, "ready": 0}
    rows: list[str] = []
    for section in sections:
        for lesson in section.get("lessons") or []:
            lid = str(lesson.get("id", ""))
            file = lesson.get("file", "")
            exists = bool(file) and (ROOT / file).exists()
            planned = bool(lesson.get("planned", not exists))
            if planned or not exists:
                state = "planned"
            else:
                stem = Path(file).stem
                review = ROOT / "docs" / f"{stem}-review.md"
                state = "reviewed" if review.exists() else "draft"
            counts[state] += 1
            rows.append(f"{lid:6} {state:8} {lesson.get('kind',''):10} {lesson.get('title','')}")

    print("ID     STATUS   KIND       TITLE")
    for row in rows:
        print(row)
    print(
        "STATUS: "
        + ", ".join(f"{k}={v}" for k, v in counts.items())
        + f"; всего={sum(counts.values())}"
    )
    return 0


def print_report() -> None:
    for w in WARNINGS:
        print(f"WARN: {w}")
    for e in ERRORS:
        print(f"ERROR: {e}")
    if not ERRORS:
        print(f"OK: проверка пройдена, предупреждений {len(WARNINGS)}")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "status"}:
        print("usage: python scripts/pipeline.py check|status")
        return 2
    return check() if sys.argv[1] == "check" else status()


if __name__ == "__main__":
    raise SystemExit(main())
