import os
from src.Task1.Branch import Branch
from src.Task1.BranchPredictor import BranchPredictor
from src.utils.utils import save_results_to_csv, createTable

from colorama import init, Fore, Style
from rich.console import Console

init(autoreset=True)  # Initialize colorama with auto reset

filesFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'txt'))
file_list = os.listdir(filesFolder)
file_list.sort(key=lambda x: os.path.getsize(os.path.join(filesFolder, x)))

rich_console = Console(color_system="auto")

def print_colored(text, color=Fore.WHITE, style=Style.NORMAL, end='\n'):
    print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)

def main():
    last_best_size = 1  # Initialize with 1 for the first file

    for file in file_list:
        file_path = os.path.join(filesFolder, file)
        print_colored(f"Processing {file}...", Fore.CYAN, Style.BRIGHT)
        branch = Branch(file_path)

        size = last_best_size  # Start with the best size from the last file
        best_accuracy = 0
        best_size = size
        max_size = len(branch)

        # Lists to store sizes and accuracies separately
        sizes = []
        accuracies = []

        while size <= max_size:
            predictor = BranchPredictor(size)
            correct_predictions = predictor.predictBranch(branch)

            accuracy = round((correct_predictions / len(branch)) * 100, 2)

            # Add to lists
            sizes.append(size)
            accuracies.append(accuracy)

            print_colored(f"Size: {size}, Accuracy: {accuracy}%", Fore.WHITE)

            if accuracy < best_accuracy + 0.01:
                break
            elif accuracy > best_accuracy:
                best_accuracy = accuracy
                best_size = size

            size *= 2

        print()
        print_colored(f"Best size: {best_size}", Fore.GREEN, Style.BRIGHT)
        print_colored(f"Best accuracy: {best_accuracy:.2f}%", Fore.GREEN, Style.BRIGHT)

        table = createTable(sizes, accuracies)
        rich_console.print(table)
        save_results_to_csv(table, file_path.replace('txt', 'csv'))

        last_best_size = best_size  # Save the best size for the next iteration

if __name__ == "__main__":
    main()