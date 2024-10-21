import csv
import os
from itertools import pairwise

from rich.console import Console
from rich import box
from rich.table import Table
from colorama import init, Fore, Style

filesFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'txt'))
csvFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'csv'))

file_list = [f for f in os.listdir(filesFolder) if f.endswith('.txt')]
file_list.sort(key=lambda x: os.path.getsize(os.path.join(filesFolder, x)))

rich_console = Console(color_system="auto")
init(autoreset=True)  # Initialize colorama with auto reset


def saveResults(files, sizes, accuracies, nameCSV):
    csv_file = os.path.join(csvFolder, nameCSV)
    existing_table = load_results_from_csv(csv_file)
    new_table = createTable(files, sizes, accuracies)

    final_table = emptyTable()

    if existing_table:
        oldColumns = existing_table.columns
        oldCells = [column.cells for column in oldColumns]
        oldRows = list(zip(*oldCells))

        #print(f"Old Rows: {oldRows}")

        # Now let's declare the new rows
        newColumns = new_table.columns
        newCells = [column.cells for column in newColumns]
        newRows = list(zip(*newCells))
        #print(f"New Rows: {newRows}")

        # Remove the rows that are already in the existing table
        newRows = [row for row in newRows if row not in oldRows]

        finalRows = oldRows + newRows
        # Sort finalRows by the first element, then second, then third
        finalRows = sorted(finalRows, key=lambda x: (
            x[0],  # Branch name (string)
            int(x[1]),  # Size (integer)
            float(x[2].rstrip('%'))  # Accuracy (float, remove '%' sign)
        ))

        #print(f"Final Rows: {finalRows}")

        for row in finalRows:
            final_table.add_row(*row)
    else:
        final_table = new_table


    # Save the final table to CSV
    save_table_to_csv(final_table, nameCSV)

    # Display the final table
    rich_console.print(final_table)

def emptyTable() -> Table:
    table = Table(title="Results Table", box=box.DOUBLE_EDGE, show_header=True, header_style="bold magenta")

    table.add_column("Branch", style="yellow", justify="center")
    table.add_column("Size", style="cyan", justify="center")
    table.add_column("Accuracy (%)", style="green", justify="center")
    return table

def createTable(files, sizes, accuracies) -> Table:
    # Create and display the table using rich
    table = emptyTable()

    for file, size, accuracy in zip(files, sizes, accuracies):
        table.add_row(os.path.basename(file), str(size), f"{accuracy:.2f}")

    return table

def save_table_to_csv(table: Table, csvName: str):
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

    print_colored(f"Table saved to {csvPath}", Fore.GREEN, Style.BRIGHT)

def load_results_from_csv(csvFile) -> Table | None:
    csvPath = os.path.join(csvFolder, csvFile)
    try:
        with open(csvPath, 'r', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            
            table = Table(title="Optimal Sizes")
            table.add_column(headers[0], style="cyan")
            table.add_column(headers[1], style="magenta")
            table.add_column(headers[2], style="green")

            for row, next_row in pairwise(reader):
                file, _, _ = row
                nextFile, _, _ = next_row

                if file != nextFile:
                    table.add_row(*row,end_section=True)
                else:
                    table.add_row(*row)

            
            return table
    except Exception as e:
        print_colored(f"Error loading CSV: {e}", Fore.RED, Style.BRIGHT)
        return None

def print_colored(text, color=Fore.WHITE, style=Style.NORMAL, end='\n'):
    print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)

def getLines(filePath):
    with open(filePath, 'r') as file:
        lines = file.readlines()

    return len(lines)

