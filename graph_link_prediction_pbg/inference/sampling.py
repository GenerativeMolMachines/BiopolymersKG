import random


def sample_negatives(source_id, all_neighbors, all_node_ids, entity_to_idx, num_negatives):
    source_idx = entity_to_idx.get(source_id)
    if source_idx is None:
        return []
    
    excluded_indices = {source_idx}
    neighbors = all_neighbors.get(source_id, set())
    for target_id in neighbors:
        if target_id in entity_to_idx:
            excluded_indices.add(entity_to_idx[target_id])
    
    available_indices = [idx for idx in range(len(all_node_ids)) 
                        if idx not in excluded_indices]
    
    if len(available_indices) < num_negatives:
        return available_indices
    else:
        return random.sample(available_indices, num_negatives)

