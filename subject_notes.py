import copy
import json
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk, colorchooser

DATA_FILE = Path(__file__).with_name("subjects.json")
UI_FILE = Path(__file__).with_name("ui_state.json")

NOT_DONE, IN_PROGRESS, DONE = "Not done", "In progress", "Done"
STATUSES = [NOT_DONE, IN_PROGRESS, DONE]
ICONS = {NOT_DONE: "\u2610  Not done", IN_PROGRESS: "\u25d0  In progress", DONE: "\u2714  Done"}


# ---------------------------------------------------------------- theme
class T:
    BG            = "#f4f6f9"
    SURFACE       = "#ffffff"
    SURFACE_ALT   = "#fafbfd"
    HOVER         = "#eef2f8"
    BORDER        = "#e3e7ed"
    BORDER_STRONG = "#cfd4dd"
    TEXT          = "#1f2430"
    TEXT_MUTED    = "#6b7280"
    TEXT_FAINT    = "#9aa1ab"
    ACCENT        = "#2f6fed"
    ACCENT_HOVER  = "#1f5ad6"
    ACCENT_SOFT   = "#e7efff"
    SUCCESS       = "#1a9d4b"
    SUCCESS_SOFT  = "#e3f6eb"
    WARNING       = "#c97a00"
    WARNING_SOFT  = "#fbeed1"
    DANGER        = "#d23b3b"
    DANGER_SOFT   = "#fde3e3"


DEFAULT_COLORS = {k: getattr(T, k) for k in vars(T)
                  if not k.startswith("_") and isinstance(getattr(T, k), str)}

COLOR_GROUPS = [
    ("App surfaces", ["BG", "SURFACE", "SURFACE_ALT", "HOVER"]),
    ("Borders",      ["BORDER", "BORDER_STRONG"]),
    ("Text",         ["TEXT", "TEXT_MUTED", "TEXT_FAINT"]),
    ("Accent",       ["ACCENT", "ACCENT_HOVER", "ACCENT_SOFT"]),
    ("Success",      ["SUCCESS", "SUCCESS_SOFT"]),
    ("Warning",      ["WARNING", "WARNING_SOFT"]),
    ("Danger",       ["DANGER", "DANGER_SOFT"]),
]

COLOR_LABELS = {
    "BG":            "App background",
    "SURFACE":       "Surface",
    "SURFACE_ALT":   "Surface alt",
    "HOVER":         "Hover",
    "BORDER":        "Border",
    "BORDER_STRONG": "Border strong",
    "TEXT":          "Text",
    "TEXT_MUTED":    "Text muted",
    "TEXT_FAINT":    "Text faint",
    "ACCENT":        "Accent",
    "ACCENT_HOVER":  "Accent hover",
    "ACCENT_SOFT":   "Accent soft",
    "SUCCESS":       "Success",
    "SUCCESS_SOFT":  "Success soft",
    "WARNING":       "Warning",
    "WARNING_SOFT":  "Warning soft",
    "DANGER":        "Danger",
    "DANGER_SOFT":   "Danger soft",
}


def pick_font(root, *candidates, default="TkDefaultFont"):
    fams = set(tkfont.families(root))
    for c in candidates:
        if c in fams:
            return c
    return tkfont.nametofont(default).actual("family")


def enable_hidpi(root):
    if sys.platform != "win32":
        return 1.0
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        return 1.0
    try:
        scale = root.winfo_fpixels('1i') / 96.0
        root.tk.call('tk', 'scaling', root.winfo_fpixels('1i') / 72.0)
        return scale
    except Exception:
        return 1.0


