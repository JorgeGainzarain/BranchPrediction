from collections import OrderedDict
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TaskID
from rich.console import Console
from src.models.Branch import Branch

class TwoBitPredictor:
    MAX_HISTORY_SIZE = 16  # Maximum number of predictions to keep in history

    def __init__(self, size):
        self.history = OrderedDict()
        self.console = Console()
        self.MAX_HISTORY_SIZE = size  # Set maximum history size based on the provided predictor size

    def predict(self, address):
        state = self.history.get(address, 0)  # Default state is 0 (Strongly Not Taken)
        return 'T' if state >= 2 else 'N'

    def update(self, address, outcome):
        if address in self.history:
            state = self.history[address]
            del self.history[address]  # Remove to update its position (LRU)
        elif len(self.history) >= self.MAX_HISTORY_SIZE:
            self.history.popitem(last=False)  # Remove least recently used item
            state = 0  # New state for new address
        else:
            state = 0  # New state for new address

        if outcome == 'T':
            state = min(3, state + 1)  # Increment state, max is 3 (Strongly Taken)
        else:
            state = max(0, state - 1)  # Decrement state, min is 0 (Strongly Not Taken)

        self.history[address] = state  # Add/Update the prediction state

    def predictBranch(self, branch: Branch, progress_toggle=False, external_progress: Progress = None, external_task_id: TaskID = None):
        correct_predictions = 0
        total_predictions = 0
        total_branches = len(branch)
        update_interval = max(1, total_branches // 100)  # Update every 1%

        if external_progress and external_task_id is not None:
            progress = external_progress
            task_id = external_task_id
        elif progress_toggle:
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn()
            )
            task_id = progress.add_task("[cyan]Processing branches...", total=total_branches)
        else:
            progress = None
            task_id = None

        try:
            if progress and not external_progress:
                progress.start()

            for i, (address, actual_outcome) in enumerate(branch):
                prediction = self.predict(address)
                if prediction == actual_outcome:
                    correct_predictions += 1
                total_predictions += 1

                self.update(address, actual_outcome)

                if progress:
                    if (i + 1) % update_interval == 0:
                        progress.update(task_id, advance=update_interval)

            if progress and not external_progress:
                progress.update(task_id, completed=total_branches)

        finally:
            if progress and not external_progress:
                progress.stop()

        accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0

        if progress_toggle:
            self.console.print(f"[green]Total branches: {total_predictions}")
            self.console.print(f"[green]Correct predictions: {correct_predictions}")
            self.console.print(f"[green]Accuracy: {accuracy:.2f}%")

        return accuracy