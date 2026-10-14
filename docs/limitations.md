# Limitations

- This is not an AI model and does not use external intelligence feeds.
- Literal pattern extraction is intentionally narrow; wording changes can produce unsupported candidates.
- YAML/schema validity does not prove a rule is useful, safe, or effective.
- Matches are evaluated only against four synthetic events; benign matches are warnings, not measured false-positive rates.
- The separate six-case evaluation set has independent expected rule IDs, but remains a small hand-authored synthetic dataset. Its metrics are reproducible checks, not production performance evidence.
- The schema is a small custom schema, not the full Sigma specification. There is no field mapping, correlation, alerting, authentication, or production-log access.
