import shutil


def organize_file(category, file):
    destination_folder = file.parent / category
    destination_folder.mkdir(exist_ok=True)
    destination_file = destination_folder / file.name

    if destination_file.exists():
        rename_duplicates(file, destination_folder)

    else:
        shutil.move(str(file), str(destination_file))


def rename_duplicates(file, destination_folder):
    duplication_folder = destination_folder / "Duplicates"
    duplication_folder.mkdir(exist_ok=True)

    counter = 0
    candidate_name = f"{file.stem}{file.suffix}"
    duplicate_path = duplication_folder / candidate_name
    
    while duplicate_path.exists():
        counter += 1
        candidate_name = f"{file.stem}({counter}){file.suffix}"
        duplicate_path = duplication_folder / candidate_name

    shutil.move(str(file), str(duplicate_path))
