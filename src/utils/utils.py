import csv
import os
import time

from rich.console import Console
from rich import box
from rich.table import Table
from colorama import init, Fore, Style
from src.Task1 import Branch, BranchPredictor

filesFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'txt'))
csvFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'csv'))

file_list = [f for f in os.listdir(filesFolder) if f.endswith('.txt')]
file_list.sort(key=lambda x: os.path.getsize(os.path.join(filesFolder, x)))

csv_file = os.path.join(csvFolder, 'analyzed_files.csv')

rich_console = Console(color_system="auto")
init(autoreset=True)  # Initialize colorama with auto reset

def print_colored(text, color=Fore.WHITE, style=Style.NORMAL, end='\n'):
    print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)
def save_results_to_csv(table: Table, csvName: str):
    # Ensure the directory exists
    csvPath = os.path.join(csvFolder, csvName)
    os.makedirs(os.path.dirname(csvPath), exist_ok=True)
    
    with open(csvPath, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write headers
        writer.writerow([column.header for column in table.columns])

        # Get all cell values for each column
        column_cells = [column.cells for column in table.columns]
        
        # Zip the cells from all columns to create rows
        rows = list(zip(*column_cells))
        
        # Write all rows except the last one
        writer.writerows(rows[:-1])
        
        # Write the last row without a newline
        if rows:
            file.write(','.join(str(cell) for cell in rows[-1]))

    print_colored(f"Results saved to {csvPath}", Fore.GREEN, Style.BRIGHT)


def createTable(sizes, accuracies) -> Table:
    # Create and display the table using rich
    table = Table(title="Results Table", box=box.DOUBLE_EDGE, show_header=True, header_style="bold magenta")

    table.add_column("Size", style="cyan", justify="center")
    table.add_column("Accuracy (%)", style="green", justify="center")

    for size, accuracy in zip(sizes, accuracies):
        table.add_row(str(size), f"{accuracy:.2f}")

    return table


import concurrent.futures
import numpy as np


def getBestSizes():
    if file_list.__len__() == 0: return None
    # Try to load existing results from CSV
    table: Table = load_results_from_csv(csv_file)

    if table:
        print_colored("Loaded existing results from CSV.", Fore.GREEN, Style.BRIGHT)
        processed_files = table.columns[0].cells
    else:
        table = Table(title="Best Sizes and Accuracies")
        table.add_column("File Name", style="cyan")
        table.add_column("Best Size", style="magenta")
        table.add_column("Best Accuracy", style="green")
        processed_files = set()

    # Process remaining files
    remaining_files = [f for f in file_list if os.path.basename(f) not in processed_files]

    if remaining_files:
        print_colored("Processing files " + remaining_files.__str__(), Fore.CYAN, Style.BRIGHT)

        last_best_size = 1

        for file in remaining_files:
            print_colored(f"Processing {os.path.basename(file)}...", Fore.CYAN, Style.BRIGHT)
            branch = Branch(os.path.join(filesFolder, file))

            size = last_best_size
            best_accuracy = 0
            best_size = size
            max_size = len(branch)

            while size <= max_size:
                predictor = BranchPredictor(size)
                analysisTable = predictor.predictBranch(branch)

                accuracy = float(list(analysisTable.columns[1].cells)[6].replace("%", ""))

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

            table.add_row(os.path.basename(file), str(best_size), f"{best_accuracy:.2f}%")
            last_best_size = best_size

        save_results_to_csv(table, csv_file)
        print_colored(f"Updated results saved to {csv_file}", Fore.GREEN, Style.BRIGHT)
    else:
        print_colored("All files have been processed previously.", Fore.GREEN, Style.BRIGHT)

    return table

"""
def getBestSizes():
    if not file_list:
        return None

    table = load_results_from_csv(csv_file) or Table(title="Best Sizes and Accuracies")
    if not table.columns:
        table.add_column("File Name", style="cyan")
        table.add_column("Best Size", style="magenta")
        table.add_column("Best Prediction Accuracy", style="green")
        table.add_column("Execution Time (s)", style="yellow")

    processed_files = set(table.columns[0].cells)
    remaining_files = [f for f in file_list if os.path.basename(f) not in processed_files]

    if not remaining_files:
        print_colored("All files have been processed previously.", Fore.GREEN, Style.BRIGHT)
        return table

    print_colored("Processing files: " + ', '.join(remaining_files), Fore.CYAN, Style.BRIGHT)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, file) for file in remaining_files]
        for future in concurrent.futures.as_completed(futures):
            filename, best_size, best_accuracy, execution_time = future.result()
            table.add_row(filename, str(best_size), f"{best_accuracy:.2f}%", f"{execution_time:.2f}")

    save_results_to_csv(table, csv_file)
    return table

def process_file(file):
    start_time = time.time()
    print_colored(f"Processing {os.path.basename(file)}...", Fore.CYAN, Style.BRIGHT)
    branch = Branch(os.path.join(filesFolder, file))
    rich_console.print(f"Processing time reading {file}: {time.time() - start_time:.2f} seconds")

    # Start with half the file length as the initial size
    initial_size = len(branch) // 2
    sizes = [initial_size] + list(np.logspace(np.log2(initial_size), np.log2(len(branch)), num=10, base=2, dtype=int))
    sizes = sorted(set(sizes))  # Remove duplicates and sort

    best_accuracy = 0
    best_size = sizes[0]
    best_execution_time = float('inf')

    for size in sizes:
        start_time = time.time()
        predictor = BranchPredictor(size)
        analysisTable = predictor.predictBranch(branch)
        execution_time = time.time() - start_time
        rich_console.print(f"Processing time for {file} (size {size}): {execution_time:.2f} seconds")

        pred_accuracy = float(list(analysisTable.columns[2].cells)[7].replace("%", ""))
        print_colored(f"Size: {size}, Prediction accuracy: {pred_accuracy}%, Time: {execution_time:.2f}s", Fore.WHITE)

        # Update best results if accuracy is better or if accuracy is the same but time is better
        if pred_accuracy > best_accuracy or (pred_accuracy == best_accuracy and execution_time < best_execution_time):
            best_accuracy = pred_accuracy
            best_size = size
            best_execution_time = execution_time
        elif pred_accuracy < best_accuracy - 0.01 and size > best_size:
            # If accuracy starts decreasing significantly and we're past the best size, stop
            break

    print_colored(f"Best size for {file}: {best_size}", Fore.GREEN, Style.BRIGHT)
    print_colored(f"Best prediction accuracy for {file}: {best_accuracy:.2f}%", Fore.GREEN, Style.BRIGHT)
    print_colored(f"Execution time for best size: {best_execution_time:.2f}s", Fore.GREEN, Style.BRIGHT)

    return os.path.basename(file), best_size, best_accuracy, best_execution_time

"""

def load_results_from_csv(csvPath) -> Table | None:
    try:
        with open(csvPath, 'r', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            
            table = Table(title="Best Sizes and Accuracies")
            table.add_column(headers[0], style="cyan")
            table.add_column(headers[1], style="magenta")
            table.add_column(headers[2], style="green")
            
            processed_files = set()
            for row in reader:
                table.add_row(*row)
                processed_files.add(row[0])  # Add filename to processed set
            
            return table
    except Exception as e:
        print_colored(f"Error loading CSV: {e}", Fore.RED, Style.BRIGHT)
        return None
