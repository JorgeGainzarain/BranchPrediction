import collections
import os
from typing import List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from src.Task1.Branch import Branch

filesFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'txt'))
folderPatterns = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'patterns'))

def analyze_patterns(branch: Branch):
    addresses, outcomes = zip(*branch)

    # 1. Frequency Analysis
    address_freq = collections.Counter(addresses)
    outcome_freq = collections.Counter(outcomes)

    print("Top 10 most common branch addresses:")
    for addr, freq in address_freq.most_common(10):
        print(f"Address: {addr}, Frequency: {freq}")

    print(f"\nTaken branches: {outcome_freq['T']}")
    print(f"Not taken branches: {outcome_freq['N']}")

    # 2. N-gram Analysis (for 2-grams)
    bigrams = list(zip(branch[:-1], branch[1:]))
    bigram_freq = collections.Counter(bigrams)

    print("\nTop 5 most common branch address pairs:")
    for pair, freq in bigram_freq.most_common(5):
        print(f"Pair: {pair}, Frequency: {freq}")

    # 3. Temporal Analysis
    plot_temporal_pattern(addresses, outcomes)

    # 4. Correlation Analysis
    plot_correlation_heatmap(addresses, outcomes)

def plot_temporal_pattern(addresses: List[str], outcomes: List[str]):
    unique_addresses = list(set(addresses))
    address_indices = [unique_addresses.index(addr) for addr in addresses]
    taken = [1 if outcome == 'T' else 0 for outcome in outcomes]

    plt.figure(figsize=(15, 6))
    plt.scatter(range(len(addresses)), address_indices, c=taken, cmap='coolwarm', alpha=0.5, s=1)
    plt.colorbar(label='Taken (1) / Not Taken (0)')
    plt.xlabel('Branch Sequence')
    plt.ylabel('Unique Branch Addresses')
    plt.title('Temporal Pattern of Branch Behavior')
    plt.savefig(os.path.join(folderPatterns,'temporal_pattern.png'))
    plt.close()

def plot_correlation_heatmap(addresses: List[str], outcomes: List[str]):
    unique_addresses = list(set(addresses))[:20]  # Limit to top 20 for visibility
    correlation_matrix = [[0 for _ in range(len(unique_addresses))] for _ in range(len(unique_addresses))]

    for i, addr1 in enumerate(unique_addresses):
        for j, addr2 in enumerate(unique_addresses):
            if i != j:
                correlation = calculate_correlation(addresses, outcomes, addr1, addr2)
                correlation_matrix[i][j] = correlation

    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', xticklabels=unique_addresses, yticklabels=unique_addresses)
    plt.title('Branch Address Correlation Heatmap')
    plt.savefig(os.path.join(folderPatterns,'correlation_heatmap.png'))
    plt.close()

def calculate_correlation(addresses: List[str], outcomes: List[str], addr1: str, addr2: str) -> float:
    outcomes1 = [outcomes[i] for i, addr in enumerate(addresses) if addr == addr1]
    outcomes2 = [outcomes[i] for i, addr in enumerate(addresses) if addr == addr2]

    if not outcomes1 or not outcomes2:
        return 0

    taken1 = sum(1 for outcome in outcomes1 if outcome == 'T') / len(outcomes1)
    taken2 = sum(1 for outcome in outcomes2 if outcome == 'T') / len(outcomes2)

    return abs(taken1 - taken2)

# Usage
def analyze_branch_patterns(branch: Branch):
    analyze_patterns(branch)
    print("Pattern analysis complete. Check 'temporal_pattern.png' and 'correlation_heatmap.png' for visualizations.")


if __name__ == "__main__":
    branch_file_path = os.path.join(filesFolder, 'gcc-10K.txt')
    branch = Branch(branch_file_path)
    analyze_branch_patterns(branch)