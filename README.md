# ThreatLens

A stateless FastAPI prototype for a student innovation challenge. It extracts literal evidence from a report, proposes two explicitly defined rule patterns, validates custom YAML rules, and tests them against synthetic logs. It does **not** claim to be an LLM, a complete detection platform, or a guarantee of real-attack detection.

## Quick start (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. The API documentation is at http://127.0.0.1:8000/docs.

Run tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The API is served from the same origin as the frontend. Available endpoints are `GET /api/health`, `GET /api/sample-report`, `GET /api/sample-events`, `GET /api/evaluation`, and `POST /api/analyze` with `{ "report": "..." }`. Reports are analysed in memory only; the application does not persist or log their content.

## Synthetic evaluation

`data/evaluation_cases.json` contains six reproducible, hand-authored cases: two intended detections, two benign lookalikes, and two unrelated events. Expected rule IDs are stored independently from the matcher. `GET /api/evaluation` calculates per-rule precision, recall, and false-positive rate from those labels; a zero denominator is returned as `null`, not a fabricated metric.

For the current dataset, each baseline rule has 1 true positive, 1 false positive, 4 true negatives, and 0 false negatives: precision `0.5`, recall `1.0`, and false-positive rate `0.2`. These numbers apply only to this deliberately small synthetic dataset and are not production-performance claims.

## Deploy to Render

`render.yaml` defines one stateless web service. It installs `requirements.txt`, starts the same FastAPI app on `0.0.0.0` using Render's `PORT`, and uses `/api/health` for health checks.

1. Create a Git repository containing this project and push it to a provider you control.
2. In Render, select **New +** → **Blueprint**, connect that repository, and review the service from `render.yaml`.
3. Keep `autoDeploy: false` or change it in Render only if you want automatic deploys after future pushes.
4. Click **Apply** to deploy. Do not add secrets: this milestone needs none.
5. After Render reports the service live, open its `/api/health` URL and then the root URL to verify the dashboard.

For another host, use the equivalent production command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

On local PowerShell, continue using the development command above; it defaults to `127.0.0.1:8000` and reloads on code changes.

See [architecture](docs/architecture.md) and [limitations](docs/limitations.md). The next milestone should add more carefully documented patterns, rule editing, and larger labelled synthetic evaluation datasets before considering any optional AI integration.
