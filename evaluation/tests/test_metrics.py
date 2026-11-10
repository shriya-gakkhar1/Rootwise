from rootwise_eval.metrics import pairwise_grouping_f1, top_k_accuracy
from rootwise_eval.models import RunRecord


def test_run_record_and_top_k() -> None:
    record = RunRecord(
        scenario_id="s1", seed=1, system_variant="baseline",
        degradation_config={}, results={"ranking": ["a", "b"]},
    )
    assert record.scenario_id == "s1"
    assert top_k_accuracy(["a", "b", "c"], "b", 2) == 1.0
    assert top_k_accuracy(["a", "b"], "c", 2) == 0.0


def test_pairwise_grouping_f1() -> None:
    assert pairwise_grouping_f1([["a", "b"], ["c"]], [["a", "b"], ["c"]]) == 1.0
    assert pairwise_grouping_f1([["a", "c"], ["b"]], [["a", "b"], ["c"]]) == 0.0
