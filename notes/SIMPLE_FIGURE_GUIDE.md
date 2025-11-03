# Simple Guide: Adding Plots to Your Paper

## The Easy Way (3 Steps)

### Step 1: Save Your Plots as PNG

In your Jupyter notebook, after creating each plot, add this code:

```python
# Example: Save the temperature effects plot
fig_totals.write_image('figures/temp_effects.png', width=1000, height=600)

# Example: Save the framing effects plot  
fig_framing.write_image('figures/framing_effects.png', width=1000, height=600)
```

**Important:** Name files with NO spaces:
- ✅ `temp_effects.png`
- ❌ `temp effects.png`

### Step 2: Add to Your LaTeX Paper

Copy-paste this into your LaTeX document:

```latex
% At the top with other packages
\usepackage{graphicx}

% Where you want the figure to appear in your paper
\begin{figure}
    \centering
    \includegraphics[width=0.8\textwidth]{figures/temp_effects.png}
    \caption{Your figure caption goes here}
    \label{fig:temp}
\end{figure}
```

Change `temp_effects.png` to your actual file name.

### Step 3: When Submitting to arXiv

1. Select **PDFLaTeX** as your compiler (not regular LaTeX)
2. Upload your `figures/` folder along with your `.tex` file
3. That's it!

## Quick Reference

**Save plot:**
```python
fig.write_image('figures/your_filename.png', width=1000, height=600)
```

**Add to LaTeX:**
```latex
\includegraphics[width=0.8\textwidth]{figures/your_filename.png}
```

**Change size:** Change `0.8\textwidth` to:
- `\textwidth` = full width
- `0.6\textwidth` = 60% width
- `10cm` = 10 centimeters

## That's It!

You don't need to read the long guide unless you run into problems. This simple approach works for 99% of cases.

