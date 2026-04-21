![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
# MUFASA V4.0: Dynamic Comparative Proteomics Engine

**MUFASA (Molecular Utility For Annotating Sequence Alignments)** is a professional-grade desktop application designed for proteomics researchers and structural biologists.

It bridges the gap between **mass spectrometry peptide output** and **multiple sequence alignment (MSA)** by providing high-confidence visual heatmaps of peptide coverage across multiple homologous proteins.

---
## Table of Contents
- [Why MUFASA?](#why-mufasa)
- [Key Features](#key-features)
- [Installation & Setup](#installation--setup)
- [Troubleshooting](#troubleshooting)
- [MAFFT Installation](#mafft-installation-required-for-local-alignment)
- [How to Use](#how-to-use)
- [Architecture Notes](#architecture-notes)
- [Acknowledgement](#acknowledgements)
- [Roadmap](#roadmap)
---

## Why MUFASA?

Standard text editors and alignment tools are not built for mass spectrometry data.

When searching hundreds of peptides against multiple sequences, traditional scripts often suffer from:

- **Cross-contamination**
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
## Troubleshooting
**Error: "MAFFT not found" on Windows**
* Ensure you extracted MAFFT to `C:\Program Files\mafft`.
* You MUST add the `bat` sub-folder inside the MAFFT directory to your System PATH Environment Variables. Restart your terminal/computer after doing this.

**Running on WSL (Windows Subsystem for Linux)**
* If you run MUFASA inside WSL, it operates as a Linux application. You must install the Linux version of MAFFT via `sudo apt-get install mafft` inside your WSL terminal, even if you already installed the Windows `.exe`.
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
## Acknowledgements
MUFASA relies on the mathematical backend of MAFFT for multiple sequence alignments. If you use the MAFFT integration in your research, please ensure you cite their work:
* Katoh, Standley 2013 ([Molecular Biology and Evolution 30:772-780](https://doi.org/10.1093/molbev/mst010))
* [MAFFT Official Website](https://mafft.cbrc.jp/alignment/software/)
---
## Roadmap
Future updates planned for the MUFASA engine:
- **Project Saving:** Ability to save and load workspace states (sequences and mapped peptides).
- **Export Options:** Direct export to high-resolution PDF for publications.
- **Advanced Alignment:** Potential integration of local pairwise alignment algorithms.
- **Data Export:** Export heatmap raw depth data directly to CSV.
- **FTIR Data Analysis:** Directly analyse the FTIR data.