# Quick Guide: Add Plots to Word

## The Easiest Way

### Step 1: Run Cell 46 in Notebook (HTML Export - Always Works)

1. Open `phase1_analysis.ipynb` in Jupyter
2. Scroll to **Cell 46** (the one with "ALTERNATIVE: Export plots as HTML")
3. **Run that cell**
4. Wait for "✅ Exported HTML" messages

### Step 2: Open HTML and Screenshot

1. Open: `figures/word_report/index.html` in your web browser
2. Click each plot link
3. **Right-click on the plot** → "Save image as..." or take a screenshot
4. Open your Word document (`Phase1_Report.docx`)
5. Paste each image where you want it

**That's it!** Simple and always works.

---

## Alternative: Try Cell 45 First (Auto PNG Export)

If you want automatic PNG export:

1. Run **Cell 45** in notebook (may need kaleido fix)
2. If it works, run: `python scripts/export_and_add_to_word.py`
3. If it fails, use Cell 46 method above

---

## Summary

**Easiest:** Cell 46 → Open HTML → Screenshot → Paste to Word  
**Automated:** Cell 45 → Run script → Done

**I recommend Cell 46** - it's simpler and always works!

