import numpy as np
import torch
from sampling import sample_negatives
from metrics import compute_ranking_metrics


def evaluate_node(source_id, true_targets, all_node_ids, entity_to_idx,
                  all_emb, operator, comp, all_neighbors, 
                  num_negatives_per_true, dim, k_values):
    source_idx = entity_to_idx.get(source_id)
    if source_idx is None:
        return None
    
    true_indices = []
    for target_id in true_targets:
        if target_id in entity_to_idx:
            true_indices.append(entity_to_idx[target_id])
    
    if not true_indices:
        return None
    
    n_true = len(true_indices)
    num_negatives = num_negatives_per_true * n_true
    negative_indices = sample_negatives(
        source_id, all_neighbors, all_node_ids, entity_to_idx, num_negatives
    )
    
    if len(negative_indices) == 0:
        return None
    
    candidate_indices = true_indices + negative_indices
    candidate_emb = all_emb[candidate_indices]
    
    if operator.dim() == 1:
        rhs_proj = candidate_emb * operator.unsqueeze(0)
    else:
        rhs_proj = candidate_emb @ operator.T
    
    src_emb = all_emb[source_idx]
    
    lhs_prepared = comp.prepare(src_emb.view(1, 1, dim)).expand(1, len(candidate_indices), dim)
    rhs_prepared = comp.prepare(rhs_proj.view(1, len(candidate_indices), dim))
    
    pos_scores, _, _ = comp(
        lhs_prepared,
        rhs_prepared,
        torch.empty(1, 0, dim),
        torch.empty(1, 0, dim),
    )
    scores = pos_scores.view(-1).cpu().numpy()
    
    labels = np.zeros(len(candidate_indices))
    labels[:n_true] = 1
    
    metrics = compute_ranking_metrics(scores, labels, k_values)
    if metrics is None:
        return None
    
    metrics["source_id"] = source_id
    metrics["num_true"] = n_true
    metrics["num_candidates"] = len(candidate_indices)
    metrics["num_negatives"] = len(negative_indices)
    metrics["scores"] = scores.tolist()
    metrics["labels"] = labels.tolist()
    
    return metrics

