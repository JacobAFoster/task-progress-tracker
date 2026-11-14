# Subjects & Tasks

A small offline desktop app for organising subjects (e.g. courses, projects)
into tasks and free-form notes. Everything is stored in plain JSON on your
machine — no accounts, no network calls.

Built with Python and Tkinter; runs anywhere Python 3.8+ and Tk are available.

---

## Features

- **Subjects sidebar** with a live progress bar per subject and a `done/total`
  count. The selected subject is highlighted.
- **Tasks** per subject, each with a title, status (`Not done` / `In progress`
  / `Done`) and a free-form description.
  - Add, rename, delete, and **reorder** tasks (`↑` / `↓` buttons or
    `Ctrl-Up` / `Ctrl-Down`).
  - Set status from the toolbar, double-click a row, or press `Return` to
    cycle through the three states.
  - **Search** box filters the task list by title or description without
    changing what's stored.
- **Notes** tab with a plain text editor per subject.
- **Undo** for the last delete: `Ctrl-Z` restores a deleted task or subject
  (including all its tasks and notes).
- **Autosave** with a 1-second debounce, plus a status line at the bottom of
  the window that shows the time of the last successful save.
- **Window state is remembered** — size, position, and the last selected
  subject are restored on next launch.
- **Atomic writes** with a temp file, so a crash mid-save can't corrupt
  `subjects.json`. A corrupt file is moved aside on load and a warning is
  shown rather than silently overwriting data.

---

## Requirements

- Python 3.8 or newer
- Tkinter (bundled with the official Python installers on Windows and macOS;
  on Linux you may need to install `python3-tk`)

No third-party packages.

---

## Running

```bash
python notes_app.py
