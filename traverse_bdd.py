import os
import argparse
from typing import Any
from collections import defaultdict

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.bdd_metamodel.models import BDDModel
from flamapy.metamodels.bdd_metamodel.transformations import FmToBDD, PNGWriter
from flamapy.metamodels.bdd_metamodel.operations import (
    BDDConfigurationsNumber, 
    BDDProductDistribution
)

def traverse(bdd_model: BDDModel, node: Any, mark: dict[int, bool], tabs: int, complemented: bool) -> None:
    print(f'{" " * tabs}{bdd_model.pretty_node_str(node, complemented)}')
    node_id = bdd_model.get_value(node, complemented)
    mark[node_id] = not mark[node_id]
    if not bdd_model.is_terminal_node(node):
        low = bdd_model.get_low_node(node)
        low_id = bdd_model.get_value(low, complemented ^ bdd_model.negated(low))
        if mark[node_id] != mark[low_id]:
            print(f'{" " * tabs} Low:')
            traverse(bdd_model, low, mark, tabs + 2, complemented)
        high = bdd_model.get_high_node(node)
        high_id = bdd_model.get_value(high, complemented)
        if mark[node_id] != mark[high_id]:
            print(f'{" " * tabs} High:')
            traverse(bdd_model, high, mark, tabs + 2, complemented ^ bdd_model.negated(high))


def traverse_bdd(bdd_model: BDDModel) -> None:
    mark: dict[int, bool] = defaultdict(bool)
    traverse(bdd_model, bdd_model.root, mark, 0, bdd_model.negated(bdd_model.root))



def main(fm_path: str):
    path, filename = os.path.split(fm_path)
    filename = '.'.join(filename.split('.')[:-1])

    fm = UVLReader(fm_path).transform()
    bdd_model = FmToBDD(fm).transform()
    n_configs = BDDConfigurationsNumber().execute(bdd_model).get_result()
    print(f'#Configs: {n_configs}')
    print(f'BDD: {bdd_model}')

    PNGWriter(f'{filename}.png', bdd_model).transform()

    traverse_bdd(bdd_model)

    dist = BDDProductDistribution().execute(bdd_model).get_result()
    print(f'Dist: {dist}')
    print(f'#Products: {sum(dist)}')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Characterize feature model complexity.')
    parser.add_argument(metavar='fm', dest='fm_filepath', type=str, help='Input feature model (.uvl).')
    args = parser.parse_args()

    main(args.fm_filepath)


