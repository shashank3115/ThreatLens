# Architecture

The FastAPI API serves the static dashboard and same-origin JSON endpoints for health, sample data, analysis, and synthetic evaluation. `service.py` coordinates report analysis; `evidence.py`, `rules.py`, `validator.py`, and `log_matcher.py` are separate deterministic business-logic modules.

The baseline has exactly two documented report patterns: the literal text `rundll32.exe` produces a process-name equality rule, and `powershell -enc` produces a command-line contains rule. Supported operators are `equals` and `contains`, both case-insensitive. All rule conditions are ANDed. Rules are rendered with PyYAML, then parsed and validated against the Pydantic schema.

`data/sample_logs.json` is synthetic. Fields are: `event_id` stable identifier, ISO-8601 `timestamp`, `host`, `user`, `event_type`, `process_name`, `command_line`, and an intentional demonstration `label` (`suspicious` or `benign`).

`evaluation.py` reads `data/evaluation_cases.json`. Its expected rule IDs are hand-authored ground truth, separate from the matcher. It reports per-rule confusion-matrix counts and derived precision, recall, and false-positive rate. Ratios with zero denominators are represented as `null`.
