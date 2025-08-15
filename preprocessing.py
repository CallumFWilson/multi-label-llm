import os
import pandas as pd


def preprocessing_utils(base_dir: str, comment: str):
    """Print header, validate base_dir, return (categories, max_len)."""
    if not os.path.isdir(base_dir):
        print(f'Base directory does not exist: "{base_dir}"')
        return [], 0  # Signal invalid

    print(comment)
    print('=' * len(comment))

    # Collect only subdirectories (categories)
    categories = [c for c in os.listdir(base_dir)
                  if os.path.isdir(os.path.join(base_dir, c))]

    if not categories:
        print("No category folders found.\n")
        return [], 0

    max_len = max(len(c) for c in categories)

    return categories, max_len


def merge_classified_unclassified(base_dir='categories'):
    """
    Merges '_classified.csv' and '_unclassified.csv' files in each category subfolder under base_dir.
    The merged file is saved as <category>.csv inside the category's folder.
    """

    # Print header, validate base_dir, and get category names + max name length
    initiation_comment = f'Merging classified and unclassified segments in: "{base_dir}"'
    categories, max_len = preprocessing_utils(base_dir, initiation_comment)
    if not categories:
        return f"Base directory does not exist: {base_dir}"

    # Iterate through each category folder
    for category in categories:
        category_path = os.path.join(base_dir, category)  # Full path to category folder
        merged_path = os.path.join(category_path, f"{category}.csv")  # Output path for merged file

        # Prepare empty DataFrames to hold classified and unclassified data
        classified_relevant = pd.DataFrame()
        unclassified_relevant = pd.DataFrame()

        # Skip any items in base_dir that are not directories
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
                    classified_relevant = classified[['segment_id', 'auto_issues', 'segment_text']].copy()
                    # Rename columns for consistency
                    classified_relevant.columns = ['segment_id', 'segment_labels', 'segment_text']
                    # Add column to indicate type of segment
                    classified_relevant['segment_type'] = 'classified'
                except KeyError as e:
                    print(f"Column missing in {file_path}: {e}")

            # Process unclassified CSV files
            elif file.endswith("_unclassified.csv"):
                try:
                    # Read unclassified CSV and keep only segment_text column
                    unclassified = pd.read_csv(file_path)
                    unclassified_relevant = unclassified[['segment_id', 'segment_text']].copy()
                    # Rename column for consistency
                    unclassified_relevant.columns = ['segment_id', 'segment_text']
                    # Add columns to indicate type and empty label list
                    unclassified_relevant[['segment_type', 'segment_labels']] = 'unclassified', '[]'
                except KeyError as e:
                    print(f"Column missing in {file_path}: {e}")

        # Merge only if both DataFrames have data
        if not classified_relevant.empty and not unclassified_relevant.empty:
            merged_relevant = pd.concat([classified_relevant, unclassified_relevant], ignore_index=True)
            # Save merged data to CSV inside category folder
            merged_relevant.to_csv(merged_path, index=False)
            # Print aligned confirmation message
            print(f'Saved:   {category:<{max_len}} - {merged_path}')
        else:
            # Inform if one or both DataFrames were empty
            print(f"Skipped: {category:<{max_len}} - one or both DataFrames are empty")

    print()


def rename_guidance_files(base_dir='categories'):
    """
    Rename 'guidance.csv' in each category folder to '<category>_guidance.csv'.
    Skips if already renamed, or marks as empty if no guidance file exists.
    """

    # Print header and get category names + max name length for alignment
    initiation_comment = f'Renaming guidance.csv files in: "{base_dir}"'
    categories, max_len = preprocessing_utils(base_dir, initiation_comment)
    if not categories:
        return f"Base directory does not exist: {base_dir}"

    # Loop through each category folder
    for category in categories:
        category_path = os.path.join(base_dir, category)
        original_guidance = os.path.join(category_path, "guidance.csv")
        renamed_guidance = os.path.join(category_path, f"{category}_guidance.csv")

        if os.path.exists(renamed_guidance):
            # File is already renamed
            print(f"Skipped: {category:<{max_len}} - {renamed_guidance}")

        elif os.path.exists(original_guidance):
            # Rename original guidance.csv
            os.rename(original_guidance, renamed_guidance)
            print(f"Renamed: {category:<{max_len}} - {renamed_guidance}")

        else:
            # No guidance file found
            print(f"Empty:   {category:<{max_len}} - guidance.csv does not exist")

    print()


def guidance_csv_to_json(base_dir='categories'):
    initiation_comment = f'Converting guidance CSV into JSON: "{base_dir}"'
    categories, max_len = preprocessing_utils(base_dir, initiation_comment)

    if not categories:
        return f"Base directory does not exist: {base_dir}"

    for category in categories:
        guidance_path = os.path.join(base_dir, category, f'{category}_guidance.csv')
        output_path = guidance_path.replace(".csv", ".json")

        try:
            guidance = pd.read_csv(guidance_path)
            guidance = guidance.fillna('')

            json_str = guidance.to_json(orient="records", indent=2, force_ascii=False)
            # print(json_str)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)

            print(f'Saved: {category:<{max_len}} - {output_path}')
        except:
            print(f"Empty: {category:<{max_len}} - {category}_guidance.csv does not exist")

    print()


# Run the merge function only if this script is executed directly
if __name__ == "__main__":
    merge_classified_unclassified()
    rename_guidance_files()
    guidance_csv_to_json()
