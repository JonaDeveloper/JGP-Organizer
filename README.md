# JGP-Organizer

A configurable file organizer built with Python. Scans a directory, classifies files by extension, and automatically moves them into category-based subfolders.

**Current version:** `v0.1.0` — functional core

## Features

- Directory scanning (single level, non-recursive)
- Automatic classification by extension via configurable dictionary
- Automatic creation of destination subfolders
- File moving to the corresponding category
- Idempotent behavior: running the script multiple times does not reorganize already-moved files

## How to run

```bash
python3 main.py
```

The script will scan the current directory, classify each file by extension, and move it into a matching subfolder (`Imagenes`, `Documentos`, `Audio`, `Video`, `Comprimidos`, `Instaladores`, `Otros`…).

## Project structure

```
JGP-Organizer/
├── main.py         # Entry point, coordinates the full flow
├── config.py       # Classification rules (extension -> category)
├── rules.py        # Classification logic for a single file
├── organizer.py    # Folder creation and file moving
└── README.md
```

Each module has a single responsibility:

- `config.py` → **what** the rules are (data only)
- `rules.py` → **how** a category is decided for a given file
- `organizer.py` → **what action** is taken (create folder, move file)
- `main.py` → orchestrates the flow; contains no business logic itself

## Known limitations

- Does not handle duplicate filenames at destination (silently overwrites)
- No exception handling (permissions, files in use, etc.)
- Classification rules are hardcoded, not user-configurable yet
- No graphical interface, console only

## Roadmap

- [x] **Phase 1 — MVP**: scanning and basic classification by extension
- [x] **Phase 1.1 — Move logic**: create destination folders and move files
- [ ] **Phase 2 — Robustness**: exception handling and duplicate file handling
- [ ] **Phase 3 — Configurable**: external rules file (JSON), CLI arguments (`argparse`), dry-run mode
- [ ] **Phase 4 — OOP**: refactor to classes (`Rule`, `Organizer`), classify by date, size, or name pattern
- [ ] **Phase 5 — Extras**: scheduled automatic execution, graphical interface, undo last organization

## Author

Built by JonasDev as a learning project.
