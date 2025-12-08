import torch
from torchbiggraph.model import DotComparator, CosComparator, L2Comparator, SquaredL2Comparator


def get_comparator(name):
    comparators = {
        "cos": CosComparator(),
        "dot": DotComparator(),
        "l2": L2Comparator(),
        "squared_l2": SquaredL2Comparator(),
    }
    if name not in comparators:
        raise ValueError(f"Unknown comparator: {name}")
    return comparators[name]

