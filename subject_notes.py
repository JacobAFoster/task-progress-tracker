import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

DATA_FILE = Path(__file__).with_name("subjects.json")

NOT_DONE, IN_PROGRESS, DONE = "Not done", "In progress", "Done"
STATUSES = [NOT_DONE, IN_PROGRESS, DONE]
ICONS = {NOT_DONE: "\u2610  Not done", IN_PROGRESS: "\u25d0  In progress", DONE: "\u2714  Done"}


class NotesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Subjects & Tasks")
        self.geometry("1000x620")
        self.minsize(700, 420)

        self.data = self.load()
        self.current = None
        self.current_task = None
        self._save_job = None
        self._refreshing = False

        self.build_ui()
        self.refresh_list()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load(self):
        try:
            raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        data = {}
        for name, value in raw.items():
            if isinstance(value, str):
                value = {"notes": value, "tasks": []}
            value.setdefault("notes", "")
            value.setdefault("tasks", [])
            for t in value["tasks"]:
                t.setdefault("status", NOT_DONE)
                t.setdefault("description", "")
            data[name] = value
        return data

    def write_file(self):
        DATA_FILE.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def save_task_desc(self):
        if self.current and self.current_task is not None:
            tasks = self.data[self.current]["tasks"]
            if self.current_task < len(tasks):
                tasks[self.current_task]["description"] = self.desc.get("1.0", "end-1c")

    def save_current(self):
        if self.current in self.data:
            self.data[self.current]["notes"] = self.notes.get("1.0", "end-1c")
            self.save_task_desc()
            self.write_file()

    def schedule_save(self, _event=None):
        if self._save_job:
            self.after_cancel(self._save_job)
        self._save_job = self.after(1000, self.save_current)

    def build_ui(self):
        left = tk.Frame(self, padx=8, pady=8)
        left.pack(side="left", fill="y")
        tk.Label(left, text="Subjects", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        lf = tk.Frame(left)
        lf.pack(fill="both", expand=True, pady=4)
        self.listbox = tk.Listbox(lf, width=24, exportselection=False, activestyle="none")
        sb = tk.Scrollbar(lf, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.on_subject_select)

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
        tk.Button(top, text="Rename", command=self.rename_task).pack(side="left", padx=(4, 0))
        tk.Button(top, text="Delete", command=self.delete_task).pack(side="left", padx=4)
        tk.Label(top, text="Mark as:").pack(side="left", padx=(16, 4))
        for status in STATUSES:
            tk.Button(top, text=ICONS[status], command=lambda s=status: self.set_status(s)).pack(
                side="left", padx=2
            )
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

    def refresh_list(self, select=None):
        self.listbox.delete(0, "end")
        for name in self.data:
            self.listbox.insert("end", name)
        if select in self.data:
            idx = list(self.data).index(select)
            self.listbox.selection_set(idx)
            self.listbox.see(idx)

    def show_subject(self, name):
        self.current = name
        self.title_label.config(text=name)
        self.notes.config(state="normal")
        self.notes.delete("1.0", "end")
        self.notes.insert("1.0", self.data[name]["notes"])
        self.notes.edit_reset()
        self.current_task = None
        self.refresh_tasks()

    def clear_editor(self):
        self.current = None
        self.current_task = None
        self.title_label.config(text="Select or add a subject")
        self.notes.config(state="normal")
        self.notes.delete("1.0", "end")
        self.notes.config(state="disabled")
        self.refresh_tasks()

    def on_subject_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        name = self.listbox.get(sel[0])
        if name == self.current:
            return
        self.save_current()
        self.show_subject(name)

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
        self.refresh_list(select=name)
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
        self.refresh_list(select=new)

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

    def tasks(self):
        return self.data[self.current]["tasks"] if self.current else []

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
        self._refreshing = False

        done = sum(t["status"] == DONE for t in tasks)
        self.progress.config(text=f"{done}/{len(tasks)} done" if tasks else "")
        if select is not None and select < len(tasks):
            self.show_task(select)
        else:
            self.clear_task_editor()

    def show_task(self, idx):
        self.current_task = idx
        t = self.tasks()[idx]
        self.desc_label.config(text=f"Description \u2014 {t['title']}")
        self.desc.config(state="normal")
        self.desc.delete("1.0", "end")
        self.desc.insert("1.0", t["description"])
        self.desc.edit_reset()

    def clear_task_editor(self):
        self.current_task = None
        self.desc_label.config(text="Description")
        self.desc.config(state="normal")
        self.desc.delete("1.0", "end")
        self.desc.config(state="disabled")

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
        t = self.tasks()[self.current_task]
        if not messagebox.askyesno("Delete task", f'Delete task "{t["title"]}"?'):
            return
        del self.tasks()[self.current_task]
        self.current_task = None
        self.write_file()
        self.refresh_tasks()

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