import random
import numpy as np
import torch
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

from config import *
from loaders import load_entity_names, load_embeddings, load_operator, load_test_pairs, load_all_neighbors
from comparator import get_comparator
from report import process_csv_file, create_summary_table
from visualization import setup_plot_style, plot_comparison_metrics, plot_main_metrics


def main():
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    setup_plot_style()
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(PLOTS_DIR).mkdir(parents=True, exist_ok=True)
    
    print("Loading model and embeddings...")
    entity_names = load_entity_names(ENTITY_JSON)
    all_emb = load_embeddings(EMB_H5)
    operator = load_operator(MODEL_H5, DIM, relation_idx=0)
    comp = get_comparator(COMPARATOR)
    print(f"Model loaded: {all_emb.shape[0]} nodes, operator shape={operator.shape}")
    
    entity_to_idx = {name: idx for idx, name in enumerate(entity_names)}
    all_node_ids = entity_names
    
    print("\nLoading test set...")
    test_pairs = load_test_pairs(TEST_TSV)
    print(f"Loaded {len(test_pairs)} test pairs")
    
    test_nodes_dict = defaultdict(set)
    for source_id, target_id in test_pairs:
        test_nodes_dict[source_id].add(target_id)
    
    print(f"Unique source nodes in test: {len(test_nodes_dict)}")
    
    print("\nLoading all neighbors from train/val/test...")
    all_neighbors = load_all_neighbors(TRAIN_TSV, VAL_TSV, TEST_TSV, relation_name="interacts_with")
    
    print(f"\nProcessing {len(CSV_FILES)} CSV files...")
    all_results_by_file = {}
    
    for csv_path in CSV_FILES:
        csv_file = Path(csv_path)
        print(f"\nProcessing: {csv_file.name}")
        
        summary = process_csv_file(
            csv_path, entity_to_idx, test_nodes_dict, all_node_ids,
            all_emb, operator, comp, all_neighbors, DIM, K_VALUES,
            NUM_NEGATIVES_PER_TRUE, OUTPUT_DIR, PLOTS_DIR
        )
        
        if summary:
            all_results_by_file[csv_file.stem] = summary
            print(f"Processed {summary['num_nodes']} nodes")
            print(f"MAP: {summary['map']:.4f}, MRR: {summary['mrr']:.4f}")
    
    if all_results_by_file:
        print("\nCreating summary table...")
        summary_df = create_summary_table(all_results_by_file, OUTPUT_DIR)
        print(summary_df.to_string(index=False))
        
        print("\nCreating comparison plots...")
        plot_comparison_metrics(all_results_by_file, PLOTS_DIR, K_VALUES)
        plot_main_metrics(all_results_by_file, PLOTS_DIR)
        print("All plots saved")
    
    print("\nDone")


if __name__ == "__main__":
    main()

