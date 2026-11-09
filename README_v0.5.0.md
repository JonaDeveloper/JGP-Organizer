# JGP Organizer

A configurable and modular file organizer built with Python.

JGP Organizer scans a directory, classifies files according to configurable rules, and organizes them automatically into category-based folders. The project has evolved from a procedural file organizer into an object-oriented application core with configurable rules, SQLite persistence, rule validation and automated tests.

**Current version:** `v0.5.0` — Object-oriented rule management, SQLite persistence and hierarchical rule validation

---

## Features

### File organization

* Directory scanning and file classification
* Automatic classification by extension
* External classification rules using `categories.json`
* Automatic creation of destination folders
* Automatic file organization
* Dry Run / simulation mode
* Duplicate filename detection and handling
* Automatic renaming of duplicate files
* Dedicated `Duplicates` folder for duplicate files
* Exception handling for common filesystem errors
* Hidden file filtering
* Directory and permission validation
* Operation summary and error reporting

### Rule management

* Object-oriented rule model (`Rule`)
* Configurable rule types: extension, name, regex and size
* SQLite persistence for rules
* Create, update and delete custom rules
* Protection of default rules
* Limit of five custom rules
* Rule validation for type, value, priority and parent relationship
* Detection of conflicting file extensions
* Hierarchical parent-child rule relationships
* Prevention of invalid parent references and circular hierarchies
* Protection against deleting rules that still have child rules

### Development and quality

* Modular architecture with separated responsibilities
* Automated tests with `pytest`
* Cross-platform development considerations for Windows and macOS

> The PyQt6 graphical interface is planned for a future development phase and is not included in this release.

---

## How it works

The file organization workflow is divided into several responsibilities:

1. **Directory analysis**  
   The application scans the selected directory and identifies the files that can be organized.

2. **File classification**  
   Files are classified according to the configured rules.

3. **Organization**  
   The organization component performs the required filesystem operations.

4. **Duplicate handling**  
   If a file with the same name already exists in the destination, the application handles the duplicate instead of overwriting the existing file.

5. **Dry Run mode**  
   When simulation mode is enabled, no files or directories are modified. The application reports the operations that would be performed.

6. **Summary**  
   At the end of the operation, the application reports the results and any errors.

---

## Rule management and persistence

JGP Organizer uses SQLite to store organization rules.

The rule-management functionality supports:

* Creating custom rules
* Updating existing custom rules
* Deleting custom rules
* Protecting default rules from modification or deletion
* Validating rule attributes before they are stored
* Detecting conflicts between extension rules
* Organizing rules through parent-child relationships

### Hierarchical rules

Rules can be organized into multiple levels. For example:

```text
Images
└── Holidays
    ├── Italy
    └── France
```

The validation layer checks parent references and prevents circular relationships. A rule cannot be deleted while other rules depend on it as their parent.

### Supported rule types

The rule model supports the following types:

* `extension`
* `name`
* `regex`
* `size`

Each type has its own value validation. Extension conflicts are checked before a rule is inserted or updated.

---

## Configuration

The file-classification configuration is stored externally in `categories.json`.

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

JGP Organizer includes a simulation mode that allows the user to preview the organization process without modifying the filesystem.

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

JGP Organizer does not blindly overwrite files when a filename already exists in the destination.

When a duplicate is detected, the application handles it separately and generates a new filename when necessary.

For example:

```text
photo.jpg
photo_1.jpg
photo_2.jpg
```

Duplicates can also be redirected to a dedicated `Duplicates` directory according to the organization logic.

---

## Database

SQLite is used to persist the application's rules without requiring a separate database server.

The current database layer provides operations to insert, retrieve, update and delete rules. Validation is performed by the application before changes are stored.

The database schema is intentionally kept simple for the current project scope. Rule validation and hierarchy protection are handled by the existing Python logic.

---

## Project structure

The project uses a modular structure. The exact package layout may evolve as development continues.

Main responsibilities include:

| Component | Responsibility |
|---|---|
| Application entry point | Coordinates the application workflow |
| Configuration | Loads configurable classification rules |
| Classification logic | Determines the category of each file |
| Organizer | Performs filesystem operations and handles duplicates |
| Rule model and validators | Represent and validate organization rules |
| Database layer | Persists rules in SQLite |
| Tests | Verify the behavior of the application and its rule-management components |

---

## Architecture

The project separates the main areas of responsibility:

