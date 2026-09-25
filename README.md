# JGP-Organizer

A configurable and modular file organizer built with Python.

JGP-Organizer scans a directory, classifies files according to configurable rules, and organizes them automatically into category-based folders. It also supports simulation mode, duplicate handling, exception management and a modular object-oriented architecture.

**Current version:** `v0.4.0` — OOP refactor in progress

---

## Features

* Directory scanning (non-recursive)
* Automatic file classification by extension
* External classification rules using `categories.json`
* Automatic creation of destination folders
* Automatic file organization
* Dry Run / simulation mode
* Duplicate filename detection and handling
* Automatic renaming of duplicate files
* Dedicated `Duplicates` folder for duplicate files
* Exception handling for common filesystem errors
* Hidden file filtering
* Directory validation
* Permission validation
* Operation summary and error reporting
* Modular architecture
* Object-oriented file organization logic
* Cross-platform compatibility considerations for Windows and macOS

---

## How it works

JGP-Organizer separates the organization process into several responsibilities:

1. **Directory analysis**
   The application scans the selected directory and identifies the files that can be organized.

2. **File classification**
   Each file is classified according to the rules defined in `categories.json`.

3. **Organization**
   The `FileOrganizer` class performs the required filesystem operations.

4. **Duplicate handling**
   If a file with the same name already exists in the destination, the application handles the duplicate instead of overwriting the existing file.

5. **Dry Run mode**
   When simulation mode is enabled, no files or directories are modified. The application reports what operations would be performed.

6. **Summary**
   At the end of the operation, the application reports the number of organized files and detected errors.

---

## Configuration

Classification rules are stored externally in `categories.json`.

This allows the user to modify the file categories and extensions without changing the Python source code.

Example:

```json
{
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".doc", ".docx", ".txt"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Video": [".mp4", ".mkv", ".avi"],
    "Compressed": [".zip", ".rar", ".7z"],
    "Installers": [".exe", ".dmg", ".pkg"]
}
```

The classification system can therefore be extended or adapted to different user requirements.

---

## Dry Run mode

JGP-Organizer includes a simulation mode that allows the user to preview the organization process without modifying the filesystem.

When Dry Run is enabled:

* Files are **not moved**
* Destination folders are **not created**
* Duplicate files are **not moved**
* The application reports the operations that would be performed

Example:

```text
[DRY RUN] Would move: photo.jpg -> Images/
[DRY RUN] Would move: document.pdf -> Documents/
[DRY RUN] Duplicate detected: song.mp3
```

This provides a safe way to verify the result before performing real changes.

---

## Duplicate handling

JGP-Organizer does not blindly overwrite files when a filename already exists in the destination.

When a duplicate is detected, the application handles it separately and generates a new filename when necessary.

For example:

```text
photo.jpg
photo_1.jpg
photo_2.jpg
```

Duplicates can also be redirected to a dedicated `Duplicates` directory according to the organization logic.

---

## Project structure

```text
JGP-Organizer/
│
├── main.py
├── config.py
├── rules.py
├── organizer.py
├── categories.json
├── README.md
│
└── tests/
```

### Module responsibilities

#### `main.py`

The application entry point and main orchestrator.

Responsible for coordinating the complete workflow without containing the core file-organization logic.

```text
main()
    ↓
directory selection / validation
    ↓
directory analysis
    ↓
file classification
    ↓
FileOrganizer
    ↓
summary
```

#### `config.py`

Handles application configuration and access to the classification rules.

The actual extension/category definitions are stored externally in `categories.json`.

#### `categories.json`

Contains the configurable classification rules.

It defines which file extensions belong to each category.

#### `rules.py`

Contains the file classification logic.

Its responsibility is to determine the category of a given file based on the configured rules.

Example:

```python
category = classify_file(file)
```

#### `organizer.py`

Contains the object-oriented file organization logic.

The `FileOrganizer` class is responsible for filesystem operations such as:

* Creating destination directories
* Moving files
* Detecting duplicates
* Handling duplicate filenames
* Supporting Dry Run operations

Example:

```python
file_organizer.organize_file(file, category)
```

---

## Architecture

The project is progressively moving from a procedural architecture to an object-oriented architecture.

Current responsibility flow:

