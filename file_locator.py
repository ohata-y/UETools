import os
import shutil


def get_untracked_over100mib_file_paths() -> (list[str] | None):
    """
    Return a list of untracked files over 100MiB in the .gitignore file.\\
    If there is no file over 100MiB in the .gitignore, return an empty list.\\
    If the .gitignore file is not found, return None.
    """

    try:
        with open(".gitignore") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None
    
    target_sharp_idx = None
    next_sharp_idx = None
    cnt_new_line = 0
    target_found = False

    for i, line in enumerate(lines):
        if line == "# files over 100MiB\n":
            target_sharp_idx = i
            target_found = True
        elif target_found and line == "\n":
            cnt_new_line += 1
        elif target_found and line.startswith("#"):
            next_sharp_idx = i
            break
    
    if target_sharp_idx is None:
        return []
    else:
        if next_sharp_idx is None:
            start_idx = target_sharp_idx + 1
            end_idx = len(lines) - 1 - cnt_new_line
            untracked_over100mib_files = [file.strip() for file in sorted((lines[start_idx:end_idx+1]))]
        else:
            start_idx = target_sharp_idx + 1
            end_idx = next_sharp_idx - 1 - cnt_new_line
            untracked_over100mib_files = [file.strip() for file in sorted((lines[start_idx:end_idx+1]))]

        return untracked_over100mib_files


def get_uploaded_file_names() -> list[str]:
    """
    Explore the "modified_untracked_files" directory and return a list of file names.\\
    If the directory does not exist or is empty, return an empty list.
    """

    uploaded_file_names = []

    for _, _, files in os.walk("modified_untracked_files"):
        for file in files:
            if file != ".gitkeep":
                uploaded_file_names.append(file)

    return uploaded_file_names


def ask_whether_to_move_files() -> bool:
    """
    Ask the user whether to move files over 100MiB to the paths specified in the .gitignore file.\\
    Return True if the user agrees, False otherwise.\\
    The process suspends if retries exceed 10 times.
    """

    resp = input("Do you want to move above files to the paths specified in the .gitignore? (y/n) >> ")
    cnt = 0
    while True:
        if resp == "y":
            return True
        elif resp == "n":
            return False
        else:
            if cnt < 10:
                resp = input("Please enter y or n. >> ")
                cnt += 1
            else:
                print("Process suspended.")
                return False


def move_files(uploaded_file_names: list[str], untracked_over100mib_files: list[str]) -> list[str]:
    """
    Move files from "modified_untracked_files" to the paths specified in the .gitignore file.\\
    Return a list of moved file paths.
    """

    moved_files = []

    for file in uploaded_file_names:
        for file_path in untracked_over100mib_files:
            if file == os.path.basename(file_path):
                file_path_after_moved = shutil.move(
                    os.path.join("modified_untracked_files", file), 
                    file_path
                )
                moved_files.append(file_path_after_moved)
    
    return moved_files


if __name__ == "__main__":
    untracked_over100mib_files = get_untracked_over100mib_file_paths()
    if untracked_over100mib_files is None:
        print("No .gitignore file found.")
    elif untracked_over100mib_files == []:
        print("No untracked files over 100MiB found.")
    else:
        uploaded_file_names = get_uploaded_file_names()
        if uploaded_file_names == []:
            print("No files found in 'modified_untracked_files' directory.")
        else:
            print(f"Found {len(uploaded_file_names)} files in 'modified_untracked_files' directory.")
            for file in uploaded_file_names:
                print(f" - {file}")
            resp = ask_whether_to_move_files()
            if resp:
                moved_files = move_files(uploaded_file_names, untracked_over100mib_files)
                print("Done.")
                print("Result:")
                for moved_file in moved_files:
                    print(f" - modified_untracked_files/{os.path.basename(moved_file)} -> {moved_file}")