def setup_theme(root):
    ui = pick_font(root, "Segoe UI Variable", "Segoe UI", "SF Pro Text",
                   "Helvetica Neue", "Inter", "Cantarell", "DejaVu Sans")
    mono = pick_font(root, "Cascadia Mono", "SF Mono", "JetBrains Mono",
                     "Menlo", "Consolas", "DejaVu Sans Mono")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=T.BG, foreground=T.TEXT, font=(ui, 10))
    style.configure("TFrame",              background=T.BG)
    style.configure("Surface.TFrame",      background=T.SURFACE)
    style.configure("TLabel",              background=T.BG, foreground=T.TEXT)
    style.configure("Surface.TLabel",      background=T.SURFACE, foreground=T.TEXT)
    style.configure("Muted.TLabel",        background=T.BG, foreground=T.TEXT_MUTED)
    style.configure("SurfaceMuted.TLabel", background=T.SURFACE, foreground=T.TEXT_MUTED, font=(ui, 9))
    style.configure("H1.TLabel",           background=T.BG, foreground=T.TEXT, font=(ui, 16, "bold"))
    style.configure("H2.TLabel",           background=T.BG, foreground=T.TEXT, font=(ui, 12, "bold"))
    style.configure("Section.TLabel",      background=T.SURFACE, foreground=T.TEXT, font=(ui, 10, "bold"))

    style.configure("Accent.TButton",
        background=T.ACCENT, foreground="white", borderwidth=0,
        focuscolor=T.ACCENT, padding=(14, 7), font=(ui, 10, "bold"))
    style.map("Accent.TButton",
        background=[("disabled", "#a9bff4"), ("pressed", T.ACCENT_HOVER), ("active", T.ACCENT_HOVER)],
        foreground=[("disabled", "#eef2fb")])

    style.configure("Secondary.TButton",
        background=T.SURFACE, foreground=T.TEXT, borderwidth=1,
        bordercolor=T.BORDER, focuscolor=T.SURFACE, padding=(12, 6), font=(ui, 10))
    style.map("Secondary.TButton",
        background=[("pressed", T.HOVER), ("active", T.SURFACE_ALT)],
        bordercolor=[("active", T.BORDER_STRONG)],
        foreground=[("disabled", T.TEXT_FAINT)])

    style.configure("Ghost.TButton",
        background=T.SURFACE, foreground=T.TEXT_MUTED, borderwidth=0,
        focuscolor=T.SURFACE, padding=(10, 6), font=(ui, 10))
    style.map("Ghost.TButton",
        background=[("pressed", T.HOVER), ("active", T.SURFACE_ALT)],
        foreground=[("active", T.TEXT), ("disabled", T.TEXT_FAINT)])

    style.configure("DangerGhost.TButton",
        background=T.SURFACE, foreground=T.TEXT_MUTED, borderwidth=0,
        focuscolor=T.SURFACE, padding=(10, 6), font=(ui, 10))
    style.map("DangerGhost.TButton",
        background=[("active", T.DANGER_SOFT)],
        foreground=[("active", T.DANGER), ("disabled", T.TEXT_FAINT)])

    style.configure("TNotebook", background=T.BG, borderwidth=0, tabmargins=(0, 2, 0, 0))
    style.configure("TNotebook.Tab", background=T.BG, foreground=T.TEXT_MUTED,
                    padding=(18, 9), borderwidth=0, font=(ui, 10, "bold"))
    style.map("TNotebook.Tab",
        background=[("selected", T.SURFACE)],
        foreground=[("selected", T.TEXT)])

    style.configure("Treeview",
        background=T.SURFACE, fieldbackground=T.SURFACE, foreground=T.TEXT,
        rowheight=30, borderwidth=0, font=(ui, 10))
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    style.configure("Treeview.Heading",
        background=T.SURFACE_ALT, foreground=T.TEXT_MUTED,
        relief="flat", borderwidth=0, padding=(10, 8), font=(ui, 9, "bold"))
    style.map("Treeview.Heading", background=[("active", T.HOVER)])
    style.map("Treeview",
        background=[("selected", T.ACCENT_SOFT)],
        foreground=[("selected", T.TEXT)])

    style.configure("Vertical.TScrollbar",
        background=T.SURFACE_ALT, troughcolor=T.SURFACE,
        borderwidth=0, arrowcolor=T.TEXT_MUTED)

    return ui, mono


# ---------------------------------------------------------- custom widgets
class CustomProgress(tk.Frame):
    def __init__(self, parent, height=6, fill=None, trough=None, **kw):
        if fill   is None: fill   = T.ACCENT
        if trough is None: trough = T.BORDER
        super().__init__(parent, bg=trough, height=height, **kw)
        self.pack_propagate(False)
        self._fill = tk.Frame(self, bg=fill)
        self._fill.place(x=0, y=0, relwidth=0, relheight=1)

    def set(self, frac, color=None):
        self._fill.place_configure(relwidth=max(0.0, min(1.0, frac)))
        if color is not None:
            self._fill.configure(bg=color)


class Tooltip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text   = text
        self.delay  = delay
        self._job   = None
        self._tip   = None
        widget.bind("<Enter>",       self._on_enter, add="+")
        widget.bind("<Leave>",       self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, _e=None):
        self._cancel()
        self._job = self.widget.after(self.delay, self._show)

    def _on_leave(self, _e=None):
        self._cancel()
        self._hide()

    def _cancel(self):
        if self._job:
            try:
                self.widget.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None

    def _show(self):
        if self._tip is not None:
            return
        try:
            x = self.widget.winfo_rootx() + 8
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except tk.TclError:
            return
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self._tip, text=self.text, bg=T.TEXT, fg="white",
                 padx=8, pady=4, bd=0).pack()

    def _hide(self):
        if self._tip:
            try:
                self._tip.destroy()
            except tk.TclError:
                pass
            self._tip = None


def make_editor(parent, font_family, **kw):
    return tk.Text(
        parent, font=(font_family, 10), wrap="word", undo=True,
        bd=0, relief="flat",
        highlightthickness=1,
        highlightbackground=T.BORDER,
        highlightcolor=T.ACCENT,
        bg=T.SURFACE, fg=T.TEXT,
        insertbackground=T.TEXT,
        selectbackground=T.ACCENT_SOFT, selectforeground=T.TEXT,
        padx=12, pady=10, **kw)


