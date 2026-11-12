# Subjects & Tasks

A simple desktop app built with Python and tkinter. Create subjects, add tasks to each one, mark them as not done, in progress or done, and write descriptions and free-form notes.

## Requirements

- Python 3.8 or newer
- tkinter (included with the standard Python installers for Windows and macOS)

On some Linux distributions tkinter is a separate package. On Debian or Ubuntu:

```
sudo apt install python3-tk
```

No other dependencies are needed.

## Running

```
python subject_notes.py
```

On some systems the command is `python3` instead of `python`.

## Using the app

### Subjects

The list on the left holds your subjects.

- **Add** creates a new subject.
- **Rename** renames the selected subject.
- **Delete** removes the selected subject, along with all of its tasks and notes (you will be asked to confirm).

### Tasks

Select a subject and open the **Tasks** tab.

- **Add task** creates a task in the selected subject.
- **Rename** and **Delete** work on the selected task.
- **Mark as** sets the selected task to *Not done*, *In progress* or *Done*. Double-clicking a task cycles through the three statuses.
- Select a task and type in the **Description** box underneath to add details to it. Each task has its own description.
- A counter in the corner shows how many tasks in the subject are done.

In progress tasks are shown in orange and done tasks in green.

### Notes

The **Notes** tab is a free writing area for the selected subject, separate from its tasks.

## Saving

Everything saves automatically: about a second after you stop typing, whenever you switch subjects or tasks, and when you close the window. There is no save button.

Your data is stored in `subjects.json`, which is created in the same folder as `subject_notes.py`. To back up or move your data, copy that file. To start fresh, delete it.

If you have a `subjects.json` from an earlier notes-only version of the app, it is upgraded automatically and your old notes appear in each subject's Notes tab.

## Data format

`subjects.json` is plain JSON, so it is easy to read or edit by hand:

```json
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
```

Valid task statuses are `Not done`, `In progress` and `Done`.

## Files

- `subject_notes.py`: the application
- `subjects.json`: your data (created on first use)

add progress meter to program
bug fix 
optimization fixes
