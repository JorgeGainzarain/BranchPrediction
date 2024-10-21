from typing import List, Tuple
from rich.progress import Progress, TaskID
from rich.console import Console

console = Console()

class Branch(List[Tuple[str, str]]):
    def __init__(self, filePath: str, percentage: float = 100.0, progress_toggle: bool = True, external_progress: Progress = None, external_task_id: TaskID = None):
        super().__init__()
        percentage = max(0.0, min(100.0, percentage))

        with open(filePath, 'r') as file:
            lines = file.readlines()

        total_lines = len(lines)
        lines_to_read = int(total_lines * (percentage / 100))
        update_interval = max(1, lines_to_read // 100)

        if external_progress and external_task_id is not None:
            progress = external_progress
            task = external_task_id
        elif progress_toggle:
            progress = Progress()
            task = progress.add_task("[cyan]Loading branches...", total=lines_to_read)
        else:
            progress = None
            task = None

        try:
            if progress and not external_progress:
                progress.start()

            for i, line in enumerate(lines[:lines_to_read]):
                address, taken = line.strip().split()
                self.append((address, taken))

                if progress and (i + 1) % update_interval == 0:
                    progress.update(task, advance=update_interval)
                    if not external_progress:
                        progress.update(description = f"[cyan]Loaded {i + 1}/{lines_to_read} branches")

            if progress and not external_progress:
                progress.update(task, completed=lines_to_read)

        finally:
            if progress and not external_progress:
                progress.stop()

        if progress_toggle and not external_progress:
            console.print(
                f"[green]Successfully loaded {len(self)} branches from {filePath} ({percentage:.1f}% of file)")