# ------------------------------------------------------------------ app
class NotesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self._scale = enable_hidpi(self)

        self._ui_state = self._load_ui_state()

        # apply any saved theme overrides before building the UI
        saved_theme = self._ui_state.get("theme", {})
        if isinstance(saved_theme, dict):
            for k, v in saved_theme.items():
                if hasattr(T, k) and isinstance(v, str):
                    setattr(T, k, v)

        self._ui_font, self._mono_font = setup_theme(self)
        self.configure(bg=T.BG)

        self.title("Subjects & Tasks")
        self.geometry(f"{int(1000 * self._scale)}x{int(620 * self._scale)}")
        self.minsize(int(700 * self._scale), int(420 * self._scale))

        geom = self._ui_state.get("geometry")
        if isinstance(geom, str):
            try:
                self.geometry(geom)
            except tk.TclError:
                pass

        self._saving_disabled = False
        self._save_job = None
        self._write_error_shown = False
        self._refreshing = False
        self._undo = None
        self.current = None
        self.current_task = None
        self.row_widgets = {}
        self.status_buttons = []
        self.task_action_buttons = []

        self.data = self.load()
        self.build_ui()
        self.refresh_list()
        if self._ui_state.get("current") in self.data:
            self.show_subject(self._ui_state["current"])
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------------------------------------- storage
    def _handle_corrupt(self, error):
        backup = DATA_FILE.with_name(f"{DATA_FILE.name}.corrupt-{int(time.time())}")
        try:
            DATA_FILE.replace(backup)
            moved = backup
        except OSError:
            moved = None
            self._saving_disabled = True
        messagebox.showwarning(
            "Could not read subjects.json",
            f"{error}\n\n"
            + (f"The old file was renamed to:\n{moved}"
               if moved is not None else
               "The old file could not be moved; saving is disabled "
               "for this session so it is not overwritten."),
            parent=self)
        return {}

    def load(self):
        try:
            text = DATA_FILE.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        except (OSError, UnicodeDecodeError) as e:
            return self._handle_corrupt(e)
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as e:
            return self._handle_corrupt(e)
        if not isinstance(raw, dict):
            return self._handle_corrupt(ValueError("Root JSON value is not an object."))

        data = {}
        for name, value in raw.items():
            if isinstance(value, str):
                value = {"notes": value, "tasks": []}
            if not isinstance(value, dict):
                continue
            if not isinstance(value.get("notes"), str):
                value["notes"] = ""
            raw_tasks = value.get("tasks")
            if not isinstance(raw_tasks, list):
                raw_tasks = []
            value["tasks"] = [t for t in raw_tasks if isinstance(t, dict)]
            for t in value["tasks"]:
                if not isinstance(t.get("title"), str):
                    t["title"] = ""
                if not isinstance(t.get("description"), str):
                    t["description"] = ""
                if t.get("status") not in STATUSES:
                    t["status"] = NOT_DONE
            data[name] = value
        return data

    def write_file(self):
        if self._saving_disabled:
            return
        tmp = DATA_FILE.with_name(DATA_FILE.name + ".tmp")
        try:
            tmp.write_text(
                json.dumps(self.data, indent=2, ensure_ascii=False),
                encoding="utf-8")
            tmp.replace(DATA_FILE)
            self._write_error_shown = False
            if getattr(self, "status", None) is not None:
                self.status.config(
                    text=f"\u25CF  Saved at {time.strftime('%H:%M:%S')}",
                    fg=T.SUCCESS)
        except OSError as e:
            if not self._write_error_shown:
                self._write_error_shown = True
                messagebox.showerror(
                    "Could not save",
                    f"Could not write subjects.json:\n{e}\n\n"
                    "Further errors will not be shown this session. "
                    "Check disk space and file permissions.",
                    parent=self)

    def _load_ui_state(self):
        try:
            state = json.loads(UI_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return state if isinstance(state, dict) else {}

    def _save_ui_state(self):
        theme = {k: getattr(T, k) for k in DEFAULT_COLORS}
        try:
            UI_FILE.write_text(
                json.dumps({"geometry": self.geometry(),
                            "current": self.current,
                            "theme":   theme},
                           indent=2),
                encoding="utf-8")
        except OSError:
            pass

    def save_task_desc(self):
        if self.current in self.data and self.current_task is not None:
            tasks = self.data[self.current]["tasks"]
            if 0 <= self.current_task < len(tasks):
                tasks[self.current_task]["description"] = self.desc.get("1.0", "end-1c")

    def save_current(self):
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
        self.status.config(text="\u25CF  Unsaved changes", fg=T.WARNING)
        self._save_job = self.after(1000, self._do_save)

    def _do_save(self):
        self._save_job = None
        self.save_current()

    # --------------------------------------------------------------- UI
    def build_ui(self):
        self.status = tk.Label(self, text="", anchor="e",
                               bg=T.BG, fg=T.TEXT_FAINT,
                               font=(self._ui_font, 9), padx=12, pady=4)
        self.status.pack(side="bottom", fill="x")

        # ---- left sidebar ----
        left = tk.Frame(self, bg=T.BG, padx=12, pady=12)
        left.pack(side="left", fill="y")
        tk.Label(left, text="Subjects", anchor="w",
                 bg=T.BG, fg=T.TEXT,
                 font=(self._ui_font, 11, "bold")).pack(fill="x", pady=(0, 8))

        lf = tk.Frame(left, bg=T.BG)
        lf.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(lf, width=280, bg=T.BG,
                                highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.rows = tk.Frame(self.canvas, bg=T.BG)
        self._rows_id = self.canvas.create_window((0, 0), window=self.rows, anchor="nw")
        self.rows.bind("<Configure>", self._on_rows_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        self.rows.bind("<MouseWheel>", self._on_mousewheel)
        self.rows.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.rows.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        b = tk.Frame(left, bg=T.BG)
        b.pack(fill="x", pady=(8, 0))
        ttk.Button(b, text="+  Add", style="Accent.TButton",
                   command=self.add_subject).pack(side="left", padx=(0, 6))
        ttk.Button(b, text="Rename", style="Secondary.TButton",
                   command=self.rename_subject).pack(side="left", padx=(0, 6))
        ttk.Button(b, text="Delete", style="DangerGhost.TButton",
                   command=self.delete_subject).pack(side="left")

        # ---- right pane ----
        right = tk.Frame(self, bg=T.BG, padx=12, pady=12)
        right.pack(side="right", fill="both", expand=True)

        if self._saving_disabled:
            tk.Label(right,
                text="\u26a0  Saving is disabled \u2014 subjects.json could "
                     "not be read or moved aside. Fix or remove the file, "
                     "then restart the app.",
                bg=T.DANGER_SOFT, fg=T.DANGER, pady=8, padx=12,
                font=(self._ui_font, 10, "bold"),
                anchor="w", justify="left",
            ).pack(fill="x", pady=(0, 8))

        header = tk.Frame(right, bg=T.BG)
        header.pack(fill="x", pady=(0, 8))
        self.title_label = tk.Label(header, text="Select or add a subject",
                                    anchor="w", bg=T.BG, fg=T.TEXT,
                                    font=(self._ui_font, 16, "bold"))
        self.title_label.pack(side="left")
        self.subtitle_label = tk.Label(header, text="", anchor="e",
                                       bg=T.BG, fg=T.TEXT_MUTED,
                                       font=(self._ui_font, 10))
        self.subtitle_label.pack(side="right")

        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True)

        # ---- tasks tab ----
        tasks_tab = tk.Frame(self.tabs, bg=T.SURFACE, padx=14, pady=14)
        self.tabs.add(tasks_tab, text="Tasks")

        top = tk.Frame(tasks_tab, bg=T.SURFACE)
        top.pack(fill="x")

        ttk.Button(top, text="+  Add task", style="Accent.TButton",
                   command=self.add_task).pack(side="left")

        b = ttk.Button(top, text="Rename", style="Secondary.TButton",
                       command=self.rename_task)
        b.pack(side="left", padx=(6, 0))
        self.task_action_buttons.append(b)

        b = ttk.Button(top, text="Delete", style="DangerGhost.TButton",
                       command=self.delete_task)
        b.pack(side="left", padx=(4, 0))
        self.task_action_buttons.append(b)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)

        for text, delta in (("\u2191", -1), ("\u2193", 1)):
            b = ttk.Button(top, text=text, width=3, style="Ghost.TButton",
                           command=lambda d=delta: self.move_task(d))
            b.pack(side="left", padx=(0, 2))
            self.task_action_buttons.append(b)

        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)

        tk.Label(top, text="Mark as:", bg=T.SURFACE, fg=T.TEXT_MUTED,
                 font=(self._ui_font, 10)).pack(side="left", padx=(0, 6))
        for status in STATUSES:
            b = ttk.Button(top, text=ICONS[status], style="Secondary.TButton",
                           command=lambda s=status: self.set_status(s))
            b.pack(side="left", padx=2)
            self.status_buttons.append(b)

        self.progress = tk.Label(top, text="", anchor="e",
                                 bg=T.SURFACE, fg=T.TEXT_MUTED,
                                 font=(self._ui_font, 9))
        self.progress.pack(side="right")

        ff = tk.Frame(tasks_tab, bg=T.SURFACE)
        ff.pack(fill="x", pady=(12, 0))
        tk.Label(ff, text="Search", bg=T.SURFACE, fg=T.TEXT_MUTED,
                 font=(self._ui_font, 10)).pack(side="left", padx=(0, 8))
        self.filter_var = tk.StringVar()
        fe = tk.Entry(ff, textvariable=self.filter_var, relief="flat", bd=0,
                      bg=T.SURFACE, fg=T.TEXT, insertbackground=T.TEXT,
                      highlightthickness=1,
                      highlightbackground=T.BORDER, highlightcolor=T.ACCENT,
                      font=(self._ui_font, 10))
        fe.pack(side="left", fill="x", expand=True, ipady=4)
        self.filter_var.trace_add("write", self._on_filter_change)

        tf = tk.Frame(tasks_tab, bg=T.SURFACE)
        tf.pack(fill="both", expand=True, pady=(12, 0))
        self.tree = ttk.Treeview(tf, columns=("status", "title"),
                                 show="headings", height=8, selectmode="browse")
        self.tree.heading("status", text="Status", anchor="w")
        self.tree.heading("title",  text="Task",   anchor="w")
        self.tree.column("status", width=150, stretch=False, anchor="w")
        self.tree.column("title",  width=420, anchor="w")
        self.tree.tag_configure("stripe_odd",  background=T.SURFACE)
        self.tree.tag_configure("stripe_even", background=T.SURFACE_ALT)
        self.tree.tag_configure(DONE,        foreground=T.SUCCESS)
        self.tree.tag_configure(IN_PROGRESS, foreground=T.WARNING)
        self.tree.tag_configure(NOT_DONE,    foreground=T.TEXT)
        tsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.config(yscrollcommand=tsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.tree.bind("<Double-1>", self._on_task_double_click)
        self.tree.bind("<Return>",       lambda e: self.cycle_status())
        self.tree.bind("<Delete>",       lambda e: self.delete_task())
        self.tree.bind("<Control-Up>",   self._move_up)
        self.tree.bind("<Control-Down>", self._move_down)

        self.desc_label = tk.Label(tasks_tab, text="Description", anchor="w",
                                   bg=T.SURFACE, fg=T.TEXT,
                                   font=(self._ui_font, 10, "bold"))
        self.desc_label.pack(fill="x", pady=(12, 6))
        df = tk.Frame(tasks_tab, bg=T.SURFACE)
        df.pack(fill="both", expand=True)
        self.desc = make_editor(df, self._ui_font, height=8, state="disabled")
        dsb = ttk.Scrollbar(df, orient="vertical", command=self.desc.yview)
        self.desc.config(yscrollcommand=dsb.set)
        self.desc.pack(side="left", fill="both", expand=True)
        dsb.pack(side="right", fill="y")
        self.desc.bind("<KeyRelease>", self.schedule_save)

        # ---- notes tab ----
        notes_tab = tk.Frame(self.tabs, bg=T.SURFACE, padx=14, pady=14)
        self.tabs.add(notes_tab, text="Notes")
        nf = tk.Frame(notes_tab, bg=T.SURFACE)
        nf.pack(fill="both", expand=True)
        self.notes = make_editor(nf, self._ui_font, state="disabled")
        nsb = ttk.Scrollbar(nf, orient="vertical", command=self.notes.yview)
        self.notes.config(yscrollcommand=nsb.set)
        self.notes.pack(side="left", fill="both", expand=True)
        nsb.pack(side="right", fill="y")
        self.notes.bind("<KeyRelease>", self.schedule_save)

        # ---- settings tab ----
        self._build_settings_tab()

        self.bind("<Control-n>", lambda e: self.add_subject())
        self.bind("<Control-t>", lambda e: self.add_task())
        self.bind_all("<Control-z>", self._on_ctrl_z)

        Tooltip(self.status_buttons[0], "Mark as Not done")
        Tooltip(self.status_buttons[1], "Mark as In progress")
        Tooltip(self.status_buttons[2], "Mark as Done")

        self._sync_task_buttons()

    # ------------------------------------------------------------ settings
    def _build_settings_tab(self):
        tab = tk.Frame(self.tabs, bg=T.SURFACE, padx=14, pady=14)
        self.tabs.add(tab, text="\u2699  Settings")

        head = tk.Frame(tab, bg=T.SURFACE)
        head.pack(fill="x", pady=(0, 4))
        tk.Label(head, text="Appearance", anchor="w",
                 bg=T.SURFACE, fg=T.TEXT,
                 font=(self._ui_font, 14, "bold")).pack(side="left")
        ttk.Button(head, text="Reset to defaults", style="Secondary.TButton",
                   command=self._reset_theme).pack(side="right")

        tk.Label(tab, text="Click any swatch to change a colour. "
                          "Changes apply instantly and are saved automatically.",
                 anchor="w", bg=T.SURFACE, fg=T.TEXT_MUTED,
                 font=(self._ui_font, 10),
                 justify="left").pack(fill="x", pady=(0, 12))

        # scrollable inner area
        wrap = tk.Frame(tab, bg=T.SURFACE)
        wrap.pack(fill="both", expand=True)
        canvas = tk.Canvas(wrap, bg=T.SURFACE, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        canvas.config(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        inner = tk.Frame(canvas, bg=T.SURFACE)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(win_id, width=e.width))

        for group_title, tokens in COLOR_GROUPS:
            group = tk.Frame(inner, bg=T.SURFACE)
            group.pack(fill="x", pady=(4, 10))
            tk.Label(group, text=group_title, anchor="w",
                     bg=T.SURFACE, fg=T.TEXT,
                     font=(self._ui_font, 11, "bold")).pack(fill="x", pady=(0, 4))
            for token in tokens:
                self._make_color_row(group, token)

        # wheel support on every settings widget
        def _bind_wheel(widget):
            widget.bind("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            -1 if e.delta > 0 else 1, "units"), add="+")
            widget.bind("<Button-4>",
                        lambda e: canvas.yview_scroll(-1, "units"), add="+")
            widget.bind("<Button-5>",
                        lambda e: canvas.yview_scroll(1, "units"), add="+")
            for c in widget.winfo_children():
                _bind_wheel(c)
        _bind_wheel(inner)

    def _make_color_row(self, parent, token):
        row = tk.Frame(parent, bg=T.SURFACE)
        row.pack(fill="x", pady=1)

        tk.Label(row, text=COLOR_LABELS.get(token, token), anchor="w",
                 width=18, bg=T.SURFACE, fg=T.TEXT,
                 font=(self._ui_font, 10)).pack(side="left")

        swatch = tk.Label(row, bg=getattr(T, token), width=4, height=1,
                          bd=0, relief="flat", cursor="hand2",
                          highlightthickness=1,
                          highlightbackground=T.BORDER_STRONG)
        swatch.pack(side="left", padx=(6, 8), ipady=5)
        swatch.bind("<Button-1>", lambda e, t=token: self._pick_color(t))

        tk.Label(row, text=getattr(T, token), anchor="w",
                 bg=T.SURFACE, fg=T.TEXT_MUTED,
                 font=(self._mono_font, 9)).pack(side="left")

    def _pick_color(self, token):
        current = getattr(T, token)
        result = colorchooser.askcolor(
            color=current, parent=self,
            title=f"Choose colour \u2014 {COLOR_LABELS.get(token, token)}")
        if not result or not result[1]:
            return
        setattr(T, token, result[1])
        self._save_ui_state()
        self._rebuild_ui()

    def _reset_theme(self):
        if not messagebox.askyesno(
                "Reset theme",
                "Reset all colours to their default values?", parent=self):
            return
        for k, v in DEFAULT_COLORS.items():
            setattr(T, k, v)
        self._save_ui_state()
        self._rebuild_ui()

    def _rebuild_ui(self):
        """Tear down and rebuild the entire UI with the current theme."""
        # preserve state
        self.save_current()          # flush any pending notes/desc edits
        cur      = self.current
        cur_task = self.current_task
        try:
            filt = self.filter_var.get()
        except (AttributeError, tk.TclError):
            filt = ""

        # tear down
        for child in self.winfo_children():
            child.destroy()
        self.row_widgets = {}
        self.status_buttons = []
        self.task_action_buttons = []

        # reapply theme
        self._ui_font, self._mono_font = setup_theme(self)
        self.configure(bg=T.BG)

        # rebuild
        self.build_ui()
        self.refresh_list()
        if cur in self.data:
            self.show_subject(cur)
            if filt:
                self.filter_var.set(filt)
            tasks = self.data[cur]["tasks"]
            if (cur_task is not None and 0 <= cur_task < len(tasks)
                    and str(cur_task) in self.tree.get_children()):
                self.refresh_tasks(select=cur_task)

        # stay on the Settings tab so the user sees live changes
        try:
            self.tabs.select(2)
        except tk.TclError:
            pass

    # -------------------------------------------------------------- rest
    def _on_filter_change(self, *_args):
        if self._refreshing:
            return
        self.refresh_tasks(select=self.current_task)

    def _update_header_stats(self):
        if not self.current or self.current not in self.data:
            self.subtitle_label.config(text="")
            return
        tasks = self.data[self.current]["tasks"]
        if not tasks:
            self.subtitle_label.config(text="No tasks yet")
        else:
            done = sum(t["status"] == DONE for t in tasks)
            self.subtitle_label.config(text=f"{done} of {len(tasks)} complete")

    def _on_rows_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self._rows_id, width=event.width)

    def _on_mousewheel(self, event):
        if event.delta == 0:
            return
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _bar_color(self, frac):
        return T.SUCCESS if frac >= 1.0 else T.ACCENT

    def _pointer_inside(self, widget):
        try:
            x, y = widget.winfo_pointerxy()
            rx = widget.winfo_rootx(); ry = widget.winfo_rooty()
            rw = widget.winfo_width(); rh = widget.winfo_height()
            return rx <= x < rx + rw and ry <= y < ry + rh
        except tk.TclError:
            return False

    def _make_subject_row(self, name):
        tasks = self.data[name]["tasks"]
        total = len(tasks)
        done  = sum(t["status"] == DONE for t in tasks)
        frac  = (done / total) if total else 0.0

        row = tk.Frame(self.rows, bg=T.SURFACE, bd=0,
                       highlightthickness=1, highlightbackground=T.BORDER)
        row.pack(fill="x", padx=2, pady=3)

        stripe = tk.Frame(row, bg=T.SURFACE, width=3)
        stripe.pack(side="left", fill="y")

        body = tk.Frame(row, bg=T.SURFACE, padx=10, pady=8)
        body.pack(side="left", fill="both", expand=True)

        top = tk.Frame(body, bg=T.SURFACE)
        top.pack(fill="x")

        label = tk.Label(top, text=name, anchor="w", bg=T.SURFACE,
                         fg=T.TEXT, font=(self._ui_font, 10, "bold"))
        label.pack(side="left", fill="x", expand=True)

        count = tk.Label(top, text=(f"{done}/{total}" if total else "\u2013"),
                         anchor="e", bg=T.SURFACE, fg=T.TEXT_MUTED,
                         font=(self._ui_font, 9))
        count.pack(side="right")

        bar = CustomProgress(body, height=5, fill=self._bar_color(frac))
        bar.pack(fill="x", pady=(6, 0))
        bar.set(frac, color=self._bar_color(frac))

        parts = (row, stripe, body, top, label, count, bar)

        def paint(bg, stripe_color, border_color=None):
            try:
                row.configure(bg=bg, highlightbackground=border_color or T.BORDER)
                stripe.configure(bg=stripe_color)
                for w in (body, top, label, count):
                    w.configure(bg=bg)
            except tk.TclError:
                pass

        def on_enter(_e=None):
            if name != self.current:
                paint(T.HOVER, T.BORDER_STRONG, T.BORDER_STRONG)

        def on_leave(_e=None):
            if name == self.current:
                return
            self.after_idle(check_leave)

        def check_leave():
            if name == self.current:
                return
            if not self._pointer_inside(row):
                paint(T.SURFACE, T.SURFACE, T.BORDER)

        for w in parts:
            w.bind("<Button-1>", lambda _e, n=name: self.select_subject(n))
            w.bind("<Enter>", on_enter, add="+")
            w.bind("<Leave>", on_leave, add="+")
            w.bind("<MouseWheel>", self._on_mousewheel)
            w.bind("<Button-4>", lambda _e: self.canvas.yview_scroll(-1, "units"))
            w.bind("<Button-5>", lambda _e: self.canvas.yview_scroll(1, "units"))

        self.row_widgets[name] = {
            "row": row, "stripe": stripe, "body": body, "top": top,
            "label": label, "count": count, "bar": bar, "paint": paint,
        }

    def _paint_selection(self):
        for name, w in self.row_widgets.items():
            if name == self.current:
                w["paint"](T.ACCENT_SOFT, T.ACCENT, T.ACCENT)
            else:
                w["paint"](T.SURFACE, T.SURFACE, T.BORDER)

    def update_progress_bars(self, name=None):
        names = [name] if name is not None else list(self.row_widgets)
        for n in names:
            if n not in self.row_widgets:
                continue
            w = self.row_widgets[n]
            tasks = self.data.get(n, {}).get("tasks", [])
            total = len(tasks)
            done  = sum(t["status"] == DONE for t in tasks)
            frac  = (done / total) if total else 0.0
            w["bar"].set(frac, color=self._bar_color(frac))
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
                     bg=T.BG, fg=T.TEXT_FAINT, justify="center",
                     pady=20, font=(self._ui_font, 10)).pack(fill="x")
        for name in self.data:
            self._make_subject_row(name)
        self.rows.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(y)
        self._paint_selection()

    # ---------------------------------------------------------- subjects
    def show_subject(self, name):
        self.current = name
        self.title_label.config(text=name)
        self.notes.config(state="normal")
        self.notes.delete("1.0", "end")
        self.notes.insert("1.0", self.data[name]["notes"])
        self.notes.edit_reset()
        self.current_task = None
        if self.filter_var.get():
            self.filter_var.set("")
        self.refresh_tasks()
        self._paint_selection()
        self._update_header_stats()

    def clear_editor(self):
        self.current = None
        self.current_task = None
        self.title_label.config(text="Select or add a subject")
        self.subtitle_label.config(text="")
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
            messagebox.showwarning("Exists", f'"{name}" already exists.', parent=self)
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
            messagebox.showwarning("Exists", f'"{new}" already exists.', parent=self)
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
            "Delete subject",
            f'Delete "{self.current}" and all its tasks and notes?', parent=self):
            return
        self._undo = ("subject", self.current, copy.deepcopy(self.data[self.current]))
        del self.data[self.current]
        self.write_file()
        self.clear_editor()
        self.refresh_list()

    # ------------------------------------------------------------- tasks
    def tasks(self):
        return self.data[self.current]["tasks"] if self.current else []

    def _sync_task_buttons(self):
        state = "normal" if self.current_task is not None else "disabled"
        for b in self.status_buttons + self.task_action_buttons:
            b.configure(state=state)

    def _visible_indices(self):
        tasks = self.tasks()
        q = self.filter_var.get().strip().lower()
        if not q:
            return list(range(len(tasks)))
        return [i for i, t in enumerate(tasks)
                if q in t["title"].lower() or q in t["description"].lower()]

    def refresh_tasks(self, select=None):
        self._refreshing = True
        try:
            self.tree.delete(*self.tree.get_children())
            tasks = self.tasks()
            visible = self._visible_indices()
            for i in visible:
                t = tasks[i]
                stripe = "stripe_even" if (i % 2) else "stripe_odd"
                self.tree.insert(
                    "", "end", iid=str(i),
                    values=(ICONS[t["status"]], t["title"]),
                    tags=(t["status"], stripe))
            done = sum(t["status"] == DONE for t in tasks)
            self.progress.config(text=f"{done}/{len(tasks)} done" if tasks else "")
            if select is not None and select in visible:
                self.tree.selection_set(str(select))
                self.tree.see(str(select))
                self.show_task(select)
            else:
                self.current_task = None
                self.clear_task_editor()
        finally:
            self._refreshing = False
        self.update_progress_bars(self.current)
        self._update_header_stats()

    def show_task(self, idx):
        self.current_task = idx
        t = self.tasks()[idx]
        title = t["title"].replace("\n", " ").replace("\r", " ")
        if len(title) > 50:
            title = title[:47] + "\u2026"
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
            messagebox.showinfo("No subject", "Add or select a subject first.", parent=self)
            return
        title = simpledialog.askstring("Add task", "Task title:", parent=self)
        if not title or not title.strip():
            return
        self.save_task_desc()
        self.tasks().append({"title": title.strip(), "status": NOT_DONE, "description": ""})
        self.write_file()
        if self.filter_var.get():
            self.filter_var.set("")
        self.refresh_tasks(select=len(self.tasks()) - 1)
        self.desc.focus_set()

    def rename_task(self):
        if self.current_task is None:
            return
        t = self.tasks()[self.current_task]
        new = simpledialog.askstring("Rename task", "New title:",
                                     initialvalue=t["title"], parent=self)
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
        if not messagebox.askyesno("Delete task",
                                   f'Delete task "{t["title"]}"?', parent=self):
            return
        self._undo = ("task", self.current, idx, copy.deepcopy(t))
        del self.tasks()[idx]
        self.current_task = None
        self.write_file()
        n = len(self.tasks())
        self.refresh_tasks(select=min(idx, n - 1) if n else None)

    def move_task(self, delta):
        if self.current_task is None:
            return
        tasks = self.tasks()
        j = self.current_task + delta
        if not (0 <= j < len(tasks)):
            return
        self.save_task_desc()
        i = self.current_task
        tasks[i], tasks[j] = tasks[j], tasks[i]
        self.write_file()
        self.refresh_tasks(select=j)

    def _move_up(self, _event=None):
        self.move_task(-1)
        return "break"

    def _move_down(self, _event=None):
        self.move_task(1)
        return "break"

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

    def _on_task_double_click(self, event):
        if not self.tree.identify_row(event.y):
            return
        self.cycle_status()

    # -------------------------------------------------------------- undo
    def _on_ctrl_z(self, _event=None):
        focus = self.focus_get()
        if isinstance(focus, (tk.Text, tk.Entry, ttk.Entry)):
            return
        if self.undo_delete():
            return "break"

    def undo_delete(self):
        undo = self._undo
        self._undo = None
        if not undo:
            return False
        if undo[0] == "task":
            _, subject, idx, task = undo
            if subject in self.data:
                tasks = self.data[subject]["tasks"]
                tasks.insert(min(idx, len(tasks)), task)
                self.write_file()
                if subject == self.current:
                    self.refresh_tasks(select=idx)
                else:
                    self.show_subject(subject)
                    self.refresh_tasks(select=idx)
                self.update_progress_bars(subject)
                self.status.config(text=f'\u21A9  Restored task "{task["title"]}"',
                                   fg=T.SUCCESS)
        else:
            _, name, payload = undo
            self.data[name] = payload
            self.write_file()
            self.refresh_list()
            self.show_subject(name)
            self.status.config(text=f'\u21A9  Restored subject "{name}"',
                               fg=T.SUCCESS)
        return True

    def on_close(self):
        self.save_current()
        self._save_ui_state()
        self.destroy()


if __name__ == "__main__":
    NotesApp().mainloop()