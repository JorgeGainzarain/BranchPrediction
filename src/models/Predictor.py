from abc import ABC, abstractmethod
from collections import OrderedDict

from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TaskID
from rich.console import Console
from src.models.Branch import Branch

class Predictor(ABC):
    MAX_HISTORY_SIZE = 16
    default_prediction_state = 'N'

    def __init__(self, size):
        self.history = OrderedDict()
        self.MAX_HISTORY_SIZE = size
        self.console = Console()

    @abstractmethod
    def predict(self, address):
        pass

    @abstractmethod
    def update(self, address, outcome):
        pass

    def predict_branch(self, branch: Branch, progress_toggle=False, external_progress: Progress = None, external_task_id: TaskID = None):
        correct_predictions = 0
        total_predictions = 0
        correct = 0
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

                if prediction is not None:
                    total_predictions += 1
                    correct_predictions += 1 if prediction == actual_outcome else 0
                    correct += 1 if actual_outcome == prediction else 0
                else:
                    correct += 1 if actual_outcome == self.default_prediction_state else 0

                self.update(address, actual_outcome)
    
                if progress:
                    if (i + 1) % update_interval == 0:
                        progress.update(task_id, advance=update_interval)
    
            if progress and not external_progress:
                progress.update(task_id, completed=total_branches)
    
        finally:
            if progress and not external_progress:
                progress.stop()

        pred_accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        total_accuracy = (correct / total_branches) * 100 if total_branches > 0 else 0
        prediction_percentage = (total_predictions / total_branches) * 100 if total_branches > 0 else 0
    
        if progress_toggle:
            self.console.print(f"[green]Total branches: {total_predictions}")
            self.console.print(f"[green]Correct predictions: {correct_predictions}")
            self.console.print(f"[green]Prediction percentage: {prediction_percentage:.2f}%")
            self.console.print(f"[green]Accuracy: {pred_accuracy:.2f}%")
    
        return pred_accuracy, total_accuracy, prediction_percentage