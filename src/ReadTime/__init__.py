# Remove unused imports
import os
import time
from typing import Dict, Tuple

from rich.console import Console

size = 1000

rich_console = Console(color_system="auto")

from src.Task1 import Branch, BranchPredictor

filesFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'txt'))
file_list = [f for f in os.listdir(filesFolder) if f.endswith('.txt')]
file = os.path.join(filesFolder, file_list[1])

# time at the start of program is noted
start = time.time()

branch = Branch(file)
predictor = BranchPredictor(size)
print("Read time in seconds: ", (time.time() - start))

print(f"Processing file: {file} with size: {size}")
start = time.time()

# Correct initialization of dictionaries
aux: Dict[str, Tuple[str, str]] = {}
predictions: Dict[str, Tuple[str, str]] = {}
replaced = 0
total = 0
correct = 0

for trace in branch:
    total += 1
    address, taken = trace
    if address in aux:
        prediction, _ = aux[address]
        predictions[address] = (prediction, taken)
        # Move the existing item to the end (most recently used)
        aux[address] = aux.pop(address)
        if prediction == taken:
            correct += 1
    else:
        predictions[address] = ('N', taken)
        if len(aux) >= size:
            # Remove the least recently used item (first item)
            replaced += 1
            aux.pop(next(iter(aux)))
        if 'N' == taken:
            correct += 1
    aux[address] = (taken, taken)  # Use the actual outcome as the new prediction

end = time.time()

for address, (prediction, actual) in list(predictions.items())[:10]:
    rich_console.print(f"{address}: Predicted {prediction}, Actual {actual}")

accuracy = correct / total * 100
print(f"Total branches: {total}, Replaced branches: {replaced} (with size {size})")
print(f"Correct predictions: {correct}")
print(f"Accuracy: {accuracy:.2f}%")
print("Execution time in seconds: ", (end - start))