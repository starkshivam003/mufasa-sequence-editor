import tkinter as tk
from tkinter import filedialog, colorchooser
import webbrowser
import os

class SequenceNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Sequence Highlighter")

        # Text area
        self.text = tk.Text(root, wrap="word", undo=True)
        self.text.pack(expand=1, fill="both")

        # Menu
        menu = tk.Menu(root)
        root.config(menu=menu)

        # File menu
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save as HTML", command=self.save_html)
        file_menu.add_command(label="Exit", command=root.quit)

        # Highlight menu
        highlight_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Highlight", menu=highlight_menu)
        highlight_menu.add_command(label="Highlight Selection", command=self.highlight_text)
        highlight_menu.add_command(label="Remove Highlight (Selection)", command=self.remove_selected_highlight)

        self.tag_count = 0

        # Ctrl+F binding
        self.root.bind("<Control-f>", self.open_find_window)

        self.last_pos = "1.0"

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, content)
            self.last_pos = "1.0"

    # ---------- SAVE HTML ----------
    def save_html(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".html")
        if not file_path:
            return

        html = "<html><body><pre style='font-family:monospace;'>"

        for i in range(1, int(self.text.index('end-1c').split('.')[0]) + 1):
            line_start = f"{i}.0"
            line_end = f"{i}.end"
            line = self.text.get(line_start, line_end)

            for tag in self.text.tag_names():
                if not tag.startswith("highlight"):
                    continue

                ranges = self.text.tag_ranges(tag)
                for j in range(0, len(ranges), 2):
                    start = ranges[j]
                    end = ranges[j+1]

                    if self.text.compare(start, "<=", line_end) and self.text.compare(end, ">", line_start):
                        color = self.text.tag_cget(tag, "background")
                        segment = self.text.get(start, end)

                        if segment.strip():
                            line = line.replace(
                                segment,
                                f"<span style='background:{color}'>{segment}</span>"
                            )

            html += line + "\n"

        html += "</pre></body></html>"

        with open(file_path, "w") as f:
            f.write(html)

        webbrowser.open(f"file://{os.path.abspath(file_path)}")

    # ---------- MANUAL HIGHLIGHT ----------
    def highlight_text(self):
        try:
            start = self.text.index("sel.first")
            end = self.text.index("sel.last")
        except tk.TclError:
            return

        color = colorchooser.askcolor()[1]
        if not color:
            return

        tag_name = f"highlight{self.tag_count}"
        self.tag_count += 1

        self.text.tag_add(tag_name, start, end)
        self.text.tag_config(tag_name, background=color)

    # ---------- REMOVE SELECTED ----------
    def remove_selected_highlight(self):
        try:
            start = self.text.index("sel.first")
            end = self.text.index("sel.last")
        except tk.TclError:
            return

        for tag in self.text.tag_names():
            if tag.startswith("highlight"):
                self.text.tag_remove(tag, start, end)

    # ---------- FIND WINDOW ----------
    def open_find_window(self, event=None):
        self.find_window = tk.Toplevel(self.root)
        self.find_window.title("Find")

        tk.Label(self.find_window, text="Find:").pack(side="left")

        self.find_entry = tk.Entry(self.find_window)
        self.find_entry.pack(side="left", fill="both", expand=1)
        self.find_entry.focus()

        tk.Button(self.find_window, text="Find Next", command=self.find_next).pack(side="left")

        # Remove search highlight when closing
        self.find_window.protocol("WM_DELETE_WINDOW", self.close_find_window)

    def close_find_window(self):
        self.text.tag_remove("search", "1.0", tk.END)
        self.find_window.destroy()

    # ---------- FIND (TEMPORARY HIGHLIGHT) ----------
    def find_next(self):
        search_term = self.find_entry.get()
        if not search_term:
            return

        # Remove previous search highlight
        self.text.tag_remove("search", "1.0", tk.END)

        pos = self.text.search(search_term, self.last_pos, stopindex=tk.END)

        if not pos:
            self.last_pos = "1.0"
            return

        end = f"{pos}+{len(search_term)}c"

        # Temporary search highlight
        self.text.tag_add("search", pos, end)
        self.text.tag_config("search", background="#ffff99")

        # Ensure manual highlights stay above
        for tag in self.text.tag_names():
            if tag.startswith("highlight"):
                self.text.tag_raise(tag)

        # Select it
        self.text.tag_remove("sel", "1.0", tk.END)
        self.text.tag_add("sel", pos, end)
        self.text.mark_set(tk.INSERT, end)
        self.text.see(pos)

        self.last_pos = end


if __name__ == "__main__":
    root = tk.Tk()
    app = SequenceNotepad(root)
    root.mainloop()