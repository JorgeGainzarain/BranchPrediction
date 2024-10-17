from colorama import Fore, Style

from src.Task1 import Branch
from src.Task1.History import History


class BranchPredictor:
    history_map: History

    def __init__(self, max_size: int):
        self.history_map = History(max_size)

    def predict(self, branch_address: str) -> str:
        return self.history_map.get(branch_address)

    def update(self, branch_address: str, actual_outcome: str):
        self.history_map.set(branch_address, actual_outcome)

    def predictBranch(self, branch: Branch):
        correct_predictions = 0

        for address, taken in branch:
            # Predict the branch outcome based on the last `maxSize` predictions.
            prediction = self.predict(address)
            # Update the predictor with the current branch outcome.
            self.update(address, taken)

            # Update the accuracy
            predicted = prediction == taken
            correct_predictions += 1 if predicted else 0

            # Show the results for each branch instruction.
            equality = f"{Fore.GREEN}==" if predicted else f"{Fore.RED}!="
            #print(f"{address} : ({prediction} {equality}{Style.RESET_ALL} {taken})")

        return correct_predictions