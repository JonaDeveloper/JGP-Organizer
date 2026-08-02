import shutil


def organize_file(category, file):
     if category == "Images":
         destination_folder = file.parent / category
         destination_folder.mkdir(exist_ok=True)
         destination_file = destination_folder / file.name
         shutil.move(str(file), str(destination_file))