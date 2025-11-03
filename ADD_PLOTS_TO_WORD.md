# Simple Instructions: Add Plots to Word Document

## Quick Steps (2 minutes)

### Step 1: Export Plots from Notebook

1. Open `phase1_analysis.ipynb` in Jupyter
2. Scroll to the **last cell** (Cell 45: "Export All Plots for Word Document")
3. **Run that cell**
4. Wait for it to finish - you'll see messages like "✅ Exported: 01_model_totals.png"

### Step 2: Add Plots to Word

Run this command:

```bash
python scripts/add_plots_to_word.py
```

Follow the prompts. The script will:
- Find all exported PNG files
- Add them to your Word document
- Create a new file: `Phase1_Report_with_figures.docx`

**That's it!** Open the new Word file and all your plots will be there.

---

## Alternative: Manual Method

If the script doesn't work:

1. **Export plots** (Step 1 above)
2. **Open** `Phase1_Report.docx` in Microsoft Word
3. **Go to the end** of the document
4. **Insert each PNG**:
   - Insert → Pictures → This Device
   - Select from `figures/word_report/`
   - Add caption below each figure

---

## Troubleshooting

**Problem:** "No PNG files found"
- **Solution:** Make sure you ran Cell 45 in the notebook first

**Problem:** "kaleido not installed"  
- **Solution:** Run `pip install kaleido` (already done if you ran the script)

**Problem:** "python-docx not installed"
- **Solution:** The script will install it automatically

---

**Need help?** Check `figures/word_report/` - if PNG files are there, the export worked!

