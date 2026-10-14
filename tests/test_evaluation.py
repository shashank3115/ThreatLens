from app.evaluation import evaluate_baseline, safe_ratio


def test_baseline_evaluation_uses_independent_expected_rule_ids():
    report = evaluate_baseline()
    assert report.dataset_size == 6
    assert [(metric.true_positives, metric.false_positives, metric.true_negatives, metric.false_negatives)
            for metric in report.metrics] == [(1, 1, 4, 0), (1, 1, 4, 0)]


def test_zero_denominator_is_not_presented_as_a_metric():
    assert safe_ratio(0, 0) is None
