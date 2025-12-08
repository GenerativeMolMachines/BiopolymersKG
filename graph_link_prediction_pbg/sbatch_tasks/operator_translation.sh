#!/bin/bash

dvc exp run -S "operator=translation" -S "train.workers=40"