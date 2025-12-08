import numpy as np
from sklearn.metrics import precision_recall_curve, precision_score, recall_score, f1_score

def compute_ranking_metrics(scores, labels, k_values):
    sorted_indices = np.argsort(scores)[::-1]
    sorted_labels = labels[sorted_indices]
    
    n_true = int(np.sum(labels))
    if n_true == 0:
        return None
    
    ranks = []
    for i in range(n_true):
        position = np.where(sorted_indices == i)[0][0] + 1
        ranks.append(position)
    
    metrics = {
        "ranks": ranks,
        "mean_rank": np.mean(ranks),
        "median_rank": np.median(ranks),
        "best_rank": np.min(ranks),
        "worst_rank": np.max(ranks),
    }
    
    for k in k_values:
        k_val = min(k, len(scores))
        true_in_top_k = np.sum(sorted_labels[:k_val])
        
        metrics[f"hit@{k}"] = 1.0 if true_in_top_k > 0 else 0.0
        metrics[f"recall@{k}"] = true_in_top_k / n_true
        metrics[f"precision@{k}"] = true_in_top_k / k_val if k_val > 0 else 0.0
    
    for k in k_values:
        prec = metrics[f"precision@{k}"]
        rec = metrics[f"recall@{k}"]
        if prec + rec > 0:
            metrics[f"f1@{k}"] = 2 * prec * rec / (prec + rec)
        else:
            metrics[f"f1@{k}"] = 0.0
    
    reciprocal_ranks = [1.0 / r for r in ranks]
    metrics["mrr"] = np.mean(reciprocal_ranks)
    
    average_precision = 0.0
    correct = 0
    for i, label in enumerate(sorted_labels, 1):
        if label == 1:
            correct += 1
            average_precision += correct / i
    metrics["map"] = average_precision / n_true if n_true > 0 else 0.0
    
    for k in k_values:
        k_val = min(k, len(scores))
        dcg = np.sum(sorted_labels[:k_val] / np.log2(np.arange(2, k_val+2)))
        ideal_labels = np.concatenate([np.ones(n_true), np.zeros(len(scores) - n_true)])[:k_val]
        idcg = np.sum(ideal_labels / np.log2(np.arange(2, k_val+2)))
        metrics[f"ndcg@{k}"] = dcg / idcg if idcg > 0 else 0.0
    
    return metrics


def compute_binary_metrics(scores, labels):
    prec, rec, thr = precision_recall_curve(labels, scores)
    f1_values = 2 * prec * rec / (prec + rec + 1e-8)
    best_idx = np.argmax(f1_values)
    best_threshold = thr[best_idx] if best_idx < len(thr) else thr[-1] if len(thr) > 0 else 0.0
    
    y_pred = (scores >= best_threshold).astype(int)
    return {
        "bin_threshold": float(best_threshold),
        "bin_precision": float(precision_score(labels, y_pred, zero_division=0)),
        "bin_recall": float(recall_score(labels, y_pred, zero_division=0)),
        "bin_f1": float(f1_score(labels, y_pred, zero_division=0)),
    }

