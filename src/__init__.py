

from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn


from src.models.OneBitPredictor import OneBitPredictor
from src.models.TwoBitPredictor import TwoBitPredictor
from src.models.ImprovedPredictor import ImprovedPredictor

from src.models.Branch import Branch
import os
import concurrent.futures

from src.utils.utils import save_table, save_results, load_results_from_csv, save_table_to_csv, getLines, empty_table
import inquirer

csvFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data', 'csv'))
console = Console()
filesFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data', 'txt'))
file_list = [f for f in os.listdir(filesFolder) if f.endswith('.txt')]
file_list.sort(key=lambda x: os.path.getsize(os.path.join(filesFolder, x)))


progress = Progress(
    TextColumn("{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
)


def get_user_selections():
    questions = [
        inquirer.List('action',
                      message="Select an action",
                      choices=['View Saved Data', 'Test All', 'Select Files', 'Exit']),
    ]

    action = inquirer.prompt(questions)['action']

    if action == 'Exit':
        return 'exit', None

    if action == 'View Saved Data':
        csv_files = [f for f in os.listdir(csvFolder) if f.endswith('.csv')]
        if not csv_files:
            console.print("[red]No saved data found.[/red]")
            return None, None

        file_choice = inquirer.prompt([
            inquirer.List('file',
                          message="Select a CSV file to view",
                          choices=csv_files)
        ])['file']

        table = load_results_from_csv(os.path.join(csvFolder, file_choice))
        return 'view', table

    elif action == 'Test All' or action == 'Select Files':
        predictor_question = [
            inquirer.List('predictor',
                          message="Select the predictor type",
                          choices=['One Bit Predictor', 'Two Bit Predictor', 'Improved Predictor'])
        ]
        predictor_type = inquirer.prompt(predictor_question)['predictor']

        if action == 'Test All':
            return 'test_all', predictor_type

        else:  # Select Files
            size_question = [
                inquirer.List('size',
                              message="Select the size for the predictor",
                              choices=['1', '2', '4', '8', '16'])
            ]

            file_question = [
                inquirer.Checkbox('files',
                                  message="Select files to process (Press -> To select and Enter to confirm)",
                                  choices=file_list),
            ]

            size = inquirer.prompt(size_question)['size']
            files = inquirer.prompt(file_question)['files']

            return 'select', (files, int(size), predictor_type)

    else:
        console.print("[red]Invalid action. Please try again.[/red]")
        return None, None


def process_selected_files(selected_files, sizes, predictor_type):


    if not selected_files:
        print("No files selected. Exiting.")
        return


    with progress:
        taskLoad = progress.add_task("[cyan]Loading files...")
        lines = sum([getLines(os.path.join(filesFolder,file)) for file in selected_files])
        progress.update(taskLoad, total=lines)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            files_futures = {executor.submit(load_file, os.path.join(filesFolder, file), taskLoad): file for file in selected_files}

            futures = []
            concurrent.futures.wait(files_futures)
            branches = [future.result() for future in concurrent.futures.as_completed(files_futures)]

            progress.update(taskLoad, completed=lines)
            progress.remove_task(taskLoad)

            total_size = sum(len(branch) for branch in branches)
            taskProcess = progress.add_task("[cyan]Processing files...", total= len(sizes) * total_size )


            futures.extend([executor.submit(process_file, branch, size, predictor_type, taskProcess) for branch in branches for size in sizes])

            # Wait for all futures to complete
            accuracies = []
            for future in concurrent.futures.as_completed(futures):
                accuracies.append(future.result())

            progress.remove_task(taskProcess)

    # Create and display the results table
    table = empty_table()

    accuracy_index = 0
    for file in selected_files:
        for size in sizes:
            pred_accuracy, total_accuracy, prediction_percentage = accuracies[accuracy_index]
            table.add_row(file, str(size), f"{pred_accuracy:.2f}%", f"{total_accuracy:.2f}%", f"{prediction_percentage:.2f}%")
            accuracy_index += 1



    console.print("\n")
    console.print(table)

    csvName = f"{predictor_type.lower().replace(' ', '_')}_results.csv"
    save_table(table,csvName)

def load_file(file_path, task):
    branch = Branch(file_path, external_progress=progress, external_task_id=task)
    return branch

def process_file(branch, size, predictor_type, task):
    if predictor_type == 'One Bit Predictor':
        predictor = OneBitPredictor(size)
    elif predictor_type == 'Two Bit Predictor':
        predictor = TwoBitPredictor(size)
    else:  # Improved Predictor
        predictor = ImprovedPredictor(size)
 
    return predictor.predict_branch(branch, external_progress=progress, external_task_id=task)
def main():
    while True:
        console.print("\n[bold cyan]Branch Prediction Analysis[/bold cyan]")
        action, data = get_user_selections()

        if action == 'exit':
            console.print("[yellow]Exiting the program. Goodbye![/yellow]")
            break

        if action == 'view':
            if data:
                console.print(data)
            else:
                console.print("[red]No data to display.[/red]")
        elif action == 'test_all':
            sizes = [1, 2, 4, 8, 16]
            process_selected_files(file_list, sizes, data)

        elif action == 'select':
            selected_files, size, predictor_type = data
            process_selected_files(selected_files, [size], predictor_type)
        else:
            console.print("[red]Invalid action. Please try again.[/red]")

        # Ask if the user wants to continue
        if not inquirer.confirm("Do you want to perform another action?"):
            console.print("[yellow]Exiting the program. Goodbye![/yellow]")
            break

if __name__ == "__main__":
    main()