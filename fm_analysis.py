import os
import argparse
from typing import Any

from alive_progress import alive_bar
import matplotlib.pyplot as plt
import seaborn as sns

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.bdd_metamodel.transformations import FmToBDD
from flamapy.metamodels.bdd_metamodel.operations import (
    BDDProductDistribution, 
    BDDFeatureInclusionProbability,
    BDDConfigurationsNumber
)

import utils


def descriptive_statistics(prod_dist: list[int]) -> dict[str, Any]:
    total_elements = sum(prod_dist)
    if total_elements == 0:
        return {
            'Mean': 0,
            'Standard deviation': 0,
            'Median': 0,
            'Median absolute deviation': 0,
            'Mode': 0,
            'Min': None,
            'Max': None,
            'Range': 0
        }

    total_sum = 0
    running_total = 0
    median1 = None
    median2 = None
    median_pos1 = (total_elements + 1) // 2
    median_pos2 = (total_elements + 2) // 2
    min_val = None
    max_val = None
    mode = None
    mode_count = 0

    sum_squared_diff = 0
    abs_deviation_total = 0
    abs_deviation_running_total = 0
    mad1 = None
    mad2 = None
    mad_pos1 = (total_elements + 1) // 2
    mad_pos2 = (total_elements + 2) // 2

    for i, count in enumerate(prod_dist):
        if count > 0:
            if min_val is None:
                min_val = i
            max_val = i
            
            total_sum += i * count
            running_total += count
            
            if mode is None or count > mode_count:
                mode = i
                mode_count = count
            
            if median1 is None and running_total >= median_pos1:
                median1 = i
            if median2 is None and running_total >= median_pos2:
                median2 = i

    mean = total_sum / total_elements
    median = (median1 + median2) / 2
    
    running_total = 0
    for i, count in enumerate(prod_dist):
        if count > 0:
            deviation = abs(i - median)
            abs_deviation_total += deviation * count
            running_total += count
            
            sum_squared_diff += count * (i - mean) ** 2
            
            abs_deviation_running_total += count
            if mad1 is None and abs_deviation_running_total >= mad_pos1:
                mad1 = deviation
            if mad2 is None and abs_deviation_running_total >= mad_pos2:
                mad2 = deviation
            if mad1 is not None and mad2 is not None:
                break

    std_dev = (sum_squared_diff / total_elements) ** 0.5
    mad = (mad1 + mad2) / 2 if mad1 is not None and mad2 is not None else 0
    
    statistics = {
        'Mean': mean,
        'Standard deviation': std_dev,
        'Median': median,
        'Median absolute deviation': mad,
        'Mode': mode,
        'Min': min_val,
        'Max': max_val,
        'Range': max_val - min_val if min_val is not None and max_val is not None else 0
    }
    return statistics

def plot_product_distribution(data: list[int]):
    # Generate an array of indices
    indices = range(len(data))
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Plot the smooth histogram using seaborn's kdeplot
    sns.kdeplot(x=indices, weights=data, bw_adjust=0.5, fill=True)
    
    # Set labels and title
    plt.xlabel('#Features')
    plt.ylabel("Products' density")
    plt.title('Product distribution')
    # Set the x-axis minimum value if specified
    plt.xlim(left=0)

    # Show the plot
    plt.show()


def plot_feature_inclusion_probabilities(probabilities):
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Create a dictionary to store counts for each unique probability
    probability_counts = {}
    for prob in probabilities:
        probability_counts[prob] = probability_counts.get(prob, 0) + 1
    
    # Plot the smooth histogram using seaborn's kdeplot
    percentages = [p/len(probabilities)*100 for p in probability_counts.values()]
    counts, bins, _ = plt.hist(x=probability_counts.keys(), weights=percentages, bins=len(probabilities), edgecolor='black', alpha=0.7)
    #sns.kdeplot(probabilities, bw_adjust=0.05, fill=True)
    
    # Highlight the area for each unique probability
    for prob, count in probability_counts.items():
        if prob == 0.5:
            plt.axvspan(prob - 0.025, prob + 0.025, color='yellow', alpha=0.3, label=f'Pure optional features (p=0.5): {count}')
        elif prob == 1.00:
            plt.axvspan(prob - 0.025, prob + 0.025, color='green', alpha=0.3, label=f'Core features (p=1.0): {count}')
        elif prob == 0.00:
            plt.axvspan(prob - 0.025, prob + 0.025, color='red', alpha=0.3, label=f'Dead features (p=0.0): {count}')

    # Add legend
    plt.legend()

    # Set labels and title
    plt.xlabel('Feature probability of being included in a valid configuration')
    plt.ylabel('%Features')
    plt.title('Feature probability distribution')
    
    # Set x-axis limits to ensure it ranges from 0 to 100
    plt.xlim(0, 1)

    # Set y-axis limits to ensure it ranges from 0 to 100
    max_y = max(percentages)
    max_y = max_y + (10 - max_y % 10)
    plt.ylim(0, min(100, max_y))
    
    # Show the plot
    plt.show()


def main(fm_path: str):
    path, filename = os.path.split(fm_path)
    filename = '.'.join(filename.split('.')[:-1])

    with alive_bar(title=f'Reading FM {fm_path}...') as bar: 
        fm = UVLReader(fm_path).transform()
        bar()

    with alive_bar(title=f'Transforming FM to BDD...') as bar: 
        bdd_model = FmToBDD(fm).transform()
        bar()

    with alive_bar(title=f'Calculating number of configurations...') as bar:     
        n_configs = BDDConfigurationsNumber().execute(bdd_model).get_result()
        bar()
    
    print(f'Number of features the SPL manages: {len(fm.get_features())}')
    print(f'Number of constraints the SPL manages: {len(fm.get_constraints())}')
    print(f'Number of valid configurations that can be derived: {utils.int_to_scientific_notation(n_configs) if n_configs > 1e6 else n_configs} {"(" + str(n_configs) + ")" if n_configs > 1e6 else ""}')
    #print(f'Homogeneity of configurations: ??')

    with alive_bar(title=f'Calculating Product distribution...') as bar: 
        prod_dist_op = BDDProductDistribution().execute(bdd_model)
        dist = prod_dist_op.product_distribution()
        bar()
    print(f'Product distribution: {dist}')
    plot_product_distribution(dist)

    with alive_bar(title=f'Calculating Feature inclusion probabilities...') as bar:
        fip = BDDFeatureInclusionProbability().execute(bdd_model).get_result()
        bar()
    print('Feature Inclusion Probabilities:')
    for feat, prob in fip.items():
        print(f'{feat}: {prob}')
    plot_feature_inclusion_probabilities(list(fip.values()))

    with alive_bar(title=f'Calculating descriptive analysis...') as bar:
        dist_stats = descriptive_statistics(dist)
        bar()
    print('Descriptive analysis (number of features for a product):')
    for ds, dv in dist_stats.items():
        print(f' |-{ds}: {dv}')

    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Characterize feature model complexity.')
    parser.add_argument(metavar='fm', dest='fm_filepath', type=str, help='Input feature model (.uvl).')
    args = parser.parse_args()

    main(args.fm_filepath)
