![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
# MUFASA V4.0: Dynamic Comparative Proteomics Engine

**MUFASA (Molecular Utility For Annotating Sequence Alignments)** is a professional-grade desktop application designed for proteomics researchers and structural biologists.

It bridges the gap between **mass spectrometry peptide output** and **multiple sequence alignment (MSA)** by providing high-confidence visual heatmaps of peptide coverage across multiple homologous proteins.

---

## Why MUFASA?

Standard text editors and alignment tools are not built for mass spectrometry data.

When searching hundreds of peptides against multiple sequences, traditional scripts often suffer from:

- ❌ **Cross-contamination**
  - A peptide from Sample A falsely maps to Sequence B due to random matches

### MUFASA V4 Solution

- Enforces **strict 1:1 Dynamic Mapping**
- Isolates sequence-to-peptide searches
- Calculates coordinate shifts caused by alignment gaps (`-`)
- Produces **stacked, publication-ready heatmaps**

---

## Key Features

### Dynamic 1:1 Sequence Mapping
- Prevents peptide cross-contamination
- Ensures biologically accurate mapping

---

### Coverage Depth Heatmaps

A dual-array engine that shows **both location and depth** of peptide coverage:

| Coverage Level | Visualization |
|----------------|--------------|
| 1 peptide      | Standard text |
| 2 overlaps     | Soft Yellow background |
| 3 overlaps     | Soft Orange background |
| 4+ overlaps    | Soft Red background (Ultra-high confidence) |

---

### Seamless MAFFT Integration
- Run **global sequence alignment locally**
- Supports:
  - Background multithreading
  - Pre-aligned sequences (web server input)

---

### Coordinate Shift Auto-Correction
- Maps peptides from **unaligned → aligned sequences**
- Correctly accounts for alignment gaps (`-`)
- Ensures **perfect visual continuity**

---

### Negative Gap Highlighting (Reverse Mode)
- Flip logic instantly
- Hide mapped regions
- Highlight **missing coverage (gaps)** in bright red

---

### Multi-Format Publishing

Export results while preserving formatting:

- HTML  
- Microsoft Word (`.docx`)  
- Rich Text (`.rtf`)  

---

## Installation & Setup

MUFASA is a **Python-based GUI application**.

### Requirements

- Python 3.8+

---

### Install Dependencies

    pip install -r requirements.txt

> Note: `python-docx` is required for Word export.

---

## MAFFT Installation (Required for Local Alignment)

### Windows

1. Download from: https://mafft.cbrc.jp/alignment/software/  
2. Extract to: `C:\Program Files\mafft`

3. Add MAFFT `bat` folder to **System PATH**

---

### macOS (Homebrew)

    brew install mafft

---

### Linux / Ubuntu / WSL

    sudo apt-get update
    sudo apt-get install mafft

---

## How to Use

### Unified Interface

Run:

    python mufasa_main.py

This launches a tabbed interface that integrates both the proteomics engine and the sequence editor into a single application.

---

### Main Proteomics Engine

Run:

    python mufasa_proteomics_engine.py

#### Steps:

1. Enter number of sequences  
2. Click **Generate Input Rows**  
3. Paste:  
   - FASTA sequence (with `>` header) → left  
   - Excel peptide column → right  
4. Choose alignment mode:  
   - Run MAFFT  
   - Pre-Aligned  
5. Click **Generate Coverage Map**

---

### Standalone Sequence Editor

Run:

    python mufasa_notepad_editor.py

#### Features:

- FASTA editing  
- Motif search (`Ctrl + F`)  
- Manual highlighting  
- Export to Word / RTF  

---

## Architecture Notes

- Built using **Python `tkinter`** for a lightweight GUI  

### Core Components:

- `threading` → prevents UI freezing during heavy computations  
- `subprocess` → executes MAFFT alignment asynchronously  

---

## Performance Design

- Handles **O(N²)** alignment complexity efficiently  
- Runs heavy tasks asynchronously  

---

## Cross-Platform Support

- Uses Python’s `platform` module for OS detection  

Automatically adapts instructions for:

- Windows  
- macOS  
- Linux / WSL  

---