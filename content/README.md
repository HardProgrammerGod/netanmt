# Neta NMT content packs

Ця папка містить історичні/поточні JSON content packs, які залишені для аудиту та подальшого поповнення банку.

Фінальний v4 release **не вимагає** окремого content SQL-файлу: learning migration працює з уже наявною таблицею `questions` і має fallback, якщо curated intro-коди з v1.7 не були імпортовані раніше.

Перевірка bundled v1.7 pack:

```bash
python tools/validate_content.py
```

Якщо пізніше потрібно окремо перетворити v1.7 JSON у SQL для нового середовища, використовуйте:

```bash
python tools/build_sql_pack_v1_7.py
```

Згенерований SQL є content import, а не частиною обов’язкової v4 schema migration.
