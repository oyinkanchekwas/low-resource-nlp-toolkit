"""Evaluation utilities for classification and routing experiments."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence


@dataclass(frozen=True)
class LabelMetrics:
    """Precision, recall, and F1 for one label."""

    precision: float
    recall: float
    f1: float
    support: int


def safe_divide(numerator: float, denominator: float) -> float:
    """Divide with zero protection."""

    return numerator / denominator if denominator else 0.0


def ordered_labels(y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str] | None = None) -> List[str]:
    """Return deterministic label order."""

    if labels:
        return list(labels)
    return sorted(set(y_true) | set(y_pred))


def confusion_matrix(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str] | None = None,
) -> Dict[str, Dict[str, int]]:
    """Build a nested confusion matrix as `truth -> prediction -> count`."""

    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")

    label_order = ordered_labels(y_true, y_pred, labels)
    matrix = {truth: {pred: 0 for pred in label_order} for truth in label_order}
    for truth, pred in zip(y_true, y_pred):
        matrix.setdefault(truth, {label: 0 for label in label_order})
        matrix[truth][pred] = matrix[truth].get(pred, 0) + 1
    return matrix


def precision_recall_f1(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str] | None = None,
) -> Dict[str, LabelMetrics]:
    """Compute per-label precision, recall, and F1."""

    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")

    label_order = ordered_labels(y_true, y_pred, labels)
    true_counts = Counter(y_true)
    pred_counts = Counter(y_pred)
    correct_counts = Counter(
        truth for truth, pred in zip(y_true, y_pred) if truth == pred
    )

    metrics: Dict[str, LabelMetrics] = {}
    for label in label_order:
        precision = safe_divide(correct_counts[label], pred_counts[label])
        recall = safe_divide(correct_counts[label], true_counts[label])
        f1 = safe_divide(2 * precision * recall, precision + recall)
        metrics[label] = LabelMetrics(
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1=round(f1, 4),
            support=true_counts[label],
        )
    return metrics


def classification_report(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str] | None = None,
) -> Mapping[str, object]:
    """Return a compact classification report."""

    metrics = precision_recall_f1(y_true, y_pred, labels)
    support_total = sum(metric.support for metric in metrics.values())
    accuracy = safe_divide(
        sum(1 for truth, pred in zip(y_true, y_pred) if truth == pred),
        len(y_true),
    )
    macro_f1 = safe_divide(sum(metric.f1 for metric in metrics.values()), len(metrics))
    weighted_f1 = safe_divide(
        sum(metric.f1 * metric.support for metric in metrics.values()),
        support_total,
    )
    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "labels": {
            label: {
                "precision": metric.precision,
                "recall": metric.recall,
                "f1": metric.f1,
                "support": metric.support,
            }
            for label, metric in metrics.items()
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, list(metrics)),
    }


def accuracy(y_true: Iterable[str], y_pred: Iterable[str]) -> float:
    """Compute exact-match accuracy."""

    truth = list(y_true)
    pred = list(y_pred)
    if len(truth) != len(pred):
        raise ValueError("y_true and y_pred must have the same length.")
    return round(safe_divide(sum(t == p for t, p in zip(truth, pred)), len(truth)), 4)