```text
main.py
   │
   ├── analyzes directory
   │
   ├── classifies files
   │
   └── FileOrganizer
          │
          ├── organize_file()
          │
          └── handle_duplicate()
```

The objective is to keep each component focused on a single responsibility while making the project easier to maintain, test and extend.

---

## Error handling

The application includes handling for common filesystem problems, including:

* Invalid directories
* Permission problems
* Files that cannot be moved
* Unexpected filesystem errors
* Duplicate filenames

Errors are reported without stopping the entire organization process whenever possible.

At the end of the operation, the application provides a summary of successful operations and detected errors.

---

## Compatibility

The project is being developed with cross-platform compatibility in mind.

Current development focuses primarily on:

* Windows
* macOS

The implementation uses Python's standard filesystem libraries such as:

```python
pathlib
shutil
os
```

to minimize platform-specific dependencies.

---

## How to run

At the current development stage, the application can be launched with:

```bash
python3 main.py
```

The application then executes the organization workflow according to the current configuration and selected operation mode.

---

## Development status

### Phase 1 — MVP

* [x] Directory scanning
* [x] Basic file classification
* [x] Classification by extension
* [x] File moving
* [x] Destination folder creation

### Phase 2 — Robustness

* [x] Exception handling
* [x] Directory validation
* [x] Permission validation
* [x] Hidden file filtering
* [x] Error reporting
* [x] Duplicate detection
* [x] Duplicate file handling
* [x] Duplicate filename generation

### Phase 3 — Configurable

* [x] External classification rules
* [x] `categories.json`
* [x] Configurable file categories
* [x] Dry Run / simulation mode
* [x] Separation of configuration from business logic

### Phase 4 — Object-Oriented Architecture

* [x] Introduce `FileOrganizer`
* [x] Move organization logic into a class
* [x] Separate file organization responsibilities
* [x] `organize_file()`
* [x] `handle_duplicate()`
* [ ] Complete OOP refactor
* [ ] Review and improve class responsibilities
* [ ] Improve testability
* [ ] Add additional classification criteria
* [ ] Classification by file size
* [ ] Classification by date
* [ ] Classification by filename patterns

### Phase 5 — Application Features

* [ ] Graphical interface with PyQt
* [ ] Folder selection through GUI
* [ ] Visual Dry Run
* [ ] Organization history
* [ ] Undo last organization
* [ ] Advanced filters
* [ ] Import / Export configuration
* [ ] Operation reports
* [ ] Scheduled organization
* [ ] Additional user preferences

---

## Future architecture

The final objective is to evolve JGP-Organizer from a command-line learning project into a complete desktop application.

The planned architecture is approximately:

```text
                    JGP-Organizer
                          │
                    ┌─────┴─────┐
                    │    GUI    │
                    │   PyQt    │
                    └─────┬─────┘
                          │
                    Application
                       Logic
                          │
              ┌───────────┼───────────┐
              │           │           │
          Classifier   Organizer    Config
              │           │           │
              └───────────┼───────────┘
                          │
                    File System
```

The GUI will eventually become the main interface while the core organization logic remains independent from the user interface.

This separation will make it possible to test and reuse the core functionality independently from the GUI.

---

## Version history

### v0.4.0

* Introduced object-oriented organization logic
* Added `FileOrganizer`
* Added `organize_file()`
* Added `handle_duplicate()`
* Improved duplicate handling
* Continued separation of responsibilities
* Improved Dry Run behavior
* Prepared the project for the future PyQt interface

### v0.3.0

* Added exception handling
* Added directory validation
* Added permission validation
* Added hidden file filtering
* Added error summary
* Refactored application entry point
* Improved macOS compatibility

### v0.2.0

* Added external JSON classification rules
* Added configurable categories
* Added Dry Run mode
* Improved project modularity

### v0.1.0

* Initial functional MVP
* Directory scanning
* Extension-based classification
* Destination folder creation
* File moving

---

## Project goal

JGP-Organizer started as a Python learning project and is progressively evolving into a modular desktop file-management application.

The main goals are:

* Practice Python programming
* Apply object-oriented programming
* Work with the filesystem
* Build reusable software components
* Implement configuration-driven behavior
* Practice exception handling
* Develop automated testing
* Build a graphical application with PyQt
* Apply software architecture and separation of responsibilities

---

## Author

Built by **JonasDev** as a Python learning and development project.
