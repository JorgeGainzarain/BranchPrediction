from collections import OrderedDict
from typing import Tuple

from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TaskID
from rich.console import Console
from src.models.Branch import Branch

class OneBitPredictor:
    MAX_HISTORY_SIZE = 16  # Maximum number of predictions to keep in history

    def __init__(self, size):
        self.history = OrderedDict[str,str]()
        self.console = Console()
        self.MAX_HISTORY_SIZE = size  # Set maximum history size based on the provided predictor size

    def predict(self, address):
        return self.history.get(address, 'T')  # Default prediction is 'T' (Taken)

    def update(self, address, prediction, outcome):
        if address in self.history:
            del self.history[address]  # Remove to update its position (LRU)
        elif len(self.history) >= self.MAX_HISTORY_SIZE:
            self.history.popitem(last=False)  # Remove least recently used item

        self.history[address] = outcome  # Add/Update the prediction

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
    
                self.update(address, prediction, actual_outcome)
    
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