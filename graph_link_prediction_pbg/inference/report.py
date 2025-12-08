import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from metrics import compute_binary_metrics


def process_csv_file(csv_path, entity_to_idx, test_nodes_dict, all_node_ids,
                     all_emb, operator, comp, all_neighbors, dim, k_values,
                     num_negatives_per_true, output_dir, plots_dir):
    csv_file = Path(csv_path)
    if not csv_file.exists():
        return None
    
    from inference.loaders import load_csv_nodes
    from inference.evaluation import evaluate_node
    from inference.visualization import plot_per_file_metrics
    
    df_valid = load_csv_nodes(csv_path, entity_to_idx)
    if len(df_valid) == 0:
        return None
    
    valid_sources = []
    for _, row in df_valid.iterrows():
        source_id = row["entity_id"]
        if source_id in test_nodes_dict and len(test_nodes_dict[source_id]) > 0:
            valid_sources.append(source_id)
    
    if len(valid_sources) == 0:
        return None
    
    all_results = []
    for source_id in tqdm(valid_sources, desc=f"Evaluating {csv_file.stem}"):
        true_targets = test_nodes_dict.get(source_id, set())
        if len(true_targets) == 0:
            continue
        
        metrics = evaluate_node(
            source_id, true_targets, all_node_ids, entity_to_idx,
            all_emb, operator, comp, all_neighbors, 
            num_negatives_per_true, dim, k_values
        )
        
        if metrics is not None:
            entity_name = df_valid[df_valid["entity_id"] == source_id]["entity_name"].iloc[0] if len(df_valid[df_valid["entity_id"] == source_id]) > 0 else source_id
            metrics["entity_name"] = entity_name
            all_results.append(metrics)
    
    if len(all_results) == 0:
        return None
    
    results_df = pd.DataFrame(all_results)
    
    all_scores_list = []
    all_labels_list = []
    for _, row in results_df.iterrows():
        if "scores" in row and "labels" in row:
            all_scores_list.extend(row["scores"])
            all_labels_list.extend(row["labels"])
    
    binary_metrics = {"bin_threshold": None, "bin_precision": None, 
                     "bin_recall": None, "bin_f1": None}
    
    if all_scores_list and all_labels_list:
        all_scores = np.array(all_scores_list)
        all_labels = np.array(all_labels_list)
        binary_metrics = compute_binary_metrics(all_scores, all_labels)
        
        if binary_metrics:
            plot_per_file_metrics(
                results_df, all_scores, all_labels, binary_metrics["bin_threshold"],
                csv_file.stem, plots_dir, k_values
            )
    
    results_df_export = results_df.drop(columns=['scores', 'labels'], errors='ignore')
    output_file = Path(output_dir) / f"{csv_file.stem}_multi_positive_improved.csv"
    results_df_export.to_csv(output_file, index=False)
    
    summary = {
        "results_df": results_df,
        "num_nodes": len(results_df),
        "avg_links_per_node": float(results_df['num_true'].mean()),
        "mean_rank": float(results_df['mean_rank'].mean()),
        "median_rank": float(results_df['median_rank'].median()),
        "map": float(results_df['map'].mean()),
        "mrr": float(results_df['mrr'].mean()),
        "hit@1": float(results_df['hit@1'].mean()),
        "hit@5": float(results_df['hit@5'].mean()),
        "hit@10": float(results_df['hit@10'].mean()),
        "recall@10": float(results_df['recall@10'].mean()),
        "precision@10": float(results_df['precision@10'].mean()),
        "f1@10": float(results_df['f1@10'].mean()),
        "ndcg@10": float(results_df['ndcg@10'].mean()),
    }
    summary.update(binary_metrics)
    
    return summary


def create_summary_table(all_results_by_file, output_dir):
    summary_data = []
    for file_name, data in all_results_by_file.items():
        row = {
            "File": file_name,
            "Nodes": data["num_nodes"],
            "Links/Node": f"{data['avg_links_per_node']:.1f}",
            "Mean_Rank": f"{data['mean_rank']:.1f}",
            "Median_Rank": f"{data['median_rank']:.1f}",
            "MAP": f"{data['map']:.4f}",
            "MRR": f"{data['mrr']:.4f}",
            "Hit@1": f"{data['hit@1']:.4f}",
            "Hit@5": f"{data['hit@5']:.4f}",
            "Hit@10": f"{data['hit@10']:.4f}",
            "Recall@10": f"{data['recall@10']:.4f}",
            "Precision@10": f"{data['precision@10']:.4f}",
            "F1@10": f"{data['f1@10']:.4f}",
            "NDCG@10": f"{data['ndcg@10']:.4f}",
        }
        
        if data.get('bin_threshold') is not None:
            row["Threshold"] = f"{data['bin_threshold']:.6f}"
            row["Bin_Precision"] = f"{data['bin_precision']:.4f}"
            row["Bin_Recall"] = f"{data['bin_recall']:.4f}"
            row["Bin_F1"] = f"{data['bin_f1']:.4f}"
        else:
            row["Threshold"] = "N/A"
            row["Bin_Precision"] = "N/A"
            row["Bin_Recall"] = "N/A"
            row["Bin_F1"] = "N/A"
        
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = Path(output_dir) / "multi_positive_summary_improved.csv"
    summary_df.to_csv(summary_file, index=False)
    return summary_df

