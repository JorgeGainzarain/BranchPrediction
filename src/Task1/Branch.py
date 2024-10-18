import fileinput
from typing import List, Tuple
import csv
from io import StringIO
from rich.progress import Progress
from rich.console import Console

console = Console()

class Branch(List[Tuple[str, str]]):
    def __init__(self, filePath: str, progress: bool = True):
        super().__init__()

        # Count the total number of lines in the file
        total_lines = sum(1 for _ in fileinput.input(filePath))

        update_interval = max(1, total_lines // 100)  # Update every 1% or at least once
        progress_count = 0

        with Progress() as progress_bar:
            if progress:
                task = progress_bar.add_task("[cyan]Loading branches...", total=total_lines, visible=progress)

            for i, line in enumerate(fileinput.input(filePath)):
                address, taken = line.strip().split()
                self.append((address, taken))

                progress_count += 1
                if progress and progress_count >= update_interval:
                    progress_bar.update(task, advance=progress_count, description=f"[cyan]Loaded {i+1}/{total_lines} branches")
                    progress_count = 0

            # Final update to ensure we reach 100%
            if progress and progress_count > 0:
                progress_bar.update(task, advance=progress_count, description=f"[cyan]Loaded {total_lines}/{total_lines} branches")

        if progress:
            console.print(f"[green]Successfully loaded {len(self)} branches from {filePath}")