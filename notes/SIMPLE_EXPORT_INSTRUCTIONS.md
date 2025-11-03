# Simple: Export Plots for Word Document

## The Problem
The PNG export needs kaleido + Chrome, which can have issues.

## The Solution (Use Cell 46)

**Just run Cell 46** in your notebook - it exports plots as HTML files (always works).

### Step 1: Run Cell 46
1. Open `phase1_analysis.ipynb`
2. Scroll to **Cell 46** (titled "ALTERNATIVE: Export plots as HTML")
3. **Run that cell**
4. It will create HTML files in `figures/word_report/`

### Step 2: Get PNGs from HTML

**Option A: Browser Screenshot (Easiest)**
1. Open `figures/word_report/index.html` in your browser
2. Click each plot link
3. Take screenshot of each plot (Win+Shift+S or Cmd+Shift+4)
4. Paste into Word document

**Option B: Use a Conversion Script (Coming Next)**
I'll create a simple script to convert HTML → PNG automatically.

---

## What Cell 46 Does

- Exports all plots as **HTML files** (no kaleido needed!)
- Creates an `index.html` page listing all plots
- You open in browser and screenshot

**That's it!** Much simpler than fighting with kaleido/Chrome issues.

