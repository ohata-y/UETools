import os
from pathspec import PathSpec


def gitignore_to_pathspec() -> (PathSpec | None):
    """
    Load the .gitignore file from the project directory and return a PathSpec object.\\
    If there is no .gitignore, return None.
    """

    try:
        with open(".gitignore") as f:
            return PathSpec.from_lines("gitwildmatch", f)
    except FileNotFoundError:
        return None


def ask_whether_to_add_new_over100mib() -> bool:
    """
    Ask whether to add files over 100MiB to .gitignore.\\
    Returns True if the user wants to add them, False otherwise.\\
    The process suspends if retries exceed 10 times.
    """

    resp = input("Do you want to add files over 100MiB to .gitignore? (y/n) >> ")
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


def get_tracked_over100mib() -> (list[str] | None):
    """
    Explore the project directory and return a list of relative paths of files over 100MiB that are not in .gitignore.
    If there is no .gitignore, return None.
    """

    greater_than_100mib_file_paths = []
    bite_100mib = 100 * 2 ** 20

    project_dir = os.getcwd()
    gitignore_spec = gitignore_to_pathspec()

    if gitignore_spec is None:
        return None

    for dir, _, files in os.walk(project_dir):
        if os.path.relpath(dir, project_dir).startswith(".git"):
            continue
        for file in files:
            file_path = os.path.join(dir, file)
            relative_file_path = os.path.relpath(file_path, project_dir)
            if gitignore_spec.match_file(relative_file_path):
                continue
            try:
                file_size = os.path.getsize(file_path)
                if file_size > bite_100mib:
                    greater_than_100mib_file_paths.append(relative_file_path.replace("\\", "/"))
            except:
                print(f"File skipped due to error: {relative_file_path}")
    
    return greater_than_100mib_file_paths


def add_new_over100mib(fp: list[str]) -> None:
    """
    Add files over 100MiB to .gitignore that were not in it.
    """

    fp_new = list(map(lambda x: x + "\n", fp))

    with open(".gitignore") as f:
        lines = f.readlines()
    
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
        if lines[-1] != "\n":
            lines.append("\n")
        lines += (["# files over 100MiB\n"] + sorted(fp_new))
    else:
        if next_sharp_idx is None:
            start_idx = target_sharp_idx + 1
            end_idx = len(lines) - 1 - cnt_new_line
            current_untracked_files = lines[start_idx:end_idx+1]
            new_untracked_files = sorted(current_untracked_files + fp_new)
            lines = lines[:start_idx] + new_untracked_files
        else:
            start_idx = target_sharp_idx + 1
            end_idx = next_sharp_idx - 1 - cnt_new_line
            current_untracked_files = lines[start_idx:end_idx+1]
            new_untracked_files = sorted(current_untracked_files + fp_new)
            lines = lines[:start_idx] + new_untracked_files + lines[end_idx+1:]
    
    with open(".gitignore", mode="w") as f:
        f.writelines(lines)
    
    return None


if __name__ == "__main__":
    tracked_over100mib = get_tracked_over100mib()
    if tracked_over100mib is None:
        print("No .gitignore file found.")
    else:
        if tracked_over100mib == []:
            print("Every file over 100MiB is already in .gitignore.")
        else:
            print(f"Files over 100MiB that are not in .gitignore: {len(tracked_over100mib)}")
            for file in tracked_over100mib:
                print(f" - {os.path.getsize(file) / 2 ** 20:.0f}MiB: {file}")
            resp = ask_whether_to_add_new_over100mib()
            if resp:
                add_new_over100mib(tracked_over100mib)
                print("Done.")
                print("If the files are already tracked by git before adding them to .gitignore, you need to run 'git rm --cached <filename>'.")

