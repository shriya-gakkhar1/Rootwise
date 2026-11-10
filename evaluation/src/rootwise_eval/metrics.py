"""Small, deterministic evaluation metrics."""

from collections.abc import Iterable, Sequence


def top_k_accuracy(predictions: Sequence[str], truth: str, k: int) -> float:
    """Return 1.0 when truth occurs among the first k predictions, otherwise 0.0."""
    if k < 1:
        raise ValueError("k must be positive")
    return float(truth in predictions[:k])


def pairwise_grouping_f1(predicted: Iterable[Iterable[str]], truth: Iterable[Iterable[str]]) -> float:
    """Compute pairwise F1 over item pairs grouped together in predicted and true clusters."""
    def pairs(groups: Iterable[Iterable[str]]) -> set[frozenset[str]]:
        return {
            frozenset((left, right))
            for group in groups
            for left in group
            for right in group
            if left != right
        }

    predicted_pairs = pairs(predicted)
    truth_pairs = pairs(truth)
    true_positives = len(predicted_pairs & truth_pairs)
    precision = true_positives / len(predicted_pairs) if predicted_pairs else 0.0
    recall = true_positives / len(truth_pairs) if truth_pairs else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0
