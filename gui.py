import argparse
import queue
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from item_map import ITEM_TO_CATEGORY_MAP_FILE
from sm import run_pipeline


class CsvPipelineApp(tk.Tk):
    """Desktop interface for the CSV processing pipeline."""

    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        self.title("Statement Studio")
        self.geometry("760x700")
        self.minsize(680, 620)
        self.configure(background="#f3f0e8")

        self.statement_directory = tk.StringVar()
        self.output_directory = tk.StringVar()
        self.mapping_file = tk.StringVar(value=str(ITEM_TO_CATEGORY_MAP_FILE))
        self.partner_filter_file = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready to process statements")
        self.result_path = None
        self.messages = queue.Queue()

        self._configure_style()
        self._build_ui()
        self.after(100, self._drain_messages)

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f3f0e8")
        style.configure("Panel.TFrame", background="#fffdf8")
        style.configure("Title.TLabel", background="#f3f0e8", foreground="#183b3b", font=("Georgia", 26, "bold"))
        style.configure("Subtitle.TLabel", background="#f3f0e8", foreground="#5d6b66", font=("TkDefaultFont", 11))
        style.configure("Section.TLabel", background="#fffdf8", foreground="#183b3b", font=("TkDefaultFont", 12, "bold"))
        style.configure("Field.TLabel", background="#fffdf8", foreground="#42504c", font=("TkDefaultFont", 10, "bold"))
        style.configure("Status.TLabel", background="#e6eee8", foreground="#24554c", padding=(12, 9))
        style.configure("Accent.TButton", background="#d46a45", foreground="white", padding=(18, 9), font=("TkDefaultFont", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#b95132"), ("disabled", "#c7b7ad")])
        style.configure("Secondary.TButton", padding=(10, 7))
        style.configure("TEntry", padding=7)
        style.configure("TProgressbar", troughcolor="#e5e0d5", background="#d46a45")

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame", padding=(34, 28, 34, 24))
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        ttk.Label(root, text="Statement Studio", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            root,
            text="Turn bank statement CSVs into a categorized report.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 22))

        panel = ttk.Frame(root, style="Panel.TFrame", padding=24)
        panel.grid(row=2, column=0, sticky="nsew")
        panel.columnconfigure(1, weight=1)

        ttk.Label(panel, text="PROCESSING SETUP", style="Section.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 20)
        )
        self._add_path_row(panel, 1, "Statement folder", self.statement_directory, self._choose_statement_directory, "Choose folder")
        self._add_path_row(panel, 2, "Output folder", self.output_directory, self._choose_output_directory, "Choose folder")
        self._add_path_row(panel, 3, "Mapping file", self.mapping_file, self._choose_mapping_file, "Choose file")
        self._add_path_row(panel, 4, "Partner filter JSON", self.partner_filter_file, self._choose_partner_filter_file, "Choose file")

        ttk.Separator(panel).grid(row=5, column=0, columnspan=3, sticky="ew", pady=22)
        ttk.Label(panel, text="ACTIVITY", style="Section.TLabel").grid(row=6, column=0, columnspan=3, sticky="w")

        self.progress = ttk.Progressbar(panel, mode="indeterminate")
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(14, 10))
        panel.rowconfigure(8, weight=1)
        self.log = tk.Text(
            panel,
            height=8,
            background="#f7f4ec",
            foreground="#42504c",
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=10,
            wrap="word",
            state="disabled",
        )
        self.log.grid(row=8, column=0, columnspan=3, sticky="nsew")

        ttk.Label(root, textvariable=self.status_text, style="Status.TLabel").grid(
            row=3, column=0, sticky="ew", pady=(16, 12)
        )
        actions = ttk.Frame(root, style="App.TFrame")
        actions.grid(row=4, column=0, sticky="e")
        self.open_button = ttk.Button(actions, text="Open report", style="Secondary.TButton", command=self._open_report, state="disabled")
        self.open_button.pack(side="left", padx=(0, 10))
        self.run_button = ttk.Button(actions, text="Run pipeline", style="Accent.TButton", command=self._start_pipeline)
        self.run_button.pack(side="left")

    def _add_path_row(self, parent, row, label, variable, command, button_text):
        ttk.Label(parent, text=label, style="Field.TLabel").grid(row=row, column=0, sticky="w", pady=7, padx=(0, 18))
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=7)
        ttk.Button(parent, text=button_text, style="Secondary.TButton", command=command).grid(row=row, column=2, padx=(10, 0), pady=7)

    def _choose_statement_directory(self):
        selected = filedialog.askdirectory(title="Select statement folder")
        if selected:
            self.statement_directory.set(selected)

    def _choose_output_directory(self):
        selected = filedialog.askdirectory(title="Select output folder")
        if selected:
            self.output_directory.set(selected)

    def _choose_mapping_file(self):
        selected = filedialog.askopenfilename(
            title="Select mapping file",
            filetypes=[("JSON files", "*.json"), ("All files", "*")],
        )
        if selected:
            self.mapping_file.set(selected)

    def _choose_partner_filter_file(self):
        selected = filedialog.askopenfilename(
            title="Select Partner Name filter JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*")],
        )
        if selected:
            self.partner_filter_file.set(selected)

    def _start_pipeline(self):
        statement_directory = Path(self.statement_directory.get().strip())
        output_directory = Path(self.output_directory.get().strip())
        mapping_file = Path(self.mapping_file.get().strip())
        partner_filter_value = self.partner_filter_file.get().strip()
        partner_filter_file = Path(partner_filter_value) if partner_filter_value else None

        if not statement_directory.is_dir():
            messagebox.showerror("Missing statement folder", "Choose a folder containing statement CSV files.")
            return
        if not mapping_file.is_file():
            messagebox.showerror("Missing mapping file", "Choose a valid JSON mapping file.")
            return
        if partner_filter_file is not None and not partner_filter_file.is_file():
            messagebox.showerror("Missing partner filter file", "Choose a valid JSON filter file or leave it blank.")
            return

        self.run_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.progress.configure(mode="indeterminate", value=0)
        self.progress.start(12)
        self.status_text.set("Processing statements...")
        self._write_log("Starting pipeline")
        thread = threading.Thread(
            target=self._run_pipeline,
            args=(statement_directory, output_directory, mapping_file, partner_filter_file, self.debug),
            daemon=True,
        )
        thread.start()

    def _run_pipeline(self, statement_directory, output_directory, mapping_file, partner_filter_file=None, debug=False):
        try:
            result = run_pipeline(
                statement_directory,
                output_directory,
                mapping_file=mapping_file,
                partner_filter_file=partner_filter_file,
                progress_callback=lambda message: self.messages.put(("progress", message)),
                debug=debug,
            )
            self.messages.put(("success", Path(result)))
        except Exception as error:
            self.messages.put(("error", str(error)))

    def _drain_messages(self):
        try:
            while True:
                message_type, value = self.messages.get_nowait()
                if message_type == "progress":
                    self.status_text.set(value)
                    self._write_log(value)
                elif message_type == "success":
                    self.progress.stop()
                    self.progress.configure(mode="determinate", value=100)
                    self.result_path = value
                    self.status_text.set("Report ready")
                    self._write_log(f"Report created: {value}")
                    self.run_button.configure(state="normal")
                    self.open_button.configure(state="normal")
                elif message_type == "error":
                    self.progress.stop()
                    self.status_text.set("Processing failed")
                    self._write_log(f"Error: {value}")
                    self.run_button.configure(state="normal")
                    messagebox.showerror("Pipeline error", value)
        except queue.Empty:
            pass
        self.after(100, self._drain_messages)

    def _write_log(self, message):
        self.log.configure(state="normal")
        self.log.insert("end", f"{message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _open_report(self):
        if self.result_path and self.result_path.exists():
            webbrowser.open(self.result_path.resolve().as_uri())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Keep intermediate stage CSV files in the output directory",
    )
    args = parser.parse_args()
    app = CsvPipelineApp(debug=args.debug)
    app.mainloop()


if __name__ == "__main__":
    main()
