from app.evidence import find_evidence


def test_finds_case_insensitive_passage():
    report = "First. RUNDLL32.EXE started here. Final."
    found = find_evidence(report, ["rundll32.exe"])
    assert found[0].reference == "passage-2"
    assert found[0].excerpt == "RUNDLL32.EXE started here."


def test_missing_evidence_is_empty():
    assert find_evidence("Nothing relevant.", ["powershell -enc"]) == []