```text
JGP Organizer
│
├── File organization
│   ├── Directory analysis
│   ├── File classification
│   ├── File operations
│   └── Duplicate handling
│
├── Rule management
│   ├── Rule model
│   ├── Rule validation
│   ├── Conflict validation
│   └── Parent-child hierarchy
│
├── Persistence
│   └── SQLite database
│
└── Automated tests
```

The graphical interface will be added in a future phase and will use the existing application logic rather than duplicating it.

---

## Error handling

The application includes handling for common filesystem problems, including:

* Invalid directories
* Permission problems
* Files that cannot be moved
* Unexpected filesystem errors
* Duplicate filenames

Errors are reported without stopping the entire organization process whenever possible.

---

## Compatibility

The project is being developed with cross-platform compatibility in mind.

Current development focuses primarily on:

* Windows
* macOS

The implementation uses Python's standard filesystem and database libraries where appropriate, including:

```python
pathlib
shutil
sqlite3
```

---

## How to run

At the current development stage, the application can be launched from the project environment using its existing entry point.

For the current command-line workflow, use:

```bash
python3 main.py
```

The graphical interface is not yet available in `v0.5.0`.

---

## Tests

The project uses `pytest` for automated testing.

Run the test suite from the project root:

```bash
python -m pytest
```

**Latest reported result for v0.5.0 development:** `113 passed`.

This result was reported from the development environment on macOS using Python 3.13.5 and pytest 9.1.1.

---

## Development status

### Phase 1 — Core file organization

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

### Phase 3 — Configurable rules and simulation

* [x] External classification rules
* [x] `categories.json`
* [x] Configurable file categories
* [x] Dry Run / simulation mode
* [x] Separation of configuration from business logic

### Phase 4 — Object-oriented rule management

* [x] Object-oriented rule model
* [x] Rule types and values
* [x] Rule priority validation
* [x] Parent-child rule relationships
* [x] Hierarchical cycle prevention
* [x] Rule conflict validation
* [x] Separation of validation responsibilities

### Phase 5 — SQLite persistence

* [x] SQLite database
* [x] Insert custom rules
* [x] Update custom rules
* [x] Delete custom rules
* [x] Protect default rules
* [x] Enforce the custom-rule limit in application logic
* [x] Protect parent-child dependencies during deletion

### Phase 6 — Validation and automated testing

* [x] Unit tests for rule validation
* [x] Database integration tests
* [x] Tests for hierarchical relationships
* [x] Tests for invalid parent references and cycles
* [x] Tests for rule conflicts
* [x] **113 automated tests passing**

### Phase 7 — Graphical user interface (planned)

* [ ] PyQt6 main window
* [ ] Directory selection through GUI
* [ ] Visual Dry Run
* [ ] Visual rule management
* [ ] Integration with the existing organization workflow

### Future improvements

* [ ] Login and access control, according to the final academic requirements
* [ ] Organization history
* [ ] Operation reports
* [ ] Undo functionality
* [ ] Scheduled organization
* [ ] Additional user preferences

---

## Version history

### v0.5.0 — Object-oriented rule management, SQLite and validation

* Expanded the object-oriented architecture with a dedicated rule model.
* Added SQLite persistence for organization rules.
* Implemented rule creation, updating and deletion.
* Added validation for rule types, values, priorities and parent relationships.
* Added extension conflict detection.
* Added hierarchical parent-child rule relationships.
* Prevented invalid parent references and circular hierarchies.
* Prevented deleting rules that still have child rules.
* Expanded automated unit and database integration tests.
* Reached 113 passing automated tests during development.

### v0.4.0 — Configurable rules, Dry Run and main refactoring

* Added external JSON-based classification rules.
* Introduced Dry Run mode.
* Improved duplicate simulation and handling.
* Refactored the main workflow into smaller functions.
* Improved separation of responsibilities.

### v0.3.0

* Added exception handling.
* Added directory validation.
* Added permission validation.
* Added hidden file filtering.
* Added error summary.
* Improved macOS compatibility.

### v0.2.0

* Added external JSON classification rules.
* Added configurable categories.
* Added Dry Run mode.
* Improved project modularity.

### v0.1.0

* Initial functional MVP.
* Directory scanning.
* Extension-based classification.
* Destination folder creation.
* File moving.

---

## Roadmap

The next development milestone is the PyQt6 graphical interface. The goal is to turn the existing application core into a desktop application while preserving the separation between interface, business logic and persistence.

The target for the stable `v1.0.0` release is the end of 2026. The final scope will prioritize the required application workflows, automated tests, installation instructions and the academic project requirements.

---

## Author

Built by **JonasDeveloper** as a Python learning and development project.
