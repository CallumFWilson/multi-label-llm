import os
import pandas as pd

def merge_classified_unclassified(base_dir='categories'):
    """
    Merges '_classified.csv' and '_unclassified.csv' files in each category subfolder under base_dir.
    The merged file is saved as <category>.csv inside the category's folder.
    """

    # Check if the base directory exists; stop execution if it doesn't
    if not os.path.isdir(base_dir):
        print(f"Base directory does not exist: {base_dir}")
        return

    # Find the length of the longest category folder name for aligned printing
    max_len = max(
        len(c) for c in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, c))
    )

    # Iterate through each item in the base directory
    for category in os.listdir(base_dir):
        category_path = os.path.join(base_dir, category)  # Full path to the category folder
        merged_path = os.path.join(category_path, f"{category}.csv")  # Output path for merged file

        # Prepare empty DataFrames to hold classified and unclassified data
        classified_relevent = pd.DataFrame()
        unclassified_relevent = pd.DataFrame()

        # Skip non-directory items in base_dir
        if not os.path.isdir(category_path):
            continue

        # Loop through all files in the category folder
        for file in os.listdir(category_path):
            file_path = os.path.join(category_path, file)  # Full path to current file

            # Process classified CSV files
            if file.endswith('_classified.csv'):
                try:
                    # Read classified CSV and keep only relevant columns
                    classified = pd.read_csv(file_path)
                    classified_relevent = classified[['auto_issues', 'segment_text']].copy()
                    # Rename columns for consistency
                    classified_relevent.columns = ['segment_labels', 'segment_text']
                    # Add column to indicate type of segment
                    classified_relevent['segment_type'] = 'classified'
                except KeyError as e:
                    print(f"Column missing in {file_path}: {e}")

            # Process unclassified CSV files
            elif file.endswith("_unclassified.csv"):
                try:
                    # Read unclassified CSV and keep only segment_text column
                    unclassified = pd.read_csv(file_path)
                    unclassified_relevent = unclassified[['segment_text']].copy()
                    # Rename column for consistency
                    unclassified_relevent.columns = ['segment_text']
                    # Add columns to indicate type and empty label list
                    unclassified_relevent[['segment_type', 'segment_labels']] = 'unclassified', '[]'
                except KeyError as e:
                    print(f"Column missing in {file_path}: {e}")

        # Merge only if both classified and unclassified DataFrames have data
        if not classified_relevent.empty and not unclassified_relevent.empty:
            merged_relevent = pd.concat(
                [classified_relevent, unclassified_relevent],
                ignore_index=True
            )
            # Save merged data to CSV inside category folder
            merged_relevent.to_csv(merged_path, index=False)
            # Print aligned confirmation message
            print(f'Saved:   {category:<{max_len}} - {merged_path}')
        else:
            # Inform if one or both DataFrames were empty
            print(f"Skipped: {category:<{max_len}} - one or both DataFrames are empty")

# Run the merge function only if this script is executed directly
if __name__ == "__main__":
    merge_classified_unclassified()
