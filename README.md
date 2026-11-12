Subjects & Tasks

A simple desktop app built with Python and tkinter. Create subjects, add tasks to each one, mark them as not done, in progress or done, and write descriptions and free-form notes.

Every subject in the sidebar now has its own progress bar, so you can see at a glance how much of each subject is finished.
Requirements

    Python 3.8 or newer

    tkinter (included with the standard Python installers for Windows and macOS)

On some Linux distributions tkinter is a separate package. On Debian or Ubuntu:
text

sudo apt install python3-tk

No other dependencies are needed.
Running
text

python subject_notes.py

On some systems the command is python3 instead of python.
Using the app
Subjects

The list on the left holds your subjects.

    Add creates a new subject.

    Rename renames the selected subject.

    Delete removes the selected subject, along with all of its tasks and notes (you will be asked to confirm).

Each subject row shows:

    the subject name,

    a done/total counter of its tasks,

    a progress bar filled in proportion to how many tasks are marked Done.

Click any row to select that subject; the selected row is highlighted. The sidebar scrolls with the mouse wheel when you have more subjects than fit on screen.
Tasks

Select a subject and open the Tasks tab.

    Add task creates a task in the selected subject.

    Rename and Delete work on the selected task.

    Mark as sets the selected task to Not done, In progress or Done. Double-clicking a task cycles through the three statuses.

    Select a task and type in the Description box underneath to add details to it. Each task has its own description.

    A counter in the corner shows how many tasks in the subject are done.

In progress tasks are shown in orange and done tasks in green.

Whenever you change a task's status, add or delete a task, the subject's progress bar in the sidebar updates immediately.
Notes

The Notes tab is a free writing area for the selected subject, separate from its tasks.
Saving

Everything saves automatically: about a second after you stop typing, whenever you switch subjects or tasks, and when you close the window. There is no save button.

Your data is stored in subjects.json, which is created in the same folder as subject_notes.py. To back up or move your data, copy that file. To start fresh, delete it.

If you have a subjects.json from an earlier notes-only version of the app, it is upgraded automatically and your old notes appear in each subject's Notes tab.
Data format

subjects.json is plain JSON, so it is easy to read or edit by hand:
json

{
  "Maths": {
    "notes": "Exam on Friday.",
    "tasks": [
      {
        "title": "Finish chapter 4 exercises",
        "status": "In progress",
        "description": "Questions 1 to 20, check answers at the back."
      }
    ]
  }
}

Valid task statuses are Not done, In progress and Done.
What's new in this version

Added

    A progress bar and done/total counter for every subject in the sidebar.

    A scrollable subject panel with mouse-wheel support and click-to-select rows.

    The selected subject is highlighted so it is always obvious which one you are editing.

Bug fixes

    Progress information now stays correct after renaming a subject, after adding or deleting tasks, and after changing a task's status.

    The subject list keeps its scroll position when it is refreshed, instead of jumping back to the top.

    Selecting a subject no longer clears the task list or loses the current task's description.

    Switching subjects with unsaved typing no longer discards the text — the pending save is flushed first.

    Deleting the last subject correctly resets the editor instead of leaving stale content on screen.

Optimisations

    Status changes update the progress bars in place rather than rebuilding the whole subject list, so the sidebar no longer flickers.

    Task rows are only redrawn when the task list actually changes, reducing redraw work on every keystroke.

    Duplicate saves are coalesced into a single write when several events fire close together.
