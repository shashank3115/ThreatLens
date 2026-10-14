from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from .models import AnalyzeRequest, AnalyzeResponse, SecurityEvent
from .service import analyze_report, load_sample_events, load_sample_report
from .evaluation import EvaluationReport, evaluate_baseline

app = FastAPI(title="ThreatLens", version="0.1.0", description="Deterministic evidence-grounded detection-rule prototype.")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/api/health")
def health() -> dict[str, str]:
    # Check bundled prerequisites without retaining or logging report input.
    try:
        load_sample_report()
        load_sample_events()
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Bundled sample data is unavailable.") from exc
    return {"status": "ok", "service": "ThreatLens"}


@app.get("/api/sample-report")
def sample_report() -> dict[str, str]:
    return {"report": load_sample_report()}


@app.get("/api/sample-events", response_model=list[SecurityEvent])
def sample_events() -> list[SecurityEvent]:
    """Expose only the bundled synthetic events for the local event inspector."""
    return load_sample_events()


@app.get("/api/evaluation", response_model=EvaluationReport)
def evaluation() -> EvaluationReport:
    """Return metrics calculated from the bundled independent synthetic labels."""
    return evaluate_baseline()


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_report(request.report)


# Mount this last: a root mount otherwise captures every /api request.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
