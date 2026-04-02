import pandas as pd
import re
import random
import xlsxwriter
import webbrowser

# -------- FILES --------
FASTA_FILE = "fasta_excel.xlsx"
PEPTIDE_FILE = "peptide_excel.xlsx"

# -------- READ FASTA --------
fasta_df = pd.read_excel(FASTA_FILE, header=None)

protein_name = str(fasta_df.iloc[0, 0])
sequence = str(fasta_df.iloc[1, 0]).strip().upper()

# -------- READ PEPTIDES --------
pep_df = pd.read_excel(PEPTIDE_FILE, header=None)
raw_peptides = pep_df[0].dropna().tolist()

# -------- CLEAN --------
def extract_peptide(p):
    match = re.search(r"\.(.*?)\.", str(p))
    return match.group(1).upper() if match else None

clean_peptides = list(set(filter(None, [extract_peptide(p) for p in raw_peptides])))

# Save cleaned
pd.DataFrame(clean_peptides).to_excel("cleaned_peptides.xlsx", index=False, header=False)

print("Peptides:", clean_peptides)

# -------- FIND REGIONS --------
regions = []

for pep in clean_peptides:
    if pep in sequence:
        start = sequence.find(pep)
        end = start + len(pep)
        regions.append((start, end, pep))
    else:
        print("⚠️ Not found:", pep)

# Sort
regions.sort(key=lambda x: x[0])

# -------- COLORS --------
def rand_color():
    return "#" + ''.join(random.choices('89ABCDEF', k=6))

color_map = {pep: rand_color() for pep in clean_peptides}

# -------- BUILD SAFE SEGMENTS --------
segments = []
cursor = 0

for start, end, pep in regions:
    if start > cursor:
        segments.append(sequence[cursor:start])

    segments.append((sequence[start:end], color_map[pep]))
    cursor = end

if cursor < len(sequence):
    segments.append(sequence[cursor:])

# -------- WRITE EXCEL --------
wb = xlsxwriter.Workbook("output_colored.xlsx")
ws = wb.add_worksheet()

ws.write("A1", protein_name)

rich = []

for seg in segments:
    if isinstance(seg, tuple):
        text, color = seg
        fmt = wb.add_format({'bg_color': color})
        rich.append(fmt)
        rich.append(text)
    else:
        rich.append(seg)

# CRITICAL: must have at least 2 elements
if len(rich) > 1:
    ws.write_rich_string("A2", *rich)
else:
    ws.write("A2", sequence)

wb.close()

# -------- HTML --------
html = ""
i = 0

while i < len(sequence):
    matched = False
    for start, end, pep in regions:
        if i == start:
            color = color_map[pep]
            html += f"<span style='background:{color}'>{sequence[start:end]}</span>"
            i = end
            matched = True
            break
    if not matched:
        html += sequence[i]
        i += 1

html_content = f"""
<html>
<body style="font-family:monospace">
<h3>{protein_name}</h3>
<p>{html}</p>
</body>
</html>
"""

with open("output.html", "w") as f:
    f.write(html_content)

webbrowser.open("output.html")

print("✅ DONE")
