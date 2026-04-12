import tkinter as tk
from tkinter import ttk

# Import your existing classes from the other files
from mufasa_proteomics_engine import MufasaV4
from mufasa_notepad_editor import SequenceNotepad

class MufasaUnifiedInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("MUFASA Studio - Unified Proteomics Suite")
        self.root.geometry("1200x800")
        
        # Create the Tabbed Environment (Notebook)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")
        
        # --- TAB 1: The Proteomics Engine ---
        self.tab_engine = tk.Frame(self.notebook)
        self.notebook.add(self.tab_engine, text="🔬 Comparative Heatmap Engine")
        
        # Initialize V4 Engine inside Tab 1
        # Note: You will need to slightly modify MufasaV4 to accept a Frame instead of the Tk() root
        self.engine_app = MufasaV4(self.tab_engine) 
        
        # --- TAB 2: The Sequence Notepad ---
        self.tab_editor = tk.Frame(self.notebook)
        self.notebook.add(self.tab_editor, text="📝 Manual Sequence Editor")
        
        # Initialize Notepad inside Tab 2
        self.editor_app = SequenceNotepad(self.tab_editor)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Optional: Apply a modern theme if you are running this on a Linux/Ubuntu environment
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
        
    app = MufasaUnifiedInterface(root)
    root.mainloop()