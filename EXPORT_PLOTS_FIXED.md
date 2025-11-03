# ✅ Fixed: How to Export Plots

## The Issue
Kaleido needs Chrome, and on Ubuntu it requires sandbox to be disabled.

## The Fix
Cell 45 now automatically disables the sandbox. **Just run it!**

## Simple Instructions

### Step 1: Run Cell 45 in Notebook
1. Open `phase1_analysis.ipynb`
2. Go to **Cell 45** (titled "Export All Plots for Word Document")
3. **Run the cell**
4. Wait for "✅ Exported" messages

### Step 2: Add Plots to Word
Run this command:
```bash
python scripts/add_plots_to_word.py
```

This creates: `Phase1_Report_with_figures.docx`

---

## If Cell 45 Still Fails

Use **Cell 46** instead (HTML export - always works):
- Run Cell 46
- Opens HTML files in browser
- Screenshot plots from browser
- Paste into Word manually

---

## What Was Fixed

- ✅ Added sandbox disable for Ubuntu
- ✅ Automatic plotly/kaleido version check
- ✅ Error handling for each plot
- ✅ Alternative HTML export (Cell 46)

**Now try running Cell 45 again - it should work!**

