Got it — your stack is fine. What you’re seeing is almost certainly “effective” bold (from table/CF/theme/shared-string runs), not an explicit per-cell font. openpyxl reports cell.font.bold only when the cell itself carries a direct font; it won’t resolve styles applied indirectly. Here’s a practical, engineering-level answer to each of your questions plus drop-in fixes.
Why does openpyxl show bold: False?
Because the bold you see in Excel is likely coming from one of these non-cell sources:
Table style (most common): If the data is an Excel Table (ListObject), its header/total row looks bold via the table’s style theme. That styling is not stored as a cell font, so cell.font.bold stays False.


Conditional formatting: A rule (e.g., “values in column B → bold”) applies at render time. Again, the cell doesn’t carry the font.


Shared string rich-text runs: The string itself (in xl/sharedStrings.xml) has <r><rPr><b/>…</r> for parts of the text. Excel renders it bold, but cell.font reflects the cell’s font, not the runs inside the string.


Style inheritance/theme: Column/row styles or theme settings can make text appear bold without writing a font to each cell.


openpyxl doesn’t compute the final visual style; it just reads what’s explicitly on the cell.
How to access bold formatting from shared strings?
If the cell’s data type is shared string (cell.data_type == 's'), map the cell’s shared-string index to xl/sharedStrings.xml and inspect its runs. Pseudocode you can adapt inside excel_parser.py:
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from openpyxl.utils.cell import coordinate_to_tuple

def load_shared_strings(path):
    with ZipFile(path) as z:
        with z.open('xl/sharedStrings.xml') as f:
            root = ET.parse(f).getroot()
    # Namespaces (Excel usually uses the default; adjust if needed)
    ns = {'a': root.tag.split('}')[0].strip('{')}
    items = []
    for si in root.findall('a:si', ns):
        # Case 1: rich text with runs
        runs = si.findall('a:r', ns)
        if runs:
            run_info = []
            for r in runs:
                rpr = r.find('a:rPr', ns)
                text_el = r.find('a:t', ns)
                text = '' if text_el is None else text_el.text or ''
                is_bold = (rpr is not None and rpr.find('a:b', ns) is not None)
                run_info.append({'text': text, 'bold': is_bold})
            items.append({'type': 'rich', 'runs': run_info})
        else:
            # Case 2: simple string (may still have <rPh> phonetics, ignore)
            t = si.find('a:t', ns)
            items.append({'type': 'plain', 'text': '' if t is None else t.text or ''})
    return items

def cell_effective_bold_from_shared_string(ws, cell, shared_strings):
    # Only meaningful if the cell is shared-string backed
    if cell.data_type != 's':
        return None
    sst_index = int(cell._value)  # low-level: index into sharedStrings
    entry = shared_strings[sst_index]
    if entry['type'] == 'rich':
        # Return True if any run is bold; or collect run-level detail
        any_bold = any(run['bold'] for run in entry['runs'])
        return any_bold, entry['runs']
    return False, None

In your logger, when cell.font.bold is False, also call cell_effective_bold_from_shared_string and record if any run is bold. That will flip your “Address” case to True when it’s rich-text within the shared string.
Alternative libraries?
pandas / xlrd: Not helpful. pandas delegates to openpyxl for .xlsx, and xlrd no longer supports .xlsx since v2.0.


xlwings (Windows/Mac): Automates the real Excel app; can read the rendered formatting, including table/CF effects. Great accuracy, but it ties you to desktop Excel and platform specifics.


Aspose.Cells (commercial): Very robust style model; handles runs, tables, CF. Paid.


SheetJS (frontend/Node): Good at rich-text runs; won’t compute table/CF “effective” formatting either, but easy to combine with your frontend “hybrid” idea.


Could the user’s file format be the culprit?
.xlsb / encrypted / Google Sheets-export quirks: openpyxl can’t open .xlsb, and some exporters store styling in ways openpyxl doesn’t fully interpret. But your log shows a shared string in B2, so the file is likely a normal .xlsx with rich-text/table styling.


