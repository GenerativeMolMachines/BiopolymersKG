DIM = 400
COMPARATOR = "cos"
NUM_NEGATIVES_PER_TRUE = 150
K_VALUES = [1, 5, 10, 50, 100]

TEST_TSV = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/test.tsv"
TRAIN_TSV = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/train.tsv"
VAL_TSV = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/val.tsv"

ENTITY_JSON = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/data/partitions/entity_names_molecules_0.json"
EMB_H5 = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/results/cos_diagonal_checkpoint/epoch_15/embeddings_molecules_0.v240.h5"
MODEL_H5 = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/results/cos_diagonal_checkpoint/epoch_15/model.v240.h5"

CSV_FILES = [
    "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/antibiotic_10k.csv",
    "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/cancer_proteins.csv",
    "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/important.csv",
    "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/pharma_proteins.csv",
    "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/resources/toxic_ptoreins.csv",
]

OUTPUT_DIR = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/metrics/multi_positive"
PLOTS_DIR = "/mnt/tank/scratch/pbogdanov/graph_link_prediction_pbg/metrics/multi_positive/plots"

