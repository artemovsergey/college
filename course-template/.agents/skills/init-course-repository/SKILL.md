---
name: init-course-repository
description: Создаёт репозиторий нового предмета из шаблона — структуру, course.yaml, AGENTS.md, syllabus и заготовку CI. Использовать при запуске нового курса до РП и КТП.
---

# Инициализация репозитория предмета

## Когда применять

- новый предмет или МДК, для которого ещё нет репозитория;
- нужно развернуть шаблон `course-template` в рабочую папку;
- перед `create-rp` и `create-ktp`, когда метаданные курса ещё не заполнены.

Не применять для существующего репозитория: там сначала читают `course.yaml` и
`AGENTS.md`, а не копируют шаблон поверх.

## Вход

| Параметр | Обязателен | Пример |
|----------|------------|--------|
| Код специальности | да | `09.02.07` |
| Квалификация | да | `администратор баз данных` |
| Модуль | да | `ПМ.01 Разработка модулей ПО` |
| МДК / предмет | да | `МДК 01.03 Разработка мобильных приложений` |
| Группа | да | `ИБ-243` |
| Курс и семестр | да | `3 курс, 5 семестр` |
| Учебный год | да | `2026/2027` |
| Преподаватель | да | `Фамилия И.О.` |
| Часы | да | `70 = 28 + 38 + 4` |
| Стек | желательно | `C#, .NET MAUI, SQLite` |
| Путь шаблона | да | `college/course-template` |
| Путь нового репозитория | да | `/home/user1/work/mdk0103` |

Если обязательного параметра нет, остановиться и спросить. Не подставлять
правдоподобные часы, группу или специальность.

## Порядок

1. **Проверить вход.** Сверить код специальности и квалификацию с учебным планом.
   Проверить арифметику часов: `total = theory + practice + selfstudy` плюс
   `course_design`, `consultation`, `exam`, если они есть.
2. **Проверить шаблон.** В шаблоне должны быть `AGENTS.md`, `README.md`,
   `docs/architecture.md`, `course.yaml`, `syllabus/`, `course/`, `projects/`,
   `templates/`. Если чего-то нет — остановиться.
3. **Создать каталог.** Если целевой путь уже существует, не перезаписывать:
   спросить, что делать.
4. **Скопировать шаблон без мусора.**
   ```bash
   TEMPLATE=/home/user1/bb-workspace/college/course-template
   TARGET=/home/user1/work/<slug>
   test -e "$TARGET" && { echo "target exists"; exit 1; }
   cp -a "$TEMPLATE" "$TARGET"
   rm -rf "$TARGET/.git" "$TARGET/dist"
   find "$TARGET" -name __pycache__ -type d -prune -exec rm -rf {} +
   ```
5. **Заполнить `course.yaml`.** Все поля — из входа, не из головы. Часы — те,
   что дал преподаватель или учебный план. Пример:
   ```yaml
   course:
     code: "МДК 01.03"
     title: "Разработка мобильных приложений"
     specialty: "09.02.07"
     qualification: "администратор баз данных"
     module: "ПМ.01 Разработка модулей программного обеспечения"
     group: "ИБ-243"
     year: "2026/2027"
     study_year: 3
     semester: 5
     teacher: "Фамилия И.О."
     repo_slug: "mdk0103"
     stack: ["C#", ".NET MAUI", "SQLite"]

   hours:
     total: 70
     theory: 28
     practice: 38
     selfstudy: 4

   build:
     docx: true
     pdf: true
     pptx: true
     figures: true
     book: false
   ```
6. **Проверить структуру.** Должны существовать `syllabus/normative/`,
   `course/`, `projects/`, `templates/`, `.agents/skills/`, `.opencode/agents/`,
   `.github/workflows/`.
7. **Инициализировать git, если попросили.** `git init`, первый коммит — только
   по команде преподавателя. Не пушить.
8. **Написать отчёт.** Что создано, какие входы использованы, чего не хватает.

## Проверки

```bash
python3 -c "import yaml; yaml.safe_load(open('course.yaml'))"
test -d syllabus/normative && test -d course && test -d projects
test ! -d dist && test ! -d .git
grep -RInE 'ghp_|github_pat_|Bearer |password=' . --exclude-dir=.git || true
find . -maxdepth 2 -type d | sort
```

- `course.yaml` парсится как YAML.
- Часы сходятся, `repo_slug` — латиницей.
- В репозитории нет `dist`, `__pycache__`, `.env`, токенов и чужих файлов.
- `plan.yml` и `syllabus/ktp.yml` остаются заготовками: их заполняют следующие
  скиллы.

## Запреты

- Не заполнять РП и КТП: это `create-rp` и `create-ktp`.
- Не придумывать часы, группу, специальность и квалификацию.
- Не копировать `.git`, `dist` и чужие рабочие файлы.
- Не коммитить и не пушить без команды.
- Не менять `AGENTS.md` и `docs/architecture.md` в шаблоне под конкретный курс.

## Результат

Репозиторий по пути `TARGET`, заполненный `course.yaml`, структура каталогов,
`AGENTS.md` и `docs/architecture.md` из шаблона, отчёт с открытыми вопросами.