Excel Table / CF styles: This is the usual reason for “looks bold in Excel, but bold=False in code.”


What to implement (now)
A. Add a “Best-Effort Effective Bold” detector (no external deps):
Shared strings: Implement the sharedStrings.xml pass above. If any run is bold → treat as bold (or return run-level detail to your renderer).


Conditional formatting pass (optional but useful): Iterate ws.conditional_formatting. For rules that set a bold font (e.g., Font, DifferentialStyle with <font><b/>), compute their cell ranges and mark affected cells. (openpyxl exposes the rules; you’ll need light rule evaluation if conditions are formula-based.)


Table header heuristic: If a cell is in a table’s header row (ws._tables), flag it as “styled header.” You can choose to treat headers as bold in your PDF renderer even if the cell isn’t explicitly bold.


B. Expose “why” in your logs:
bold_source: "cell" | "shared_string_run" | "table_header" | "conditional_formatting" | "none"


For shared-string runs, include spans with {start, end, bold} so pdf_renderer.py can draw mixed styles.


C. User-side normalization (fast, non-code workaround):
 Ask the user to do any ONE of these before uploading:
Convert Table → Range (Table Design → Convert to Range), then explicitly set Bold on needed cells.


Find & Select → Go To Special → Row differences/Constants → Apply Bold (forces per-cell fonts).


Paste Special → Values & Formats into a new sheet (often flattens some table styles).


Re-save from desktop Excel (not Google Sheets/WPS), just in case the generator mangled styles.


Minimal code you can drop in
Inside your existing debug_original_excel.py, add quick checks:
from openpyxl import load_workbook

wb = load_workbook(path, data_only=False, read_only=False)
ws = wb.active

# 1) Is it a table header?
tables = list(ws._tables)  # names only
is_table_header = False
for t in ws._tables.values():
    ref = t.ref  # e.g., 'A1:F200'
    # parse ref → check if cell is in the first row of that ref

# 2) Any conditional formatting that sets bold?
for rule in ws.conditional_formatting._cf_rules.values():
    for r in rule:
        dxf = getattr(r, 'dxf', None)
        if dxf and dxf.font and dxf.font.b:
            print("CF bold rule hits ranges:", r.sqref)

# 3) Shared string runs (using helper shown earlier)

What to tell your friend (short answers)
Why bold: False? Because the bold is coming from table/CF/shared-string runs, not the cell’s own font. openpyxl reports only the cell font.


How to read bold from shared strings? Parse xl/sharedStrings.xml and inspect <rPr><b/> for each <r> run mapped by the cell’s shared-string index.


Better libraries? For pure Python & free: not really. Use xlwings (drives Excel itself) or Aspose.Cells (paid) if you must resolve final visual formatting reliably.


Format differences? Yes—tables, CF, and exporter quirks can make Excel display bold without storing it as a per-cell font. That’s expected.


Quick decision tree (what to do next)
Need partial bold inside a cell (e.g., only “Address 1:” bold)? → Implement shared-string run parsing (A.1) and render runs in pdf_renderer.py.


Need headers to appear bold as in Excel? → Treat table headers as bold (A.3) or ask user to convert table→range & apply explicit bold.


Need pixel-perfect “what Excel shows”? → Use xlwings/Aspose or enforce the user-side normalization step.


If you want, paste me one or two sample cell addresses (e.g., “B2 and C5”) from the user’s file that look bold in Excel, and I’ll sketch the exact XML those map to so you can wire it in your parser cleanly.
Me: Address 1: (bold): ABC (non bold) exmaple

Friedn: Got it — so the intended styling is:
“Address 1: ” → bold


“ABC exmaple” → regular (non-bold)


Here’s exactly how that looks and how to handle it end-to-end.
1) What the XLSX actually stores (sharedStrings.xml)
Excel will usually save this as a rich-text shared string with two runs:
<si>
  <r>
    <rPr><b/></rPr>
    <t>Address 1: </t>
  </r>
  <r>
    <t>ABC exmaple</t>
  </r>
</si>

