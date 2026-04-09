import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import webbrowser
import os
import threading
import subprocess
import tempfile
import shutil
import platform

try:
    from docx import Document
    from docx.shared import RGBColor, Pt, Inches
    from docx.enum.section import WD_ORIENT
    from docx.enum.text import WD_COLOR_INDEX
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

class MufasaV4:
    def __init__(self, root):
        self.root = root
        self.root.title("MUFASA V4 - Dynamic Comparative Proteomics Engine")
        self.root.geometry("1100x750")

        # --- TOP CONTROL BAR ---
        top_frame = tk.Frame(root, padx=10, pady=10, bg="#E0E0E0")
        top_frame.pack(fill="x")

        # Number Generator
        tk.Label(top_frame, text="Number of Sequences:", font=("Arial", 10, "bold"), bg="#E0E0E0").pack(side="left")
        self.num_seq_var = tk.StringVar(value="2")
        tk.Spinbox(top_frame, from_=1, to=50, textvariable=self.num_seq_var, width=5, font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(top_frame, text="Generate Input Rows", command=self.generate_input_rows, bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=10)

        # Alignment Mode
        tk.Label(top_frame, text=" | Alignment Mode:", font=("Arial", 10, "bold"), bg="#E0E0E0").pack(side="left", padx=(10, 5))
        self.align_mode = tk.StringVar(value="RAW")
        tk.Radiobutton(top_frame, text="Run MAFFT", variable=self.align_mode, value="RAW", bg="#E0E0E0").pack(side="left")
        tk.Radiobutton(top_frame, text="Pre-Aligned", variable=self.align_mode, value="PRE", bg="#E0E0E0").pack(side="left")

        # Help Button
        tk.Button(top_frame, text="❓ Help & Manual", font=("Arial", 9, "bold"), bg="#FF9800", fg="white", command=self.show_help_manual).pack(side="right", padx=5)

        # --- SCROLLABLE MAIN AREA ---
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")

        # --- BOTTOM ACTION BAR ---
        bottom_frame = tk.Frame(root, pady=10)
        bottom_frame.pack(fill="x", side="bottom")
        
        self.reverse_mode = tk.BooleanVar(value=False)
        tk.Checkbutton(bottom_frame, text="Reverse Mode (Highlight missing gaps)", variable=self.reverse_mode, font=("Arial", 10, "bold"), fg="#D32F2F").pack(side="top", pady=5)
        
        self.generate_btn = tk.Button(bottom_frame, text="GENERATE COVERAGE MAP", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.start_pipeline)
        self.generate_btn.pack(pady=5, ipadx=20, ipady=5)

        self.font_palette = ["#000080", "#800000", "#006400", "#4B0082", "#8B4513", "#2F4F4F"]
        self.input_cells = [] # Stores references to the text boxes

        # Initialize default rows
        self.generate_input_rows()

    # ---------- DYNAMIC UI GENERATION ----------
    def generate_input_rows(self):
        """Clears the canvas and generates exactly N pairs of input boxes."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.input_cells.clear()
        
        try:
            num = int(self.num_seq_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        for i in range(num):
            row_frame = tk.LabelFrame(self.scrollable_frame, text=f"Sequence Data {i+1}", font=("Arial", 10, "bold"), padx=10, pady=10)
            row_frame.pack(fill="x", pady=5, expand=True)

            # Sequence Input (Left)
            seq_frame = tk.Frame(row_frame)
            seq_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            tk.Label(seq_frame, text="Paste FASTA (with > header):").pack(anchor="w")
            seq_text = tk.Text(seq_frame, height=6, wrap="word", font=("Courier New", 9))
            seq_text.pack(fill="both", expand=True)

            # Peptide Input (Right)
            pep_frame = tk.Frame(row_frame)
            pep_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            tk.Label(pep_frame, text="Paste corresponding Peptides:").pack(anchor="w")
            pep_text = tk.Text(pep_frame, height=6, wrap="none", font=("Courier New", 9))
            pep_text.pack(fill="both", expand=True)

            self.input_cells.append({"seq_widget": seq_text, "pep_widget": pep_text})

    # ---------- NEW: TABBED HELP & MANUAL ----------
    def show_help_manual(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("MUFASA Help Center")
        help_win.geometry("600x500")

        notebook = ttk.Notebook(help_win)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # TAB 1: User Manual
        manual_frame = tk.Frame(notebook, bg="#F5F5F5")
        notebook.add(manual_frame, text="User Manual")
        
        manual_text = tk.Text(manual_frame, wrap="word", font=("Arial", 10), padx=10, pady=10, bg="#F5F5F5")
        manual_text.pack(expand=True, fill="both")
        
        manual_content = """MUFASA V4 - User Guide

1. SETTING UP YOUR WORKSPACE
At the top left, enter the number of sequences you want to analyze and click "Generate Input Rows". The software will create distinct boxes for each sequence. This 1:1 mapping prevents peptide cross-contamination.

2. ENTERING DATA
- Left Box (FASTA): Paste your full FASTA sequence here. It MUST include the header line starting with '>' (e.g., >Sequence_1).
- Right Box (Peptides): Paste your column of peptides. Brackets, weights, and cleavage dots (e.g., K.A[+80]SD.R) will be automatically cleaned by the software.

3. CHOOSING AN ALIGNMENT MODE
- Run MAFFT: Choose this if you pasted raw sequences. MUFASA will use your local CPU to perfectly align them and dynamically shift your peptide coordinates to match the gaps. (Requires MAFFT installed).
- Pre-Aligned: Choose this if you already aligned your sequences online. MUFASA will skip MAFFT and map peptides directly onto the gaps you provided.

4. REVERSE MODE
Check the box at the bottom to flip the logic. Mapped areas will be hidden, and gaps (missing coverage) will be highlighted in bright red.

5. THE DEPTH HEATMAP
MUFASA automatically calculates overlapping coverage.
- Single Coverage = Standard text color.
- Double Coverage = Soft Yellow background.
- Triple Coverage = Soft Orange background.
- 4+ Overlaps = Soft Red background."""
        manual_text.insert(tk.END, manual_content)
        manual_text.config(state=tk.DISABLED)

        # TAB 2: MAFFT Setup
        setup_frame = tk.Frame(notebook, bg="#F5F5F5")
        notebook.add(setup_frame, text="MAFFT Installation")
        
        setup_text = tk.Text(setup_frame, wrap="word", font=("Arial", 10), padx=10, pady=10, bg="#F5F5F5")
        setup_text.pack(expand=True, fill="both")
        
        os_name = platform.system()
        setup_content = f"Detected OS: {os_name}\n\n"
        
        if os_name == "Windows":
            setup_content += "1. Download 'MAFFT for Windows' from the official website.\n2. Extract folder to C:\\Program Files\\mafft.\n3. ADD TO SYSTEM PATH:\n   - Search Windows for 'Environment Variables'.\n   - Click 'Edit the system environment variables'.\n   - Click 'Environment Variables' button.\n   - Under 'System variables', find 'Path' and click 'Edit'.\n   - Click 'New' and paste the path to your MAFFT 'bat' folder.\n   - Click OK, close MUFASA, and restart."
        elif os_name == "Darwin":
            setup_content += "1. Open the Terminal application.\n2. Run this command:\n   brew install mafft\n3. Restart MUFASA."
        elif os_name == "Linux":
            setup_content += "1. Open Terminal.\n2. Run commands:\n   sudo apt-get update\n   sudo apt-get install mafft\n3. Restart MUFASA."
        else:
            setup_content += "Please visit the official MAFFT website to install the CLI version for your OS."
            
        setup_text.insert(tk.END, setup_content)
        setup_text.config(state=tk.DISABLED)

    # ---------- DATA EXTRACTION & PIPELINE ----------
    def clean_peptide(self, raw_pep):
        pep = raw_pep.strip()
        if not pep: return ""
        match = re.search(r"\.(.*?)\.", pep)
        if match: pep = match.group(1)
        return re.sub(r'[^a-zA-Z]', '', pep).upper()

    def extract_data_from_ui(self):
        """Reads the dynamic cells and builds the sequence/peptide dictionaries."""
        parsed_data = []
        for index, cell in enumerate(self.input_cells):
            raw_fasta = cell["seq_widget"].get("1.0", tk.END).strip()
            raw_peps = cell["pep_widget"].get("1.0", tk.END).strip().split('\n')
            
            if not raw_fasta: continue # Skip completely empty rows
            
            # Extract header and raw string from FASTA
            lines = raw_fasta.split('\n')
            header = f"Seq_{index+1}"
            seq_lines = []
            
            for line in lines:
                if line.startswith('>'):
                    header = line[1:].split()[0]
                else:
                    seq_lines.append(re.sub(r'\s+', '', line))
                    
            raw_seq = "".join(seq_lines).upper()
            
            # Clean peptides specific to THIS sequence
            peptides = list(set(filter(None, [self.clean_peptide(p) for p in raw_peps])))
            peptides.sort(key=len)
            
            parsed_data.append({
                "header": header,
                "raw": raw_seq,
                "peptides": peptides
            })
            
        return parsed_data

    def start_pipeline(self):
        if self.align_mode.get() == "RAW" and not shutil.which("mafft"):
            messagebox.showerror("MAFFT Not Found", "MAFFT is not detected. Click '❓ Help & Manual' for setup instructions.")
            self.show_help_manual()
            return

        parsed_data = self.extract_data_from_ui()
        if not parsed_data:
            messagebox.showwarning("Empty Input", "Please provide data in at least one sequence row.")
            return

        self.generate_btn.config(state=tk.DISABLED, text="PROCESSING... PLEASE WAIT")
        thread = threading.Thread(target=self.run_heavy_math, args=(parsed_data,))
        thread.daemon = True
        thread.start()

    # ---------- MATHEMATICAL CORE ----------
    def run_heavy_math(self, parsed_data):
        try:
            # 1. Alignment
            if self.align_mode.get() == "RAW" and len(parsed_data) > 1:
                aligned_seqs = self.run_mafft(parsed_data)
            else:
                aligned_seqs = [item['raw'] for item in parsed_data]

            processed_data = []
            total_unmapped = 0

            # 2. 1:1 Coordinate Shift
            for i, seq_obj in enumerate(parsed_data):
                aligned_seq = aligned_seqs[i]
                raw_seq = aligned_seq.replace('-', '') 
                peptides = seq_obj['peptides']
                
                # Search peptides ONLY against their specific parent sequence
                raw_fgs, raw_bgs, found_peps = self.map_peptides(raw_seq, peptides)
                total_unmapped += (len(peptides) - len(found_peps))

                bridge = self.build_index_map(aligned_seq)

                aligned_fgs = [None] * len(aligned_seq)
                aligned_bgs = [0] * len(aligned_seq)

                for raw_idx in range(len(raw_seq)):
                    algn_idx = bridge[raw_idx]
                    aligned_fgs[algn_idx] = raw_fgs[raw_idx]
                    aligned_bgs[algn_idx] = raw_bgs[raw_idx]

                    # Gap coloring math
                    if raw_idx < len(raw_seq) - 1:
                        next_algn_idx = bridge[raw_idx + 1]
                        if next_algn_idx > algn_idx + 1: 
                            if raw_bgs[raw_idx] > 0 and raw_bgs[raw_idx] == raw_bgs[raw_idx + 1]:
                                if raw_fgs[raw_idx] == raw_fgs[raw_idx + 1]:
                                    for gap_idx in range(algn_idx + 1, next_algn_idx):
                                        aligned_fgs[gap_idx] = raw_fgs[raw_idx]
                                        aligned_bgs[gap_idx] = raw_bgs[raw_idx]

                if self.reverse_mode.get():
                    for idx in range(len(aligned_seq)):
                        if aligned_seq[idx] == '-': continue 
                        if aligned_bgs[idx] > 0:
                            aligned_fgs[idx] = None
                            aligned_bgs[idx] = 0
                        else:
                            aligned_fgs[idx] = "#D32F2F"
                            aligned_bgs[idx] = 1

                processed_data.append({
                    "header": seq_obj['header'],
                    "aligned": aligned_seq,
                    "fgs": aligned_fgs,
                    "bgs": aligned_bgs
                })

            self.root.after(0, self.finish_pipeline, processed_data, total_unmapped)

        except Exception as e:
            self.root.after(0, self.pipeline_error, str(e))

    def run_mafft(self, parsed_data):
        with tempfile.TemporaryDirectory() as temp_dir:
            in_file = os.path.join(temp_dir, "in.fasta")
            with open(in_file, "w") as f:
                for i, seq in enumerate(parsed_data):
                    clean_seq = seq['raw'].replace('-', '')
                    f.write(f">seq_{i}\n{clean_seq}\n")

            result = subprocess.run(["mafft", "--quiet", "--auto", in_file], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("MAFFT Alignment Failed.")

            aligned = []
            curr = []
            for line in result.stdout.split('\n'):
                if line.startswith('>'):
                    if curr: aligned.append("".join(curr).upper())
                    curr = []
                else:
                    curr.append(line.strip())
            if curr: aligned.append("".join(curr).upper())
            return aligned

    def map_peptides(self, raw_seq, peptides):
        fgs = [None] * len(raw_seq)
        bgs = [0] * len(raw_seq)
        found_set = set()

        for idx, pep in enumerate(peptides):
            color = self.font_palette[idx % len(self.font_palette)]
            start = 0
            while True:
                start = raw_seq.find(pep, start)
                if start == -1: break
                found_set.add(pep)
                for i in range(start, start + len(pep)):
                    fgs[i] = color
                    bgs[i] += 1
                start += 1
        return fgs, bgs, found_set

    def build_index_map(self, aligned_seq):
        bridge = []
        for idx, char in enumerate(aligned_seq):
            if char != '-':
                bridge.append(idx)
        return bridge

    # ---------- GUI PREVIEW & EXPORT ----------
    def pipeline_error(self, error_msg):
        self.generate_btn.config(state=tk.NORMAL, text="GENERATE COVERAGE MAP")
        messagebox.showerror("Pipeline Error", error_msg)

    def finish_pipeline(self, processed_data, total_unmapped):
        self.generate_btn.config(state=tk.NORMAL, text="GENERATE COVERAGE MAP")
        self.open_preview_window(processed_data, total_unmapped)

    def get_bg_color(self, hits):
        if hits <= 1: return None
        if hits == 2: return "#FFF9C4"
        if hits == 3: return "#FFE0B2"
        return "#FFCDD2"

    def open_preview_window(self, processed_data, total_unmapped):
        preview_win = tk.Toplevel(self.root)
        preview_win.title("MUFASA V4 - Comparative Map")
        preview_win.geometry("1000x750")

        if total_unmapped > 0 and not self.reverse_mode.get():
            tk.Label(preview_win, text=f"⚠️ {total_unmapped} peptides could not be mapped to their specific sequences.", fg="#D32F2F", font=("Arial", 10, "bold")).pack(pady=5)

        preview_text = tk.Text(preview_win, wrap="none", font=("Courier New", 11), bg="#FAFAFA")
        preview_text.pack(expand=True, fill="both", padx=10, pady=5)

        chunk_size = 60
        total_length = len(processed_data[0]["aligned"])

        for i in range(0, total_length, chunk_size):
            for seq_obj in processed_data:
                header = seq_obj["header"][:12].ljust(14)
                preview_text.insert(tk.END, header)

                chunk_seq = seq_obj["aligned"][i:i+chunk_size]
                chunk_fg = seq_obj["fgs"][i:i+chunk_size]
                chunk_hits = seq_obj["bgs"][i:i+chunk_size]

                if chunk_seq:
                    current_str = chunk_seq[0]
                    current_fg = chunk_fg[0]
                    current_bg = self.get_bg_color(chunk_hits[0])

                    for j in range(1, len(chunk_seq)):
                        bg = self.get_bg_color(chunk_hits[j])
                        fg = chunk_fg[j]

                        if fg == current_fg and bg == current_bg:
                            current_str += chunk_seq[j]
                        else:
                            self._insert_styled(preview_text, current_str, current_fg, current_bg)
                            current_str = chunk_seq[j]
                            current_fg = fg
                            current_bg = bg
                    
                    self._insert_styled(preview_text, current_str, current_fg, current_bg)
                preview_text.insert(tk.END, "\n")
            preview_text.insert(tk.END, "\n") 

        preview_text.config(state=tk.DISABLED)

        btn_frame = tk.Frame(preview_win, pady=10)
        btn_frame.pack()
        tk.Button(btn_frame, text="Export HTML", command=lambda: self.save_html(preview_text)).pack(side="left", padx=5)

    def _insert_styled(self, widget, text, fg, bg):
        fg_str = fg if fg else "NONE"
        bg_str = bg if bg else "NONE"
        tag = f"style|{fg_str}|{bg_str}"
        kwargs = {"font": ("Courier New", 11, "bold" if fg else "normal")}
        if fg: kwargs["foreground"] = fg
        if bg: kwargs["background"] = bg
        widget.tag_configure(tag, **kwargs)
        widget.insert(tk.END, text, tag)

    def save_html(self, text_widget):
        file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML File", "*.html")])
        if not file_path: return
        dump = text_widget.dump("1.0", "end-1c", text=True, tag=True)
        html = ["<html><body style='background:#ffffff; padding:20px;'><pre style='font-family:\"Courier New\"; font-size:14px;'>"]
        
        active_fg, active_bg = None, None
        for type_, value, index in dump:
            if type_ == "tagon" and value.startswith("style|"):
                parts = value.split("|")
                active_fg = parts[1] if parts[1] != "NONE" else None
                active_bg = parts[2] if parts[2] != "NONE" else None
            elif type_ == "tagoff" and value.startswith("style|"):
                active_fg, active_bg = None, None
            elif type_ == "text":
                style = ""
                if active_fg: style += f"color:{active_fg}; font-weight:bold; "
                if active_bg: style += f"background-color:{active_bg}; "
                if style: html.append(f"<span style='{style}'>{value}</span>")
                else: html.append(value)

        html.append("</pre></body></html>")
        with open(file_path, "w", encoding="utf-8") as f: f.write("".join(html))
        webbrowser.open(f"file://{os.path.abspath(file_path)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MufasaV4(root)
    root.mainloop()