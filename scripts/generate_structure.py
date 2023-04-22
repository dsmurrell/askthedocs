import os

import pathspec


def read_gitignore(path):
    gitignore_path = os.path.join(path, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as file:
            ignore_patterns = file.read().splitlines()
    else:
        ignore_patterns = []
    return ignore_patterns


def is_ignored(path, spec, root):
    relative_path = os.path.relpath(path, root)
    return spec.match_file(relative_path) or os.path.basename(path).startswith(".")


def generate_structure(path, spec, prefix="", root=None, is_root=True):
    output = []

    if root is None:
        root = path

    if os.path.isfile(path):
        if is_ignored(path, spec, root):
            return []
        else:
            return [f"{prefix}├── {os.path.basename(path)}"]

    if is_root:
        output.append(f"{os.path.basename(path)}/")

    if is_ignored(path, spec, root):
        return []

    with os.scandir(path) as entries:
        files = sorted([entry for entry in entries], key=lambda x: x.is_file())
        for index, entry in enumerate(files):
            child_prefix = (
                f"{prefix}│   " if index != len(files) - 1 else f"{prefix}    "
            )
            branch = "├──" if index != len(files) - 1 else "└──"

            if entry.is_dir():
                subdir_output = generate_structure(
                    entry.path, spec, child_prefix, root, is_root=False
                )
                if subdir_output:
                    output.append(f"{prefix}{branch} {entry.name}/")
                    output.extend(subdir_output)
            elif not is_ignored(entry.path, spec, root):
                output.append(f"{prefix}{branch} {entry.name}")

    return output


project_path = "./"
ignore_patterns = read_gitignore(project_path)
spec = pathspec.PathSpec.from_lines(
    pathspec.patterns.GitWildMatchPattern, ignore_patterns
)
structure = generate_structure(project_path, spec)
print("\n".join(structure))
