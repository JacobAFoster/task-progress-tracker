Subjects & Tasks

A small desktop app for keeping notes and task lists, organised by subject. It is built with Python and Tkinter and stores everything in a single JSON file next to the script.

Features
Subjects sidebar with a progress bar and a done/total count for each subject
Tasks with three statuses: Not done, In progress, Done
Per-task descriptions and a free-form notes tab for each subject
Autosave: saves one second after you stop typing, when you switch subject, and when you close the window
Safe storage: atomic writes, backups of unreadable files, and a visible warning if a save fails
Requirements
Python 3.8 or newer
Tkinter (included with the standard Python installers for Windows and macOS)
On Debian/Ubuntu: sudo apt install python3-tk

No third-party packages are needed.

Running
bash
python notes_app.py

subjects.json is created in the same folder as the script the first time you add a subject.

Using the app
Action	How
Add / rename / delete a subject	Buttons under the sidebar (Ctrl+N adds)
Add a task	Add task button or Ctrl+T
Rename / delete a task	Rename / Delete buttons, or Delete key to delete
Change a task's status	Mark as buttons, or press Enter / double-click to cycle through the statuses
Edit a description	Select a task, then type in the Description box
Edit notes	Open the Notes tab

Ctrl+N and Ctrl+T also work while you are typing in the description or notes boxes.

Data file

Data lives in subjects.json:

json
{
  "Maths": {
    "notes": "Revise chapter 4",
    "tasks": [
      { "title": "Past paper", "status": "In progress", "description": "Section B only" }
    ]
  }
}

Valid statuses are Not done, In progress and Done. On load, anything unexpected is cleaned up: older files that stored a subject as a plain string are converted, and missing fields get defaults.

Backups and error handling
Atomic saves: data is written to subjects.json.tmp and then swapped in, so a crash mid-write cannot leave a half-written file. The temp file is removed if anything goes wrong.
Unreadable file: if subjects.json is not valid JSON, the app renames it to subjects.json.corrupt-<timestamp> and starts empty. If it can't be renamed, saving is disabled for the session so the file is never overwritten, and a banner explains why.
Cleaned-up file: if loading had to change or drop anything, the original text is saved as subjects.json.bak-<timestamp> before the first save overwrites it.
Failed saves: a red "Not saved" banner stays visible until a write succeeds. You also get a one-time error dialog.
Encoding: files are read as utf-8-sig, so a UTF-8 BOM added by editors such as Notepad is fine.
Changes in this version

Bug fixes:

Ctrl+N / Ctrl+T no longer also trigger Tk's built-in transpose and cursor-down inside text boxes.
Removed the misleading _refreshing flag; the on_task_select index check already handles queued select events.
A UTF-8 BOM no longer makes a valid file look corrupt.
Data that load() cleans up is backed up before being overwritten.
Progress bar colour and thickness now apply on Windows (the clam theme is used).
Saving is triggered by <<Modified>>, so paste, cut and undo are saved, and arrow keys no longer trigger a save.
Changing a status updates only that row, so the description box keeps its cursor and undo history.
Write failures show a persistent warning instead of a one-time popup.

Also: temp files are cleaned up after a failed save, a pending autosave is cancelled when a subject is deleted, and reused variable names were renamed.

Known limitations
Double-click cycles a task's status, which is easy to trigger by accident.
Tasks are identified by list position, and there is no reordering.
Fonts are set to Segoe UI, so they fall back to a default on macOS and Linux.
Subject names are case-sensitive (Math and math are different subjects).
The subject sidebar is not keyboard navigable.
