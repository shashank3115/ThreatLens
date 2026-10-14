from app.service import analyze_report


def test_rule_evidence_refs_are_passages_returned_for_the_same_report():
    result = analyze_report("Opening. The operator used rundll32.exe. Closing.")
    available = {(item.reference, item.excerpt) for item in result.extracted_evidence}
    rule_evidence = {(item.reference, item.excerpt) for item in result.rules[0].rule.evidence_refs}
    assert rule_evidence
    assert rule_evidence <= available
