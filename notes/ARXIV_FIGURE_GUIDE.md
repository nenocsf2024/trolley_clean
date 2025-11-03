# Including PNG Plots in arXiv Submission

Based on [arXiv Submission Guidelines](https://info.arxiv.org/help/submit/index.html)

## Overview

arXiv accepts PNG figures when using **PDFLaTeX** processing. Your plots should be embedded directly in the LaTeX document, not linked externally.

## Accepted Figure Formats for PDFLaTeX

According to arXiv guidelines, these formats work with PDFLaTeX:
- **JPEG** (.jpg, .jpeg)
- **GIF** (.gif)
- **PNG** (.png) ✅ **Your plots can use this format**
- **PDF** (.pdf)

**Important:** If you're using regular (La)TeX (not PDFLaTeX), you must use PostScript formats (.ps, .eps) instead.

## Step-by-Step: Including PNG Plots in LaTeX

### 1. Export Plots as PNG

From your Jupyter notebook or Python scripts, save plots as PNG files:

```python
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# For matplotlib
plt.savefig('figure_temperature_effects.png', dpi=300, bbox_inches='tight')

# For plotly (convert to static PNG)
fig = go.Figure(...)
fig.write_image('figure_framing_effects.png', width=800, height=600, scale=2)
```

**Recommended settings:**
- **DPI**: 300 for publication quality
- **Width**: 800-1200 pixels (or ~6-8 inches at 150 DPI)
- **Height**: 600-900 pixels (or ~4-6 inches at 150 DPI)
- **Format**: PNG with good compression

### 2. Organize Figures in Submission

Create a `figures/` subdirectory in your submission:

```
your_paper/
├── main.tex
├── references.bib
├── figures/
│   ├── temperature_effects.png
│   ├── framing_effects.png
│   ├── judge_agreement.png
│   ├── scenario_difficulty.png
│   └── ...
```

### 3. Include Figures in LaTeX Document

Use the `graphicx` package (recommended) or `graphics` package:

```latex
\documentclass{article}
\usepackage{graphicx}  % Required for \includegraphics
\usepackage{float}     % Optional: for better figure placement

\begin{document}

\section{Results}

\subsection{Temperature Effects}

Figure \ref{fig:temp} shows the alignment scores across temperatures.

\begin{figure}[H]  % [H] forces placement here (requires float package)
    \centering
    \includegraphics[width=0.8\textwidth]{figures/temperature_effects.png}
    \caption{Mean alignment scores across temperature range (0.0-1.0) for each model. Error bars represent standard error of the mean.}
    \label{fig:temp}
\end{figure}

\subsection{Framing Effects}

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{figures/framing_effects.png}
    \caption{Framing effects on alignment scores. The safety-first framing consistently yields higher alignment than neutral or freedom-first framings.}
    \label{fig:framing}
\end{figure}

\end{document}
```

### 4. Important LaTeX Commands

**Basic inclusion:**
```latex
\includegraphics{figures/filename.png}
```

**With sizing:**
```latex
\includegraphics[width=0.8\textwidth]{figures/filename.png}  % 80% of text width
\includegraphics[height=5cm]{figures/filename.png}           % Fixed height
\includegraphics[scale=0.8]{figures/filename.png}            % Scale factor
```

**Best practices:**
- Use `width=\textwidth` or `width=0.8\textwidth` for most figures
- Use `height=` only when you need specific vertical sizing
- `scale=` multiplies both dimensions proportionally

### 5. Create Multiple Subfigures

For side-by-side or grid layouts:

```latex
\usepackage{subcaption}  % Required for subfigure environments

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth]{figures/model_a.png}
        \caption{Model A}
        \label{fig:model_a}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth]{figures/model_b.png}
        \caption{Model B}
        \label{fig:model_b}
    \end{subfigure}
    \caption{Comparison of two models across scenarios}
    \label{fig:models}
\end{figure}
```

## arXiv-Specific Requirements

### File Names

arXiv accepts only these characters in file names:
```
a-z A-Z 0-9 _ + - . , =
```

**Do NOT use:**
- Spaces
- Question marks (?)
- Asterisks (*)
- Special characters (#, @, %, etc.)

**Good examples:**
- `temperature_effects.png` ✅
- `fig1-framing.png` ✅
- `judge_agreement_v2.png` ✅

**Bad examples:**
- `temperature effects.png` ❌ (space)
- `fig1/framing.png` ❌ (slash)
- `plot@temp.png` ❌ (special character)

### Case Sensitivity

**Important:** arXiv's file system is **case sensitive**. 

- `Figure1.png` and `figure1.png` are **different files**
- Ensure LaTeX `\includegraphics` paths match file names exactly
- Test on a case-sensitive system (Linux/Mac) before submitting

### Directory Structure

When uploading to arXiv:
- Upload your entire directory structure (with `figures/` folder)
- Or upload as a `.tar.gz` or `.zip` file containing all files
- arXiv will preserve the directory structure

**Example upload structure:**
```
paper.tar.gz
├── main.tex
├── references.bib
├── figures/
│   ├── temp_effects.png
│   └── framing_effects.png
```

### Compiler Selection

In arXiv submission:
1. **Select PDFLaTeX** as your compiler (not regular LaTeX)
2. This enables PNG/JPEG support
3. arXiv will auto-detect, but verify it's correct

## Common Issues and Solutions

### Issue 1: "File not found" error

**Cause:** Path mismatch or case sensitivity

**Solution:**
```latex
% Check exact path and case
\includegraphics{figures/Temperature_Effects.png}  % Case must match exactly
```

### Issue 2: Figures don't appear

**Cause:** Missing `\usepackage{graphicx}`

**Solution:**
```latex
\documentclass{article}
\usepackage{graphicx}  % Must include this
```

### Issue 3: Figure placement issues

**Cause:** LaTeX floating behavior

**Solution:**
```latex
\usepackage{float}  % Add this package

\begin{figure}[H]  % [H] forces exact placement
    ...
\end{figure}
```

### Issue 4: Figures too large/small

**Cause:** Wrong scaling

**Solution:**
```latex
% Use relative sizing
\includegraphics[width=0.8\textwidth]{figures/plot.png}  % 80% of page width
\includegraphics[width=6cm]{figures/plot.png}            % Fixed 6cm width
```

## Complete Example Template

```latex
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{float}
\usepackage{subcaption}
\usepackage{booktabs}  % For nice tables

\title{Phase 1 Analysis: Local Model Moral Reasoning Evaluation}
\author{Your Name}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
Your abstract here...
\end{abstract}

\section{Introduction}
...

\section{Temperature Effects}

Figure \ref{fig:temperature} shows the alignment scores across the full temperature range.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{figures/temperature_effects.png}
    \caption{Mean alignment scores by temperature for each model. Error bars represent SEM.}
    \label{fig:temperature}
\end{figure}

Our analysis reveals modest temperature effects (range: 0.15-0.23 points)...

\section{Framing Effects}

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.49\textwidth}
        \centering
        \includegraphics[width=\textwidth]{figures/framing_by_temp.png}
        \caption{By temperature}
        \label{fig:framing_temp}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.49\textwidth}
        \centering
        \includegraphics[width=\textwidth]{figures/framing_spread.png}
        \caption{Framing spread}
        \label{fig:framing_spread}
    \end{subfigure}
    \caption{Framing effects on alignment scores. (a) Alignment by framing and temperature. (b) Largest framing separation per model.}
    \label{fig:framing}
\end{figure}

\section{Conclusions}
...

\bibliography{references}

\end{document}
```

## Checklist Before Submission

- [ ] All PNG files saved with descriptive names (no spaces/special chars)
- [ ] File names match exactly in `\includegraphics{}` commands (case-sensitive)
- [ ] `\usepackage{graphicx}` included in preamble
- [ ] PDFLaTeX compiler selected (not regular LaTeX)
- [ ] Figures directory included in upload
- [ ] Test compilation locally before submitting
- [ ] All figures have captions and labels
- [ ] References to figures use `\ref{fig:label}`

## Exporting from Your Notebook

Since you're using Plotly in your Jupyter notebook, here's how to export:

```python
# Method 1: Use plotly's write_image (requires kaleido)
fig.write_image('figures/temperature_effects.png', 
                width=1200, height=800, scale=2)

# Method 2: Convert to matplotlib first
import plotly.graph_objects as go
from plotly.io import to_image

img_bytes = to_image(fig, format="png", width=1200, height=800)
with open('figures/temperature_effects.png', 'wb') as f:
    f.write(img_bytes)

# Method 3: Use plotly's static image export
fig.show(renderer='png')  # Then save from browser
```

## References

- [arXiv Submission Guidelines](https://info.arxiv.org/help/submit/index.html)
- [arXiv Figure Formats](https://info.arxiv.org/help/submit/index.html#formats-figures)
- [LaTeX Graphics Guide](https://www.overleaf.com/learn/latex/Inserting_Images)

## Next Steps

1. Export all plots from your notebook as PNG files (300 DPI, proper sizing)
2. Create a `figures/` directory in your LaTeX project
3. Create a LaTeX document with proper `\includegraphics` commands
4. Test compilation locally with PDFLaTeX
5. Upload complete project (including figures/) to arXiv

