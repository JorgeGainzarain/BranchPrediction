import csv
import os

from rich import box
from rich.table import Table

def save_results_to_csv(table: Table, csv_file: str):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write headers
        writer.writerow([column.header for column in table.columns])
        
        # Write data
        sizes = table.columns[0].cells
        accuracies = table.columns[1].cells
        rows = list(zip(sizes, accuracies))
        
        # Write all rows except the last one
        for row in rows[:-1]:
            writer.writerow(row)
        
        # Write the last row without a newline
        if rows:
            file.write(','.join(str(cell) for cell in rows[-1]))

    return csv_file

def createTable(sizes, accuracies) -> Table:
    # Create and display the table using rich
    table = Table(title="Results Table", box=box.DOUBLE_EDGE, show_header=True, header_style="bold magenta")

    table.add_column("Size", style="cyan", justify="center")
    table.add_column("Accuracy (%)", style="green", justify="center")

    for size, accuracy in zip(sizes, accuracies):
        table.add_row(str(size), f"{accuracy:.2f}")

    return table