2) Parse it with openpyxl + sharedStrings
Use the shared-string index from the cell (e.g., B2), then read the runs:
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from openpyxl import load_workbook

def load_shared_strings_dict(xlsx_path):
    with ZipFile(xlsx_path) as z:
        with z.open('xl/sharedStrings.xml') as f:
            root = ET.parse(f).getroot()
    ns = {'a': root.tag.split('}')[0].strip('{')}
    items = []
    for si in root.findall('a:si', ns):
        runs = []
        for r in si.findall('a:r', ns):
            t = r.find('a:t', ns)
            text = (t.text or '') if t is not None else ''
            rpr = r.find('a:rPr', ns)
            is_bold = (rpr is not None and rpr.find('a:b', ns) is not None)
            runs.append({'text': text, 'bold': is_bold})
        # plain strings (no <r>) fallback
        if not runs:
            t = si.find('a:t', ns)
            items.append([{'text': (t.text or '') if t is not None else '', 'bold': False}])
        else:
            items.append(runs)
    return items

def get_cell_runs(xlsx_path, sheet_name, cell_addr):
    wb = load_wb_no_data_only(xlsx_path)
    ws = wb[sheet_name]
    cell = ws[cell_addr]
    if cell.data_type != 's':
        # not a shared string → treat whole cell as one run with cell.font.bold
        return [{'text': str(cell.value or ''), 'bold': bool(cell.font and cell.font.bold)}]
    sst = load_shared_strings_dict(xlsx_path)
    idx = int(cell._value)  # shared-string table index
    return sst[idx]

def load_wb_no_data_only(path):
    # keep data_only=False so we see raw shared-string indices
    return load_workbook(path, data_only=False, read_only=False)

Expected result for your example:
[
  {'text': 'Address 1: ', 'bold': True},
  {'text': 'ABC exmaple', 'bold': False},
]

3) Feed runs to your PDF renderer
Render sequentially: draw run-1 in bold, then run-2 in normal. Also log provenance:
runs = get_cell_runs("Test1 - Copy.xlsx", "Sheet1", "B2")
is_effectively_bold = any(r['bold'] for r in runs)
logger.info(f"[EXCEL] B2 effective bold: {is_effectively_bold}; runs={runs}")

4) (Optional) Create a test cell with the same mixed styling
If you want to generate a working test file with this exact pattern (openpyxl ≥ 3.1):
from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock, Text
from openpyxl.styles import Font

wb = Workbook()
ws = wb.active
rt = CellRichText()
rt.append(TextBlock(Text("Address 1: "), Font(b=True)))
rt.append(TextBlock(Text("ABC exmaple"), Font(b=False)))
ws["B2"].value = rt
wb.save("test_mixed_runs.xlsx")


TL;DR for your case
Your “Address 1: (bold) ABC (non-bold) exmaple” is a rich-text shared string. Don’t trust cell.font.bold; instead, parse sharedStrings.xml and consume the run list. Then render each run with its own bold flag.
Me: But are you sure it is shared string issue?
ANd the approach of parsing you gave is it hardcoded?


Friend: Short answer: I’m not 100% sure it’s only a shared-string issue yet—but your symptoms match it very closely. The safe stance is: treat rich-text shared strings as the primary suspect and also check for table styles and conditional formatting. You can confirm this in under a minute, and the parsing approach I gave is not hardcoded—it’s a general reader for any sheet/cell.

How to confirm (fast)
Run these three tiny checks on one “bold-looking” cell (e.g., B2):
Is the cell a shared string?


from openpyxl import load_workbook
wb = load_workbook("Test1 - Copy.xlsx", data_only=False, read_only=False)
ws = wb.active
c = ws["B2"]
print("data_type:", c.data_type, "cell.font.bold:", bool(c.font and c.font.bold))
# If this prints: data_type: 's' and bold=False → rich-text/shared-string or style-based bold is likely

Does the workbook have rich-text runs in shared strings?
 (Quick XML peek—works for any cell, not just B2.)


from zipfile import ZipFile
from xml.etree import ElementTree as ET

