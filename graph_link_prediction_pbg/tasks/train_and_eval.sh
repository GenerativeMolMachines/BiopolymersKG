#!/bin/bash
set -euo pipefail

BIN="/mnt/tank/scratch/pbogdanov/graph/.venv/bin"
BASE="/mnt/tank/scratch/pbogdanov/graph/toy_pbg"

CONFIG="$BASE/configs/train.py"

EDGE_PATH_TRAIN="$BASE/data/partitions/train_partitioned"      
EDGE_PATH_VALID="$BASE/data/partitions/val_partitioned"
EDGE_PATH_TEST="$BASE/data/partitions/test_partitioned"

echo "== TRAIN =="
"$BIN/torchbiggraph_train"\
    "$CONFIG" \
    -p workers=8 \
    -p edge_paths="$EDGE_PATH_TRAIN"

echo "== EVAL VALID =="
"$BIN/torchbiggraph_eval" \
    "$CONFIG" \
    -p workers=8 \
    -p edge_paths="$EDGE_PATH_VALID"

echo "== EVAL TEST =="
"$BIN/torchbiggraph_eval" \
    "$CONFIG" \
    -p workers=8 \
    -p edge_paths="$EDGE_PATH_TEST"

echo "== EVAL TRAIN =="
"$BIN/torchbiggraph_eval" \
    "$CONFIG" \
    -p workers=8 \
    -p edge_paths="$EDGE_PATH_TRAIN"

echo "== DONE =="