#!/bin/bash

uv run dvc exp run -S "operator=diagonal" -S "train.workers=25"
