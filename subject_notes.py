import json
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

DATA_FILE = Path(__file__).with_name("subjects.json")

NOT_DONE, IN_PROGRESS, DONE = "Not done", "In progress", "Done"
STATUSES = [NOT_DONE, IN_PROGRESS, DONE]
ICONS = {NOT_DONE: "\u2610  Not done", IN_PROGRESS: "\u25d0  In progress", DONE: "\u2714  Done"}

SELECTED_BG = "#cfe3ff"
SELECTED_BORDER = "#7aa7e0"


class NotesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Subjects & Tasks")
        self.geometry("1000x620")
        self.minsize(700, 420)

        self._saving_disabled = False
        self._save_job = None
        self._refreshing = False
        self.current = None
        self.current_task = None
        self.row_widgets = {}          # subject name -> dict of widgets in the sidebar
        self.status_buttons = []
        self.task_action_buttons = []

        self.data = self.load()
        self.build_ui()
        self.refresh_list()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------------------------------------------- storage
    def load(self):
        try:
            text = DATA_FILE.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        except OSError:
            return {}
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as e:
            backup = DATA_FILE.with_name(
                f"{DATA_FILE.name}.corrupt-{int(time.time())}"
            )
            moved = None
            try:
                DATA_FILE.replace(backup)
                moved = backup
            except OSError:
                moved = None
            if moved is None:
                # We could not move the bad file out of the way; refuse to
                # overwrite it on the next save so nothing is destroyed.
                self._saving_disabled = True
            messagebox.showwarning(
                "Could not read subjects.json",
                f"{e}\n\n"
                + (
                    f"The old file was renamed to:\n{moved}"
                    if moved is not None
                    else "The old file could not be moved; saving is disabled "
                         "for this session so it is not overwritten."
                ),
                parent=self,
            )
            return {}
        if not isinstance(raw, dict):
            return {}
        data = {}
        for name, value in raw.items():
            if isinstance(value, str):
                value = {"notes": value, "tasks": []}
            if not isinstance(value, dict):
                continue
            value.setdefault("notes", "")
            value.setdefault("tasks", [])
            if not isinstance(value["tasks"], list):
                value["tasks"] = []
            for t in value["tasks"]:
                if not isinstance(t, dict):
                    continue
                t.setdefault("status", NOT_DONE)
                t.setdefault("description", "")
                t.setdefault("title", "")
            data[name] = value
        return data

    def write_file(self):
        if self._saving_disabled:
            return
        tmp = DATA_FILE.with_name(DATA_FILE.name + ".tmp")
        tmp.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        # Atomic rename: subjects.json is either the old version or the new
        # one, never a half-written file.
        tmp.replace(DATA_FILE)

    def save_task_desc(self):
        if self.current and self.current_task is not None:
            tasks = self.data[self.current]["tasks"]
            if self.current_task < len(tasks):
                tasks[self.current_task]["description"] = self.desc.get("1.0", "end-1c")

    def save_current(self):
        # Flush any pending debounced save so it does not fire later against
        # the wrong subject.
        if self._save_job:
            self.after_cancel(self._save_job)
            self._save_job = None
        if self.current in self.data:
            self.data[self.current]["notes"] = self.notes.get("1.0", "end-1c")
            self.save_task_desc()
            self.write_file()

    def schedule_save(self, _event=None):
        if self.current is None:
            return
        if self._save_job:
            self.after_cancel(self._save_job)
        self._save_job = self.after(1000, self._do_save)

    def _do_save(self):
        self._save_job = None
        self.save_current()

    # ------------------------------------------------------------------- UI
    def build_ui(self):
        left = tk.Frame(self, padx=8, pady=8)
        left.pack(side="left", fill="y")
        tk.Label(left, text="Subjects", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        # ---- scrollable sidebar where every subject gets its own progress bar
        lf = tk.Frame(left)
        lf.pack(fill="both", expand=True, pady=4)

        self.canvas = tk.Canvas(lf, width=280, highlightthickness=0)
        sb = tk.Scrollbar(lf, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.rows = tk.Frame(self.canvas)
        self._rows_id = self.canvas.create_window((0, 0), window=self.rows, anchor="nw")
        self.rows.bind("<Configure>", self._on_rows_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        style = ttk.Style(self)
        style.configure("Subject.Horizontal.TProgressbar",
                        thickness=9, troughcolor="#e8e8e8")
        style.configure("Done.Horizontal.TProgressbar",
                        thickness=9, troughcolor="#e8e8e8", background="#2e7d32")
        style.configure("Empty.Horizontal.TProgressbar",
                        thickness=9, troughcolor="#e8e8e8", background="#a0a0a0")

        b = tk.Frame(left)
        b.pack(fill="x")
        tk.Button(b, text="Add", command=self.add_subject).pack(side="left", expand=True, fill="x")
        tk.Button(b, text="Rename", command=self.rename_subject).pack(side="left", expand=True, fill="x")
        tk.Button(b, text="Delete", command=self.delete_subject).pack(side="left", expand=True, fill="x")

        right = tk.Frame(self, padx=8, pady=8)
        right.pack(side="right", fill="both", expand=True)

        self.title_label = tk.Label(
            right, text="Select or add a subject", font=("Segoe UI", 13, "bold"), anchor="w"
        )
        self.title_label.pack(fill="x")

        tabs = ttk.Notebook(right)
        tabs.pack(fill="both", expand=True, pady=4)

        tasks_tab = tk.Frame(tabs, padx=6, pady=6)
        tabs.add(tasks_tab, text="Tasks")

        top = tk.Frame(tasks_tab)
        top.pack(fill="x")
        tk.Button(top, text="Add task", command=self.add_task).pack(side="left")
        b = tk.Button(top, text="Rename", command=self.rename_task)
        b.pack(side="left", padx=(4, 0))
        self.task_action_buttons.append(b)
        b = tk.Button(top, text="Delete", command=self.delete_task)
        b.pack(side="left", padx=4)
        self.task_action_buttons.append(b)
        tk.Label(top, text="Mark as:").pack(side="left", padx=(16, 4))
        for status in STATUSES:
            b = tk.Button(top, text=ICONS[status], command=lambda s=status: self.set_status(s))
            b.pack(side="left", padx=2)
            self.status_buttons.append(b)
        self.progress = tk.Label(top, text="", fg="gray40")
        self.progress.pack(side="right")

        tf = tk.Frame(tasks_tab)
        tf.pack(fill="both", expand=True, pady=6)
        self.tree = ttk.Treeview(tf, columns=("status", "title"), show="headings", height=8,
                                 selectmode="browse")
        self.tree.heading("status", text="Status")
        self.tree.heading("title", text="Task")
        self.tree.column("status", width=130, stretch=False)
        self.tree.column("title", width=400)
        self.tree.tag_configure(DONE, foreground="#2e7d32")
        self.tree.tag_configure(IN_PROGRESS, foreground="#b36b00")
        tsb = tk.Scrollbar(tf, command=self.tree.yview)
        self.tree.config(yscrollcommand=tsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.tree.bind("<Double-1>", self.cycle_status)
        self.tree.bind("<Delete>", lambda e: self.delete_task())
        self.tree.bind("<Return>", lambda e: self.cycle_status())

        self.desc_label = tk.Label(tasks_tab, text="Description", anchor="w",
                                   font=("Segoe UI", 10, "bold"))
        self.desc_label.pack(fill="x")
        df = tk.Frame(tasks_tab)
        df.pack(fill="both", expand=True)
        self.desc = tk.Text(df, wrap="word", undo=True, height=8, font=("Segoe UI", 11),
                            state="disabled")
        dsb = tk.Scrollbar(df, command=self.desc.yview)
        self.desc.config(yscrollcommand=dsb.set)
        self.desc.pack(side="left", fill="both", expand=True)
        dsb.pack(side="right", fill="y")
        self.desc.bind("<KeyRelease>", self.schedule_save)

        notes_tab = tk.Frame(tabs, padx=6, pady=6)
        tabs.add(notes_tab, text="Notes")
        nf = tk.Frame(notes_tab)
        nf.pack(fill="both", expand=True)
        self.notes = tk.Text(nf, wrap="word", undo=True, font=("Segoe UI", 11), state="disabled")
        nsb = tk.Scrollbar(nf, command=self.notes.yview)
        self.notes.config(yscrollcommand=nsb.set)
        self.notes.pack(side="left", fill="both", expand=True)
        nsb.pack(side="right", fill="y")
        self.notes.bind("<KeyRelease>", self.schedule_save)

        self.bind("<Control-n>", lambda e: self.add_subject())
        self.bind("<Control-t>", lambda e: self.add_task())

    # -------------------------------------------------- subject sidebar rows
    def _on_rows_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self._rows_id, width=event.width)

    def _on_mousewheel(self, event):
        step = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(step, "units")

    def _bar_style(self, frac):
        if frac >= 1.0:
            return "Done.Horizontal.TProgressbar"
        if frac == 0.0:
            return "Empty.Horizontal.TProgressbar"
        return "Subject.Horizontal.TProgressbar"

    def _make_subject_row(self, name):
        tasks = self.data[name]["tasks"]
        total = len(tasks)
        done = sum(t["status"] == DONE for t in tasks)
        frac = (done / total) if total else 0.0

        bg = self.rows.cget("bg")
        row = tk.Frame(self.rows, padx=6, pady=4, bd=0,
                       highlightthickness=1, highlightbackground=bg)
        row.pack(fill="x", padx=2, pady=2)

        top = tk.Frame(row)
        top.pack(fill="x")
        label = tk.Label(top, text=name, anchor="w", font=("Segoe UI", 10, "bold"))
        label.pack(side="left", fill="x", expand=True)
        count = tk.Label(top, text=(f"{done}/{total}" if total else "\u2013"),
                         anchor="e", fg="gray35", font=("Segoe UI", 9))
        count.pack(side="right")

        bar = ttk.Progressbar(row, style=self._bar_style(frac),
                              mode="determinate", maximum=1.0, value=frac)
        bar.pack(fill="x", pady=(3, 0))

        self.row_widgets[name] = {
            "row": row, "top": top, "label": label, "count": count, "bar": bar,
        }

        for w in (row, top, label, count, bar):
            w.bind("<Button-1>", lambda _e, n=name: self.select_subject(n))
            w.bind("<MouseWheel>", self._on_mousewheel)
            w.bind("<Button-4>", lambda _e: self.canvas.yview_scroll(-1, "units"))
            w.bind("<Button-5>", lambda _e: self.canvas.yview_scroll(1, "units"))

    def _paint_selection(self):
        base = self.rows.cget("bg")
        for name, w in self.row_widgets.items():
            selected = (name == self.current)
            bg = SELECTED_BG if selected else base
            w["row"].configure(bg=bg,
                               highlightbackground=SELECTED_BORDER if selected else base)
            w["top"].configure(bg=bg)
            w["label"].configure(bg=bg)
            w["count"].configure(bg=bg)

    def update_progress_bars(self, name=None):
        """Refresh one subject's progress bar (or all of them when name is None)."""
        names = [name] if name is not None else list(self.row_widgets)
        for n in names:
            if n not in self.row_widgets:
                continue
            w = self.row_widgets[n]
            tasks = self.data.get(n, {}).get("tasks", [])
            total = len(tasks)
            done = sum(t["status"] == DONE for t in tasks)
            frac = (done / total) if total else 0.0
            w["bar"].configure(value=frac, style=self._bar_style(frac))
            w["count"].configure(text=(f"{done}/{total}" if total else "\u2013"))

    def select_subject(self, name):
        if name == self.current:
            return
        self.save_current()
        self.show_subject(name)

    def refresh_list(self):
        y = self.canvas.yview()[0] if self.row_widgets else 0.0
        for child in self.rows.winfo_children():
            child.destroy()
        self.row_widgets = {}
        if not self.data:
            tk.Label(self.rows,
                     text="No subjects yet.\nClick Add to get started.",
                     fg="gray45", justify="center", pady=20).pack(fill="x")
        for name in self.data:
            self._make_subject_row(name)
        self.rows.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(y)
        self._paint_selection()

    # ------------------------------------------------------------- subjects
    def show_subject(self, name):
        self.current = name
        self.title_label.config(text=name)
        self.notes.config(state="normal")
        self.notes.delete("1.0", "end")
        self.notes.insert("1.0", self.data[name]["notes"])
        self.notes.edit_reset()
        self.current_task = None
        self.refresh_tasks()
        self._paint_selection()

    def clear_editor(self):
        self.current = None
        self.current_task = None
        self.title_label.config(text="Select or add a subject")
        self.notes.config(state="normal")
        self.notes.delete("1.0", "end")
        self.notes.config(state="disabled")
        self.refresh_tasks()
        self._paint_selection()

    def add_subject(self):
        name = simpledialog.askstring("Add subject", "Subject name:", parent=self)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self.data:
            messagebox.showwarning("Exists", f'"{name}" already exists.')
            return
        self.save_current()
        self.data[name] = {"notes": "", "tasks": []}
        self.write_file()
        self.current = name
        self.refresh_list()
        self.show_subject(name)

    def rename_subject(self):
        if not self.current:
            return
        new = simpledialog.askstring("Rename subject", "New name:",
                                     initialvalue=self.current, parent=self)
        if not new or not new.strip() or new.strip() == self.current:
            return
        new = new.strip()
        if new in self.data:
            messagebox.showwarning("Exists", f'"{new}" already exists.')
            return
        self.save_current()
        self.data = {(new if k == self.current else k): v for k, v in self.data.items()}
        self.write_file()
        self.current = new
        self.title_label.config(text=new)
        self.refresh_list()

    def delete_subject(self):
        if not self.current:
            return
        if not messagebox.askyesno(
            "Delete subject", f'Delete "{self.current}" and all its tasks and notes?'
        ):
            return
        del self.data[self.current]
        self.write_file()
        self.clear_editor()
        self.refresh_list()

    # ---------------------------------------------------------------- tasks
    def tasks(self):
        return self.data[self.current]["tasks"] if self.current else []

    def _sync_task_buttons(self):
        state = "normal" if self.current_task is not None else "disabled"
        for b in self.status_buttons + self.task_action_buttons:
            b.configure(state=state)

    def refresh_tasks(self, select=None):
        self._refreshing = True
        self.tree.delete(*self.tree.get_children())
        tasks = self.tasks()
        for i, t in enumerate(tasks):
            self.tree.insert("", "end", iid=str(i), values=(ICONS[t["status"]], t["title"]),
                             tags=(t["status"],))
        if select is not None and select < len(tasks):
            self.tree.selection_set(str(select))
            self.tree.see(str(select))

        done = sum(t["status"] == DONE for t in tasks)
        self.progress.config(text=f"{done}/{len(tasks)} done" if tasks else "")
        if select is not None and select < len(tasks):
            self.show_task(select)
        else:
            self.clear_task_editor()
        self._refreshing = False

        # Only the current subject's bar can have changed.
        self.update_progress_bars(self.current)

    def show_task(self, idx):
        self.current_task = idx
        t = self.tasks()[idx]
        title = t["title"] if len(t["title"]) <= 50 else t["title"][:47] + "\u2026"
        self.desc_label.config(text=f"Description \u2014 {title}")
        self.desc.config(state="normal")
        self.desc.delete("1.0", "end")
        self.desc.insert("1.0", t["description"])
        self.desc.edit_reset()
        self._sync_task_buttons()

    def clear_task_editor(self):
        self.current_task = None
        self.desc_label.config(text="Description")
        self.desc.config(state="normal")
        self.desc.delete("1.0", "end")
        self.desc.config(state="disabled")
        self._sync_task_buttons()

    def on_task_select(self, _event=None):
        if self._refreshing:
            return
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx == self.current_task:
            return
        self.save_task_desc()
        self.show_task(idx)

    def add_task(self):
        if not self.current:
            messagebox.showinfo("No subject", "Add or select a subject first.")
            return
        title = simpledialog.askstring("Add task", "Task title:", parent=self)
        if not title or not title.strip():
            return
        self.save_task_desc()
        self.tasks().append({"title": title.strip(), "status": NOT_DONE, "description": ""})
        self.write_file()
        self.refresh_tasks(select=len(self.tasks()) - 1)
        self.desc.focus_set()

    def rename_task(self):
        if self.current_task is None:
            return
        t = self.tasks()[self.current_task]
        new = simpledialog.askstring("Rename task", "New title:", initialvalue=t["title"], parent=self)
        if not new or not new.strip():
            return
        self.save_task_desc()
        t["title"] = new.strip()
        self.write_file()
        self.refresh_tasks(select=self.current_task)

    def delete_task(self):
        if self.current_task is None:
            return
        idx = self.current_task
        t = self.tasks()[idx]
        if not messagebox.askyesno("Delete task", f'Delete task "{t["title"]}"?'):
            return
        del self.tasks()[idx]
        self.current_task = None
        self.write_file()
        n = len(self.tasks())
        self.refresh_tasks(select=min(idx, n - 1) if n else None)

    def set_status(self, status):
        if self.current_task is None:
            return
        idx = self.current_task
        self.save_task_desc()
        self.tasks()[idx]["status"] = status
        self.write_file()
        self.refresh_tasks(select=idx)

    def cycle_status(self, _event=None):
        if self.current_task is None:
            return
        cur = self.tasks()[self.current_task]["status"]
        self.set_status(STATUSES[(STATUSES.index(cur) + 1) % len(STATUSES)])

    def on_close(self):
        self.save_current()
        self.destroy()


if __name__ == "__main__":
    NotesApp().mainloop()