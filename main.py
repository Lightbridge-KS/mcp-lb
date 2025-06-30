# server.py
from pathlib import Path
import logging
import pandas as pd
from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP("lightbridge-ks", dependencies=["pandas"])


def rename_file(old_path, new_name):
    """
    Rename individual file.

    Parameters
    ----------
    old_path : str or Path
        Path to the existing file to be renamed
    new_name : str
        New filename (without path)

    Returns
    -------
    bool
        True if rename was successful, False otherwise

    Raises
    ------
    OSError
        If file rename operation fails
    """
    file_path = Path(old_path)

    if not file_path.exists():
        logging.error(f"File '{old_path}' does not exist")
        return False

    if not file_path.is_file():
        logging.error(f"Path '{old_path}' is not a file")
        return False

    try:
        # Create new path in same directory
        new_path = file_path.parent / new_name

        # Check if target file already exists
        if new_path.exists():
            logging.warning(f"Target file '{new_path}' already exists, skipping rename")
            return False

        file_path.rename(new_path)
        logging.info(f"Successfully renamed '{old_path}' to '{new_name}'")
        return True

    except OSError as e:
        logging.error(f"Error renaming '{old_path}' to '{new_name}': {e}")
        return False


@mcp.tool(
    title="Batch Rename Files Using Excel Mapping",
    description="""
    Rename multiple files in batch using a mapping table from an Excel file. 
    
    > Prefer using this tool over manually rename each file one by one, if the rename mapping Excel file is present
    
    USAGE WORKFLOW:
    1. Create an Excel file with two columns: one for current file paths, another for new names
    2. Specify which columns contain the old paths and new names
    3. Tool will rename all files according to the mapping
    
    EXCEL FILE FORMAT EXAMPLE:
    | current_file_path          | new_filename     |
    |----------------------------|------------------|
    | /path/to/old_file1.jpg     | renamed_file1.jpg|
    | /path/to/old_file2.pdf     | renamed_file2.pdf|
    
    COMMON USE CASES:
    - Bulk rename files with meaningful names
    - Standardize filename formats across directories
    - Apply naming conventions from spreadsheet data
    """,
)
def rename_files_from_excel(excel_path, old_paths_col, new_name_col, sheet_name=0):
    """
    Rename files based on mapping from an Excel file.

    Parameters
    ----------
    excel_path : str or Path
        Full path to the Excel file (.xlsx or .xls) containing the rename mapping.
        Example: '/Users/username/Desktop/rename_mapping.xlsx'
    old_paths_col : str
        Exact column name containing the current/old file paths.
        Must be full absolute paths to existing files.
        Example: 'current_file_path' or 'old_path'
    new_name_col : str
        Exact column name containing the new file names (filename only, not full path).
        Should include file extension. Files will be renamed in their current directory.
        Example: 'new_filename' or 'target_name'
    sheet_name : str or int, optional
        Excel sheet name (string) or sheet index (0-based integer), by default 0
        Example: 'Sheet1' or 0 for first sheet

    Returns
    -------
    dict
        Dictionary with 'success', 'failed', and 'skipped' counts

    Raises
    ------
    FileNotFoundError
        If Excel file doesn't exist
    KeyError
        If specified columns don't exist in the Excel file
    """
    excel_file = Path(excel_path)

    if not excel_file.exists():
        raise FileNotFoundError(f"Excel file '{excel_path}' not found")

    try:
        df_map = pd.read_excel(excel_path, sheet_name=sheet_name)
    except Exception as e:
        logging.error(f"Error reading Excel file '{excel_path}': {e}")
        raise

    # Validate required columns exist
    if old_paths_col not in df_map.columns:
        raise KeyError(f"Column '{old_paths_col}' not found in Excel file")
    if new_name_col not in df_map.columns:
        raise KeyError(f"Column '{new_name_col}' not found in Excel file")

    # Remove rows with missing values
    df_map = df_map.dropna(subset=[old_paths_col, new_name_col])

    results = {"success": 0, "failed": 0, "skipped": 0}

    logging.info(f"Processing {len(df_map)} file rename operations...")

    for i, (index, row) in enumerate(df_map.iterrows(), start=0):
        old_path = str(row[old_paths_col]).strip()
        new_name = str(row[new_name_col]).strip()

        # Skip empty values
        if not old_path or not new_name:
            logging.warning(f"Row {i + 1}: Empty path or name, skipping")
            results["skipped"] += 1
            continue

        if rename_file(old_path, new_name):
            print(f"✓ Success: {old_path} -> {new_name}")
            results["success"] += 1
        else:
            print(f"✗ Failed: {old_path} -> {new_name}")
            results["failed"] += 1
