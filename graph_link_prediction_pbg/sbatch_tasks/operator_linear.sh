#!/bin/bash

dvc exp run -S "operator=linear" -S "train.workers=40"