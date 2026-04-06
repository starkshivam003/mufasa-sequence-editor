import tkinter as tk
from tkinter import messagebox, filedialog
import re
import random
import webbrowser
import os

# Try to import docx
try:
    from docx import Document
    from docx.shared import RGBColor, Pt, Inches
    from docx.enum.section import WD_ORIENT
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

class MufasaMapper:
    def __init__(self, root):
        self.root = root
        self.root.title("MUFASA - Peptide Automation Engine")
        self.root.geometry("1000x600")

        # --- UI LAYOUT ---
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(expand=True, fill="both")

        # Left Panel (Parent Sequence)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))
        tk.Label(left_frame, text="1. Paste Parent Sequence (or drag .fasta text):", font=("Arial", 10, "bold")).pack(anchor="w")
        self.seq_text = tk.Text(left_frame, wrap="word", font=("Courier New", 10))
        self.seq_text.pack(expand=True, fill="both")

        # Right Panel (Peptides)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", expand=True, fill="both", padx=(5, 0))
        tk.Label(right_frame, text="2. Paste Peptide Column (from Excel):", font=("Arial", 10, "bold")).pack(anchor="w")
        self.pep_text = tk.Text(right_frame, wrap="none", font=("Courier New", 10))
        self.pep_text.pack(expand=True, fill="both")

        # Bottom Button
        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack(fill="x")
        generate_btn = tk.Button(btn_frame, text="GENERATE PREVIEW", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.generate_preview)
        generate_btn.pack(pady=10, ipadx=20, ipady=5)

        # Pre-defined high-contrast colors for readability
        self.palette = ["#E6194B", "#3CB44B", "#FFE119", "#4363D8", "#F58231", 
                        "#911EB4", "#46F0F0", "#F032E6", "#BCF60C", "#FABEBE"]

    # ---------- PHASE 1: SANITIZATION LAYER ----------
    def clean_peptide(self, raw_pep):
        """Strips PTM brackets and cleavage dots (e.g., K.A[+80]SDF.R -> ASDF)"""
        pep = raw_pep.strip()
        if not pep: return ""
        
        # If it has dots (MaxQuant/PEAKS style), extract the middle part
        match = re.search(r"\.(.*?)\.", pep)
        if match:
            pep = match.group(1)
            
        # Strip everything that is not an alphabet letter (removes numbers, brackets)
        pep = re.sub(r'[^a-zA-Z]', '', pep)
        return pep.upper()

    def clean_sequence(self, raw_seq):
        """Removes fasta headers, spaces, and line breaks."""
        # Remove FASTA header if it exists
        lines = raw_seq.split('\n')
        clean_lines = [line for line in lines if not line.startswith('>')]
        clean_str = "".join(clean_lines)
        
        # Remove all whitespace/hidden characters
        clean_str = re.sub(r'\s+', '', clean_str)
        return clean_str.upper()

    # ---------- PHASE 2 & 3: MAPPING & PREVIEW ----------
    def generate_preview(self):
        raw_seq = self.seq_text.get("1.0", tk.END)
        raw_peps = self.pep_text.get("1.0", tk.END).split('\n')

        sequence = self.clean_sequence(raw_seq)
        if not sequence:
            messagebox.showwarning("Empty Input", "Please provide a parent sequence.")
            return

        # Clean peptides and remove empty ones
        peptides = list(set(filter(None, [self.clean_peptide(p) for p in raw_peps])))
        
        if not peptides:
            messagebox.showwarning("Empty Input", "Please provide at least one peptide.")
            return

        # --- MULTI-MAPPING ALGORITHM ---
        # Create an array to hold the color of every single character
        char_colors = [None] * len(sequence)
        unmapped = []
        color_map = {}

        for idx, pep in enumerate(peptides):
            # Assign color
            color = self.palette[idx % len(self.palette)]
            color_map[pep] = color

            start = 0
            found = False
            # Find ALL occurrences, not just the first one
            while True:
                start = sequence.find(pep, start)
                if start == -1: break
                found = True
                # Paint the array
                for i in range(start, start + len(pep)):
                    char_colors[i] = color
                start += 1 # Advance by 1 to catch overlapping duplicates

            if not found:
                unmapped.append(pep)

        self.open_preview_window(sequence, char_colors, unmapped)

    def open_preview_window(self, sequence, char_colors, unmapped):
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Preview & Export")
        preview_win.geometry("900x700")

        # Orphan Report
        if unmapped:
            warning_text = f"⚠️ WARNING: {len(unmapped)} peptides could not be mapped to the parent sequence."
            tk.Label(preview_win, text=warning_text, fg="red", font=("Arial", 10, "bold")).pack(pady=5)
            # Print to terminal for debugging just in case
            print("Unmapped:", unmapped)

        # The Read-Only Preview Area
        preview_text = tk.Text(preview_win, wrap="none", font=("Courier New", 12))
        preview_text.pack(expand=True, fill="both", padx=10, pady=5)

        # --- CLUSTAL WRAP ENGINE (60 chars per line) ---
        chunk_size = 60
        for i in range(0, len(sequence), chunk_size):
            chunk_seq = sequence[i:i+chunk_size]
            chunk_colors = char_colors[i:i+chunk_size]

            # Group characters by color to build tags efficiently
            current_str = chunk_seq[0]
            current_color = chunk_colors[0]

            for j in range(1, len(chunk_seq)):
                if chunk_colors[j] == current_color:
                    current_str += chunk_seq[j]
                else:
                    self._insert_colored(preview_text, current_str, current_color)
                    current_str = chunk_seq[j]
                    current_color = chunk_colors[j]
            
            # Insert the final piece of the chunk
            self._insert_colored(preview_text, current_str, current_color)
            preview_text.insert(tk.END, "\n") # Force the Clustal break

        # Lock the text box so user can't break the alignment
        preview_text.config(state=tk.DISABLED)

        # Action Bar
        btn_frame = tk.Frame(preview_win, pady=10)
        btn_frame.pack()
        
        # We pass the preview_text widget to the export functions
        tk.Button(btn_frame, text="Export HTML", command=lambda: self.save_html(preview_text)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Export Word (.docx)", command=lambda: self.save_docx(preview_text)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Export RTF (.rtf)", command=lambda: self.save_rtf(preview_text)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Go Back", command=preview_win.destroy).pack(side="left", padx=5)

    def _insert_colored(self, widget, text, color):
        """Helper to inject text with specific color tags"""
        if color:
            tag = f"c_{color}"
            widget.tag_configure(tag, foreground=color, font=("Courier New", 12, "bold"))
            widget.insert(tk.END, text, tag)
        else:
            widget.insert(tk.END, text)

    # ---------- EXPORT ENGINES ----------
    def _get_segments(self, text_widget):
        """Translates Tkinter tags to raw text/color tuples for exporting."""
        dump = text_widget.dump("1.0", "end-1c", text=True, tag=True)
        active_color = None
        segments = []

        for type_, value, index in dump:
            if type_ == "tagon" and value.startswith("c_"):
                active_color = value.replace("c_", "")
            elif type_ == "tagoff" and value.startswith("c_"):
                active_color = None
            elif type_ == "text":
                segments.append((value, active_color))
        return segments

    def save_html(self, text_widget):
        file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML File", "*.html")])
        if not file_path: return

        segments = self._get_segments(text_widget)
        html = ["<html><body style='background:#1e1e1e; color:#d4d4d4; padding:20px;'>"]
        html.append("<h3>MUFASA Coverage Map</h3>")
        html.append("<pre style='font-family:\"Courier New\", Courier, monospace; font-size:14px; line-height:1.5;'>")

        for text, color in segments:
            if color:
                html.append(f"<span style='color:{color}; font-weight:bold;'>{text}</span>")
            else:
                html.append(text)

        html.append("</pre></body></html>")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("".join(html))
        webbrowser.open(f"file://{os.path.abspath(file_path)}")

    def save_docx(self, text_widget):
        if not HAS_DOCX:
            messagebox.showerror("Missing Library", "Please run 'pip install python-docx'.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")])
        if not file_path: return

        doc = Document()
        section = doc.sections[-1]
        new_w, new_h = section.page_height, section.page_width
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = new_w, new_h
        section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Courier New'
        style.font.size = Pt(9)
        
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)

        segments = self._get_segments(text_widget)
        for text, color in segments:
            parts = text.split('\n')
            for i, part in enumerate(parts):
                if part:
                    run = p.add_run(part)
                    if color:
                        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                        run.font.color.rgb = RGBColor(r, g, b)
                        run.font.bold = True
                if i < len(parts) - 1:
                    p = doc.add_paragraph()
                    p.paragraph_format.space_after = Pt(0)

        doc.save(file_path)
        messagebox.showinfo("Success", "Saved Word Document.")

    def save_rtf(self, text_widget):
        file_path = filedialog.asksaveasfilename(defaultextension=".rtf", filetypes=[("Rich Text", "*.rtf")])
        if not file_path: return

        segments = self._get_segments(text_widget)
        unique_colors = set(c for t, c in segments if c)
        color_to_idx = {c: i+1 for i, c in enumerate(unique_colors)}

        rtf = ["{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0\\fmodern\\fcharset0 Courier New;}}"]
        if unique_colors:
            ctbl = "{\\colortbl;"
            for c in unique_colors:
                r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
                ctbl += f"\\red{r}\\green{g}\\blue{b};"
            ctbl += "}"
            rtf.append(ctbl)

        rtf.append("\\landscape\\paperw15840\\paperh12240\\margl720\\margr720\\margt720\\margb720\n")
        rtf.append("\\f0\\fs18\n") # 9pt font

        for text, color in segments:
            text = text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}').replace('\n', '\\par\n')
            if color:
                idx = color_to_idx[color]
                rtf.append(f"\\cf{idx}\\b {text}\\b0\\cf0 ")
            else:
                rtf.append(text)

        rtf.append("}")
        with open(file_path, "w") as f:
            f.write("".join(rtf))
        messagebox.showinfo("Success", "Saved RTF.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MufasaMapper(root)
    root.mainloop()