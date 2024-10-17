from colorama import Fore, Style
from rich.table import Table
from rich import box

from src.Task1 import Branch
from src.Task1.History import History

class BranchPredictor:
    history_map: History
    default_pred: str = 'N'

    correct: int = 0
    incorrect: int = 0
    correct_predictions: int = 0
    miss_predictions: int = 0
    traces: int = 0

    def __init__(self, max_size: int):
        self.history_map = History(max_size)

    def predict(self, branch_address: str) -> str:
        return self.history_map.get(branch_address)

    def update(self, branch_address: str, actual_outcome: str):
        self.history_map.set(branch_address, actual_outcome)

    def predictBranch(self, branch: Branch, verbose: bool = False) -> Table:
        self.correct_predictions = 0
        self.correct = 0
        self.incorrect = 0
        self.miss_predictions = 0
        self.traces = 0

        for address, taken in branch:
            self.traces += 1
            prediction = self.predict(address)
            value = self.default_pred if prediction == '' else prediction

            self.update(address, taken)

            if prediction != '':  # Valid prediction
                if prediction == taken:
                    self.correct_predictions += 1
                else:
                    self.miss_predictions += 1
            
            if value == taken:
                self.correct += 1
            else:
                self.incorrect += 1

            if verbose:
                equality = f"{Fore.GREEN}==" if value == taken else f"{Fore.RED}!="
                print(f"{address} : ({value} {equality}{Style.RESET_ALL} {taken})")

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



        table.add_row("Overall Accuracy", f"{overall_accuracy:.2%}", f"{overall_accuracy:.2%}", style="bold")
        table.add_row("Predicted Accuracy", f"{predicted_accuracy:.2%}",
                      f"{self.correct_predictions/self.traces:.2%}", style="bold")
        table.add_row("Default Accuracy", f"{default_accuracy:.2%}",
                      f"{(self.correct - self.correct_predictions)/self.traces:.2%}",
                      style="bold", end_section=True)


        table.add_row("Predicted vs Default", f"+{accuracy_diff:.2%}", style="bold green")

        return table