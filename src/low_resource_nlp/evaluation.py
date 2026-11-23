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


def ordered_labels(
    y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str] | None = None
) -> List[str]:
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
    correct_counts = Counter(truth for truth, pred in zip(y_true, y_pred) if truth == pred)

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


def selective_classification_report(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    accepted: Sequence[bool],
    labels: Sequence[str] | None = None,
) -> Mapping[str, object]:
    """Report accuracy and coverage for predictions that may be rejected."""

    if len(y_true) != len(y_pred) or len(y_true) != len(accepted):
        raise ValueError("y_true, y_pred and accepted must have the same length.")
    if any(type(value) is not bool for value in accepted):
        raise ValueError("accepted must contain boolean values.")

    label_order = ordered_labels(y_true, y_pred, labels)
    accepted_pairs = [
        (truth, prediction) for truth, prediction, keep in zip(y_true, y_pred, accepted) if keep
    ]
    accepted_truth = [truth for truth, _ in accepted_pairs]
    accepted_predictions = [prediction for _, prediction in accepted_pairs]
    accepted_count = len(accepted_pairs)
    total = len(y_true)
    correct_count = sum(truth == prediction for truth, prediction in accepted_pairs)

    if accepted_pairs:
        accepted_report = classification_report(
            accepted_truth,
            accepted_predictions,
            label_order,
        )
    else:
        accepted_report = classification_report([], [], label_order)

    per_label: Dict[str, Mapping[str, object]] = {}
    for label in label_order:
        support = sum(truth == label for truth in y_true)
        selected = [
            (truth, prediction)
            for truth, prediction, keep in zip(y_true, y_pred, accepted)
            if keep and truth == label
        ]
        selected_correct = sum(truth == prediction for truth, prediction in selected)
        per_label[label] = {
            "support": support,
            "accepted": len(selected),
            "coverage": round(len(selected) / support, 4) if support else None,
            "selective_accuracy": round(selected_correct / len(selected), 4) if selected else None,
        }

    selective_accuracy = safe_divide(correct_count, accepted_count)
    return {
        "total": total,
        "accepted": accepted_count,
        "abstained": total - accepted_count,
        "coverage": round(accepted_count / total, 4) if total else None,
        "selective_accuracy": round(selective_accuracy, 4) if accepted_count else None,
        "selective_risk": round(1.0 - selective_accuracy, 4) if accepted_count else None,
        "overall_accuracy": round(correct_count / total, 4) if total else None,
        "accepted_macro_f1": accepted_report["macro_f1"] if accepted_count else None,
        "accepted_weighted_f1": accepted_report["weighted_f1"] if accepted_count else None,
        "labels": per_label,
        "confusion_matrix": accepted_report["confusion_matrix"],
    }


def accuracy(y_true: Iterable[str], y_pred: Iterable[str]) -> float:
    """Compute exact-match accuracy."""

    truth = list(y_true)
    pred = list(y_pred)
    if len(truth) != len(pred):
        raise ValueError("y_true and y_pred must have the same length.")
    return round(safe_divide(sum(t == p for t, p in zip(truth, pred)), len(truth)), 4)
