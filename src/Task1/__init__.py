import os
import inquirer
from colorama import Fore, Style

from src.Task1.Branch import Branch
from src.Task1.BranchPredictor import BranchPredictor
from src.utils.utils import save_results_to_csv, getBestSizes, filesFolder, file_list, print_colored
from rich.console import Console


rich_console = Console(color_system="auto")


def main():
    table = getBestSizes()

    if table is None:
        print_colored("No branches found! (Please add branches as txt files inside Data/txt)", Fore.RED, Style.BRIGHT)
        return

    rich_console.print(table)


    files = list(table.columns[0].cells)
    sizes = list(table.columns[1].cells)
    # Create a list of choices including all files and an "All files" option

    answers = inquirer.prompt([
        inquirer.Checkbox(
                name='files',
                message="Choose the files you want to predict (Press -> to select and enter to confirm):",
                choices=files,
                )
    ])

    selectedFiles = answers['files']
    print(f"Predicting branch outcomes for files: {selectedFiles}")

    for row in list(zip(files, sizes)):
        file = row[0]
        size = int(row[1])
        if file in selectedFiles:
            print(f"Predicting branch outcomes for file: {file}")
            filePath = os.path.join(filesFolder, file)
            branch = Branch(filePath.__str__())
            predictor = BranchPredictor(size)
            analysis = predictor.predictBranch(branch)
            analysis.title = f"\nAnalysis for {file} with size {size}"
            rich_console.print(analysis)
            save_results_to_csv(analysis, f"results/{file}_{size}.csv")




if __name__ == "__main__":
    main()