import math

from colorama import Fore, Style
from rich.table import Table
from rich import box
from src.Task1 import Branch
from src.Task1.History import History
from rich.console import Console
console = Console(color_system="auto")

class BranchPredictor:
    history_map: History
    default_pred: str = 'N'

    correct: int = 0
    incorrect: int = 0
    correct_predictions: int = 0
    miss_predictions: int = 0
    traces: int = 0
    addressReplacement: int = 0
    accurateReplacements: int = 0

    def __init__(self, max_size: int):
        self.history_map = History(max_size)

    def predict(self, branch_address: str) -> str:
        return self.history_map.get(branch_address)

    def update(self, branch_address: str, prediction: str, actual_outcome: str):
        was_replaced, was_accurate = self.history_map.set(branch_address, prediction, actual_outcome)
        if was_replaced:
            self.addressReplacement += 1

        if was_accurate:
            self.accurateReplacements += 1

    def predictBranch(self, branch: Branch, verbose: bool = False, progress: bool = True) -> Table:
        correct_predictions = correct = incorrect = miss_predictions = traces = address_replacement = accurate_replacements = 0
        total_branches = len(branch)
        progress_step = max(0, total_branches // 10)
        next_progress = progress_step

        history_get = self.history_map.get
        history_set = self.history_map.set
        default_pred = self.default_pred

        for index, (address, taken) in enumerate(branch, 0):
            traces += 1
            prediction = history_get(address)
            value = default_pred if prediction == '' else prediction

            was_replaced, was_accurate = history_set(address, prediction, taken)
            address_replacement += was_replaced
            accurate_replacements += was_accurate

            if prediction:  # Valid prediction
                if prediction == taken:
                    correct_predictions += 1
                else:
                    miss_predictions += 1

            if value == taken:
                correct += 1
            else:
                incorrect += 1

            if verbose:
                equality = "==" if value == taken else "!="
                print(f"{address} : ({value} {equality} {taken})")

            # Log progress every 10%
            if index == next_progress and progress:
                progress_percentage = math.ceil((index * 100) / total_branches)
                console.print(f"Progress: {progress_percentage}% - Processed {index} out of {total_branches} branches")
                next_progress += progress_step

        self.correct_predictions = correct_predictions
        self.correct = correct
        self.incorrect = incorrect
        self.miss_predictions = miss_predictions
        self.traces = traces
        self.addressReplacement = address_replacement
        self.accurateReplacements = accurate_replacements

        return self.analysisTable()

    def analysisTable(self) -> Table:
        table = Table(title="Branch Prediction Results", box=box.DOUBLE_EDGE)
        table.add_column("Metric", justify="right")
        table.add_column("Value")
        table.add_column("Total %")

        predicted = self.correct_predictions + self.miss_predictions
        default = self.traces - predicted
        overall_accuracy = self.correct / self.traces
        predicted_accuracy = self.correct_predictions / predicted if predicted > 0 else 0
        default_accuracy = (self.correct - self.correct_predictions) / default if default > 0 else 0
        accuracy_diff = predicted_accuracy - default_accuracy

        table.add_row("Total Branches", str(self.traces), "100%", end_section=True)

        table.add_row("Predicted Branches", str(predicted), f"{predicted/self.traces:.2%}")
        table.add_row("Default Branches", str(default), f"{default / self.traces:.2%}", end_section=True)

        table.add_row("Correct Predicted", str(self.correct_predictions))
        table.add_row("Miss Predicted", str(self.miss_predictions))
        table.add_row("Correct Defaults", str(self.correct - self.correct_predictions), end_section=True)

        table.add_row("Overall Accuracy", "", f"{overall_accuracy:.2%}", style="bold")
        table.add_row("Predicted Accuracy", f"{predicted_accuracy:.2%}",
                      f"{self.correct_predictions/self.traces:.2%}", style="bold")
        table.add_row("Default Accuracy", f"{default_accuracy:.2%}",
                      f"{(self.correct - self.correct_predictions)/self.traces:.2%}",
                      style="bold", end_section=True)

        table.add_row("Predicted vs Default", f"+{accuracy_diff:.2%}", style="bold green", end_section=True)

        # Debug Metrics
        table.add_row("Address Replacements", str(self.addressReplacement), f"{self.addressReplacement / self.traces:.2%}")

        table.add_row("Replacement Skips", str(self.accurateReplacements), f"{self.accurateReplacements / self.traces:.2%}")

        return table