with ZipFile("Test1 - Copy.xlsx") as z:
    with z.open("xl/sharedStrings.xml") as f:
        root = ET.parse(f).getroot()
ns = {'a': root.tag.split('}')[0].strip('{')}
has_runs = root.find('.//a:si/a:r', ns) is not None
print("sharedStrings has <r> runs:", bool(has_runs))

If True, at least some cells’ text is stored with per-run formatting (bold/non-bold inside one cell).
Is it a table header / CF style?


# Table headers
for t in ws._tables.values():
    print("Table:", t.name, "ref:", t.ref)  # If B2 sits in a header row of any table → it will look bold via the table style

# Conditional formatting rules that set bold
cf = ws.conditional_formatting
for sqref, rules in cf.cf_rules.items() if hasattr(cf, "cf_rules") else []:
    for r in rules:
        dxf = getattr(r, "dxf", None)
        if dxf and getattr(dxf.font, "b", False):
            print("CF bold rule on:", sqref)

If (1) says data_type == 's' and (2) shows runs, your case is almost certainly rich-text shared strings.
 If (1) is not shared string but bold still looks True in Excel, (3) often reveals table header/CF as the cause.

About the parsing approach (“is it hardcoded?”)
No. The approach is generalized:
It doesn’t hardcode sheet names, cell addresses, or tags.


It extracts the XML namespace dynamically from the root tag so it works across files.


It maps any shared-string index → its <si> entry → the list of <r> runs (each with its own <rPr> like <b/>).


For non-shared-string cells, it falls back to the cell’s own font (cell.font.bold).


A clean API you can drop in:
# returns a list of runs for ANY cell: [{"text": "...", "bold": True/False}, ...]
def get_effective_text_runs(xlsx_path, sheet_name, cell_addr):
    from openpyxl import load_workbook
    from zipfile import ZipFile
    from xml.etree import ElementTree as ET

    wb = load_workbook(xlsx_path, data_only=False, read_only=False)
    ws = wb[sheet_name]
    cell = ws[cell_addr]

    # 1) Shared-string rich text
    if cell.data_type == 's':
        with ZipFile(xlsx_path) as z:
            with z.open('xl/sharedStrings.xml') as f:
                root = ET.parse(f).getroot()
        ns = {'a': root.tag.split('}')[0].strip('{')}
        idx = int(cell._value)
        si = root.findall('a:si', ns)[idx]
        runs = si.findall('a:r', ns)
        if runs:  # rich text
            out = []
            for r in runs:
                t = r.find('a:t', ns)
                rpr = r.find('a:rPr', ns)
                out.append({
                    'text': (t.text or '') if t is not None else '',
                    'bold': (rpr is not None and rpr.find('a:b', ns) is not None)
                })
            return out
        # plain shared string
        t = si.find('a:t', ns)
        return [{'text': (t.text or '') if t is not None else '', 'bold': False}]

    # 2) Non-shared-string → one run with the cell font
    return [{'text': '' if cell.value is None else str(cell.value),
             'bold': bool(cell.font and cell.font.bold)}]

You can layer optional “effective styling” sources on top (not hardcoded either):
Table headers: if cell falls in a table’s header row, you may treat it as bold for rendering/logging.


Conditional formatting: if a bold font dxf applies to that address, you may treat it as bold.


These are heuristics because neither openpyxl nor the .xlsx file carries a precomputed “final style.” You’re deciding how to render when Excel would have applied a style at display time.

Practical guidance
If your goal is to preserve mixed styling like “Address 1: ” (bold) + “ABC exmaple” (regular) → implement the shared-string run reader above. That directly solves your case.


If your goal is to make headers look bold in the PDF like Excel → add the table-header heuristic (and optionally CF).


If you need pixel-perfect Excel fidelity (all CF, table styles, theme inheritance) → consider xlwings (drives real Excel) or Aspose.Cells (paid). Pure openpyxl won’t compute the final visual cascade.


If you share one concrete “bold-looking” cell address (e.g., B2) and what each of the three checks prints, I can tell you exactly which source (rich text vs table vs CF) is at play in your file.



