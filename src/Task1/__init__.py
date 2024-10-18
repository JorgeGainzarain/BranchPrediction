import os
import inquirer
from colorama import Fore, Style
import time

from src.Task1.Branch import Branch
from src.Task1.BranchPredictor import BranchPredictor
from src.utils.utils import save_results_to_csv, getOptimalSize, filesFolder, print_colored, existsOptimalSizes
from rich.console import Console


rich_console = Console(color_system="auto")


def processFile(file, size) :
    print(f"Processing file: {file} with history size: {size}")
    start_time = time.time()

    # Read file
    filePath = os.path.join(filesFolder, file)
    branch = Branch(filePath.__str__())

    # Predict
    predictor = BranchPredictor(size)

    # Print and save results to CSV file
    analysis = predictor.predictBranch(branch)
    analysis.title = f"\nAnalysis for {file} with size {size}"
    rich_console.print(analysis)
    save_results_to_csv(analysis, f"results/{file}_{size}.csv")

    # log the processing time
    rich_console.print(f"Processing time for {file}: {time.time() - start_time:.2f} seconds")

def main():
    # Check if optimal sizes exist
    if not existsOptimalSizes():
        print_colored("No optimal sizes found. Calculating optimal sizes...", Fore.YELLOW, Style.BRIGHT)
        table = getOptimalSize()
        if table is None:
            print_colored("No branches found! (Please add branches as txt files inside Data/txt)", Fore.RED, Style.BRIGHT)
            return
        else:
            rich_console.print(table)
            print_colored("Optimal sizes calculated and saved.", Fore.GREEN, Style.BRIGHT)
        input("Press Enter to continue...")

    while True:
        # Main menu
        main_choices = [
            "View Optimal Sizes",
            "Predict Branches",
            "Exit"
        ]
        main_answer = inquirer.prompt([
            inquirer.List('action',
                          message="What would you like to do?",
                          choices=main_choices,
                          )
        ])

        if main_answer['action'] == "View Optimal Sizes":
            table = getOptimalSize()
            if table is None:
                print_colored("No branches found! (Please add branches as txt files inside Data/txt)", Fore.RED, Style.BRIGHT)
            else:
                rich_console.print(table)
            input("Press Enter to continue...")

        elif main_answer['action'] == "Predict Branches":
            table = getOptimalSize()
            if table is None:
                print_colored("No branches found! (Please add branches as txt files inside Data/txt)", Fore.RED, Style.BRIGHT)
                continue

            files = [file for file in list(table.columns[0].cells) if os.path.exists(os.path.join(filesFolder, file))]
            if not files:
                print_colored("No valid files found in the table!", Fore.RED, Style.BRIGHT)
                continue

            sizes = list(table.columns[1].cells)

            answers = inquirer.prompt([
                inquirer.Checkbox(
                    name='files',
                    message="Choose the files you want to predict (Press -> to select and enter to confirm):",
                    choices=files,
                )
            ])

            selectedFiles = answers['files']
            print(f"Files selected: {selectedFiles}")

            for file, optimal_size in zip(files, sizes):
                if file in selectedFiles:
                    size_choice = inquirer.prompt([
                        inquirer.List('size_option',
                                      message=f"For {file}, use optimal size ({optimal_size}) or input custom size?",
                                      choices=['Use optimal size', 'Input custom size'],
                                      )
                    ])

                    if size_choice['size_option'] == 'Use optimal size':
                        size = int(optimal_size)
                    else:
                        while True:
                            custom_size = inquirer.prompt([
                                inquirer.Text('custom_size',
                                              message="Enter custom size (integer greater than 0):",
                                              validate=lambda _, x: x.isdigit() and int(x) > 0)
                            ])
                            size = int(custom_size['custom_size'])
                            if size > 0:
                                break
                            else:
                                print_colored("Invalid size. Please enter a positive integer.", Fore.RED, Style.BRIGHT)

                    processFile(file, size)

            input("Press Enter to continue...")

        elif main_answer['action'] == "Exit":
            print_colored("Exiting the program. Goodbye!", Fore.GREEN, Style.BRIGHT)
            break

if __name__ == "__main__":
    main()