#!/bin/bash

set -euo pipefail

BIN="/mnt/tank/scratch/pbogdanov/graph/.venv/bin"

"$BIN/torchbiggraph_import_from_tsv" \
    --lhs-col=0 --rel-col=1 --rhs-col=2 \
    configs/import_data.py \
    data/resources/train.tsv \
    data/resources/test.tsv \
    data/resources/val.tsv