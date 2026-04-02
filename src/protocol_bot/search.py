import pandas as pd
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from datetime import datetime
from pathlib import Path

console = Console()

# --- Utility Functions --- #
def load_excel_with_second_row_headers(filepath):
    sheet_dict = pd.read_excel(filepath, sheet_name=None, header=None)
    cleaned_sheets = {}
    for name, df in sheet_dict.items():
        if len(df) > 1:
            df.columns = df.iloc[1].fillna("").astype(str)
            df = df.drop(index=[0, 1]).reset_index(drop=True)
        else:
            df.columns = [f"Column_{i+1}" for i in range(df.shape[1])]
        df = df.map(lambda x: " ".join(str(x).split()) if pd.notna(x) else "")
        cleaned_sheets[name] = df
    return cleaned_sheets

def clean_df(df):
    df = df.map(lambda x: " ".join(str(x).split()) if pd.notna(x) else "")
    return df

def show_table(df, title):
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row.values])
    console.print(table)

def export_results(df, filename_prefix="search_results"):
    # Export DataFrame results to CSV with headers #
    output_dir = Path("Search_Results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    filepath = output_dir / filename
    
    df.to_csv(filepath, index=False)
    console.print(f"[bold green]Results exported to:[/bold green] {filepath}")

# --- Search Function --- #
def search_excel(repository_list, stock_repo_path="data/Stock_Repository"):
    console.print("[cyan]Loading Excel files...[/cyan]")
    
    repo_data = {}
    stock_repo_path = Path(stock_repo_path)

    for fname in repository_list:
        fullpath = Path(fname)
        if not fullpath.is_absolute():
            fullpath = stock_repo_path / fname
            
        if not fullpath.exists():
            console.print(f"[bold red]Warning:[/bold red] File not found at {fullpath}")
            continue

        excel_obj = pd.ExcelFile(fullpath)

        if len(excel_obj.sheet_names) > 1:
            repo_data[fname] = {
                "type": "multi",
                "data": load_excel_with_second_row_headers(fullpath)
            }
        else:
            df = pd.read_excel(fullpath)
            df = clean_df(df)
            repo_data[fname] = {
                "type": "single",
                "data": df
            }

    console.print("[green]Excel files loaded successfully.[/green]")

    # --- Interactive Search Loop --- #
    choices = list(repository_list.keys()) + ["Exit"]

    while True:
        repo_choice = inquirer.select(
            message="Select a dataset to search:",
            choices=choices
        ).execute()

        if repo_choice == "Exit":
            console.print("[bold green]Goodbye![/bold green]")
            break

        query = inquirer.text(
            message=f"Enter keyword to search in {repo_choice}:"
        ).execute()

        entry = repo_data[repo_choice]
        repo_type = entry["type"]

        # =============================================================== #
        #                  MULTI-SHEET SEARCH                             #
        # =============================================================== #
        if repo_type == "multi":
            all_results = []
            found_any = False

            for sheet_name, df in entry["data"].items():
                results = df[df.apply(
                    lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1
                )]
                if not results.empty:
                    found_any = True
                    show_table(results, f"Results from sheet: {sheet_name}")

                    df2 = results.copy()
                    df2.loc[:, "Sheet"] = sheet_name
                    all_results.append(df2)

            if not found_any:
                console.print(f"[red]No results found for '{query}' in any sheet of {repo_choice}.[/red]")
            else:
                export_choice = inquirer.confirm(
                    message="Export all found results to CSV?",
                    default=True
                ).execute()
                if export_choice:
                    merged = pd.concat(all_results, ignore_index=True)
                    prefix = repo_choice.replace(".xlsx", "")
                    export_results(merged, filename_prefix=f"{prefix}_{query.replace(' ', '_')}")

        # =============================================================== #
        #                  SINGLE-SHEET SEARCH                            #
        # =============================================================== #
        else:
            df = entry["data"]
            results = df[df.apply(
                lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1
            )]
            if results.empty:
                console.print(f"[red]No results found for '{query}' in {repo_choice}.[/red]")
            else:
                show_table(results, f"Results from {repo_choice}")
                export_choice = inquirer.confirm(
                    message="Export results to CSV?",
                    default=True
                ).execute()
                if export_choice:
                    prefix = repo_choice.replace(".xlsx", "")
                    export_results(results, filename_prefix=f"{prefix}_{query.replace(' ', '_')}")

# --- Run Program --- #
if __name__ == "__main__":
    # User can define the stock repository paths and names
    search_excel(repository_list={"GeneletRepository.xlsx": 2, "ComponentRepository.xlsx": 1})
