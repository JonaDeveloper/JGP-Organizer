from pathlib import Path
import rules, organizer


p = Path('.')

if __name__ == "__main__":

  print(f"Organizing files in directory: {p.resolve()}")

  for xfile in p.iterdir():
    if xfile.is_file():
      category, file = rules.detection(xfile)
      organizer.organize_file(category, file)

  print("Files organized successfully.")