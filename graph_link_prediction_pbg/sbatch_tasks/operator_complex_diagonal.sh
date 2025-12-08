#!/bin/bash

dvc exp run -S "operator=complex_diagonal" -S "train.workers=40"