from app.rules import generate_rules


def test_rules_have_or_lack_evidence_based_on_report():
    rules = generate_rules("The operator used rundll32.exe.")
    assert len(rules) == 2
    assert rules[0].evidence_refs
    assert not rules[1].evidence_refs
