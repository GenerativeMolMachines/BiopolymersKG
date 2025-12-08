import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def setup_plot_style():
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except:
        try:
            plt.style.use('seaborn-darkgrid')
        except:
            plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10


def plot_per_file_metrics(results_df, all_scores, all_labels, best_threshold, 
                          csv_file_stem, plots_dir, k_values):
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Metrics for {csv_file_stem}', fontsize=16, fontweight='bold')
    
    from sklearn.metrics import precision_recall_curve
    prec, rec, _ = precision_recall_curve(all_labels, all_scores)
    
    ax1 = axes[0, 0]
    ax1.plot(rec, prec, linewidth=2)
    ax1.set_xlabel('Recall', fontsize=12)
    ax1.set_ylabel('Precision', fontsize=12)
    ax1.set_title('Precision-Recall Curve', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[0, 1]
    all_ranks = []
    for ranks_list in results_df['ranks']:
        all_ranks.extend(ranks_list)
    log_ranks = np.log10(np.array(all_ranks) + 1)
    ax2.hist(log_ranks, bins=50, edgecolor='black', alpha=0.7)
    ax2.set_xlabel('log10(Rank + 1)', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title('Rank Distribution', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    ax3 = axes[1, 0]
    available_k = [k for k in k_values if f'hit@{k}' in results_df.columns]
    if available_k:
        hit_at_k = [results_df[f'hit@{k}'].mean() for k in available_k]
        recall_at_k = [results_df[f'recall@{k}'].mean() for k in available_k]
        precision_at_k = [results_df[f'precision@{k}'].mean() for k in available_k]
        ndcg_at_k = [results_df[f'ndcg@{k}'].mean() for k in available_k]
        
        ax3.plot(available_k, hit_at_k, marker='o', linewidth=2, label='Hit@K', markersize=8)
        ax3.plot(available_k, recall_at_k, marker='s', linewidth=2, label='Recall@K', markersize=8)
        ax3.plot(available_k, precision_at_k, marker='^', linewidth=2, label='Precision@K', markersize=8)
        ax3.plot(available_k, ndcg_at_k, marker='d', linewidth=2, label='NDCG@K', markersize=8)
    ax3.set_xlabel('K', fontsize=12)
    ax3.set_ylabel('Metric Value', fontsize=12)
    ax3.set_title('Metrics @K', fontsize=13, fontweight='bold')
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    
    ax4 = axes[1, 1]
    pos_scores = all_scores[all_labels == 1]
    neg_scores = all_scores[all_labels == 0]
    if len(pos_scores) > 10000:
        pos_scores = np.random.choice(pos_scores, 10000, replace=False)
    if len(neg_scores) > 10000:
        neg_scores = np.random.choice(neg_scores, 10000, replace=False)
    
    ax4.hist(neg_scores, bins=50, alpha=0.6, label='Negatives', color='red', edgecolor='black')
    ax4.hist(pos_scores, bins=50, alpha=0.6, label='Positives', color='green', edgecolor='black')
    ax4.axvline(x=best_threshold, color='blue', linestyle='--', linewidth=2, label=f'Threshold: {best_threshold:.4f}')
    ax4.set_xlabel('Score', fontsize=12)
    ax4.set_ylabel('Frequency', fontsize=12)
    ax4.set_title('Score Distribution', fontsize=13, fontweight='bold')
    ax4.legend(loc='best')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_file = plots_dir / f"{csv_file_stem}_metrics.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(plot_file)


def plot_comparison_metrics(all_results_by_file, plots_dir, k_values):
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    file_names = list(all_results_by_file.keys())
    colors = plt.cm.tab10(np.linspace(0, 1, len(file_names)))
    
    first_file_data = all_results_by_file[file_names[0]]
    available_k_vals = [k for k in k_values if f'hit@{k}' in first_file_data]
    if not available_k_vals:
        available_k_vals = k_values
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Comparison of Metrics Across CSV Files', fontsize=16, fontweight='bold')
    
    for metric_idx, metric_name in enumerate(['hit@', 'recall@', 'precision@', 'ndcg@']):
        ax = axes[metric_idx // 2, metric_idx % 2]
        for i, file_name in enumerate(file_names):
            data = all_results_by_file[file_name]
            values = []
            k_plot = []
            for k in available_k_vals:
                key = f'{metric_name}{k}'
                if key in data:
                    values.append(data[key])
                    k_plot.append(k)
            if values:
                markers = ['o', 's', '^', 'd']
                ax.plot(k_plot, values, marker=markers[metric_idx], linewidth=2, 
                       label=file_name[:20], color=colors[i], markersize=6)
        ax.set_xlabel('K', fontsize=12)
        ax.set_ylabel(metric_name.replace('@', '@').title(), fontsize=12)
        ax.set_title(f'{metric_name.replace("@", "@").title()} Across Files', fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_file = plots_dir / "comparison_metrics_at_k.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(plot_file)


def plot_main_metrics(all_results_by_file, plots_dir):
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    file_names = list(all_results_by_file.keys())
    file_names_short = [name[:15] + '...' if len(name) > 15 else name for name in file_names]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Comparison of Main Metrics Across CSV Files', fontsize=16, fontweight='bold')
    
    x = np.arange(len(file_names))
    width = 0.35
    
    ax1 = axes[0, 0]
    map_values = [all_results_by_file[f]['map'] for f in file_names]
    mrr_values = [all_results_by_file[f]['mrr'] for f in file_names]
    ax1.bar(x - width/2, map_values, width, label='MAP', alpha=0.8)
    ax1.bar(x + width/2, mrr_values, width, label='MRR', alpha=0.8)
    ax1.set_xlabel('File', fontsize=12)
    ax1.set_ylabel('Value', fontsize=12)
    ax1.set_title('MAP and MRR', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(file_names_short, rotation=45, ha='right')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2 = axes[0, 1]
    bin_precision_values = []
    bin_recall_values = []
    bin_f1_values = []
    valid_files = []
    for f in file_names:
        data = all_results_by_file[f]
        if data.get('bin_precision') is not None:
            bin_precision_values.append(data['bin_precision'])
            bin_recall_values.append(data['bin_recall'])
            bin_f1_values.append(data['bin_f1'])
            valid_files.append(f)
    
    if valid_files:
        x_bin = np.arange(len(valid_files))
        valid_files_short = [name[:15] + '...' if len(name) > 15 else name for name in valid_files]
        ax2.bar(x_bin - width/3, bin_precision_values, width/1.5, label='Precision', alpha=0.8)
        ax2.bar(x_bin, bin_recall_values, width/1.5, label='Recall', alpha=0.8)
        ax2.bar(x_bin + width/3, bin_f1_values, width/1.5, label='F1', alpha=0.8)
        ax2.set_xlabel('File', fontsize=12)
        ax2.set_ylabel('Value', fontsize=12)
        ax2.set_title('Binary Metrics', fontsize=13, fontweight='bold')
        ax2.set_xticks(x_bin)
        ax2.set_xticklabels(valid_files_short, rotation=45, ha='right')
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3, axis='y')
    else:
        ax2.text(0.5, 0.5, 'Binary metrics\nnot available', 
                ha='center', va='center', fontsize=14, transform=ax2.transAxes)
        ax2.set_title('Binary Metrics', fontsize=13, fontweight='bold')
    
    ax3 = axes[1, 0]
    mean_rank_values = [all_results_by_file[f]['mean_rank'] for f in file_names]
    median_rank_values = [all_results_by_file[f]['median_rank'] for f in file_names]
    ax3.bar(x - width/2, mean_rank_values, width, label='Mean Rank', alpha=0.8)
    ax3.bar(x + width/2, median_rank_values, width, label='Median Rank', alpha=0.8)
    ax3.set_xlabel('File', fontsize=12)
    ax3.set_ylabel('Rank', fontsize=12)
    ax3.set_title('Mean and Median Ranks', fontsize=13, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(file_names_short, rotation=45, ha='right')
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_yscale('log')
    
    ax4 = axes[1, 1]
    num_nodes_values = [all_results_by_file[f]['num_nodes'] for f in file_names]
    avg_links_values = [all_results_by_file[f]['avg_links_per_node'] for f in file_names]
    ax4_twin = ax4.twinx()
    ax4.bar(x - width/2, num_nodes_values, width, label='Number of Nodes', alpha=0.8, color='skyblue')
    ax4_twin.bar(x + width/2, avg_links_values, width, label='Avg Links per Node', alpha=0.8, color='coral')
    ax4.set_xlabel('File', fontsize=12)
    ax4.set_ylabel('Number of Nodes', fontsize=12, color='skyblue')
    ax4_twin.set_ylabel('Avg Links per Node', fontsize=12, color='coral')
    ax4.set_title('Nodes and Links', fontsize=13, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(file_names_short, rotation=45, ha='right')
    ax4.tick_params(axis='y', labelcolor='skyblue')
    ax4_twin.tick_params(axis='y', labelcolor='coral')
    ax4.grid(True, alpha=0.3, axis='y')
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='best')
    
    plt.tight_layout()
    plot_file = plots_dir / "comparison_main_metrics.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(plot_file)

