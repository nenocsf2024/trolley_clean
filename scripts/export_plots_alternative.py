#!/usr/bin/env python3
"""
Alternative method to export plots: Save as HTML, then user can screenshot or use browser.

This avoids kaleido/Chrome issues.
"""

from pathlib import Path
import json

def create_html_viewer(figures_dir):
    """Create an HTML file that shows all plots for easy screenshotting."""
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Phase 1 Analysis - All Plots</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .plot-container { background: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
    </style>
</head>
<body>
    <h1>Phase 1 Analysis - All Plots</h1>
    <p>Use browser screenshot tool or print to PDF to capture these plots for Word document.</p>
"""
    
    # This will be populated by the notebook cell
    return html_content

def export_as_html(notebook_path, output_html):
    """Create HTML export instructions."""
    
    code = '''
# Alternative: Export plots as HTML (for manual screenshot)
from pathlib import Path
import plotly.graph_objects as go
import plotly.offline as pyo

figures_dir = Path("figures/word_report")
figures_dir.mkdir(parents=True, exist_ok=True)

html_parts = []

# Export each figure as standalone HTML
plots = [
    ('fig_totals', '01_model_totals', 'Per-model response totals'),
    ('fig_iters', '02_iteration_coverage', 'Iteration coverage'),
    ('fig_temps', '03_temperature_coverage', 'Temperature coverage'),
    ('fig_align_overall', '04_alignment_distribution', 'Alignment distribution'),
    ('fig_align_by_model', '05_alignment_by_model', 'Alignment by model'),
    ('fig_mean_sem', '06_temperature_effects', 'Temperature effects'),
    ('fig_lh', '07_low_vs_high_temp', 'Low vs high temperature'),
    ('fig_ag_overall', '08_judge_agreement_overall', 'Judge agreement overall'),
    ('fig_ag_temp', '09_judge_agreement_by_temp', 'Judge agreement by temp'),
    ('fig_hm', '10_pairwise_agreement_heatmap', 'Pairwise agreement heatmap'),
    ('fig_lines', '11_pairwise_agreement_by_temp', 'Pairwise agreement by temp'),
    ('fig_ft', '12_framing_effects_by_temp', 'Framing effects'),
    ('fig_model_var', '14_intra_model_variance', 'Intra-model variance'),
    ('fig_heatmap', '16_model_ranking_heatmap', 'Model ranking'),
]

for var_name, filename, caption in plots:
    if var_name in globals():
        fig = globals()[var_name]
        html_file = figures_dir / f"{filename}.html"
        fig.write_html(str(html_file))
        html_parts.append((filename, caption))
        print(f"✅ Exported HTML: {filename}.html")

# Create index page
index_html = """<!DOCTYPE html>
<html>
<head>
    <title>Phase 1 Plots</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .plot-link { display: block; margin: 10px 0; padding: 10px; background: #f0f0f0; }
    </style>
</head>
<body>
    <h1>Phase 1 Analysis - All Plots</h1>
    <p>Open each plot, take screenshot, and paste into Word.</p>
    <ul>
"""
        
        for filename, caption in html_parts:
            index_html += f'        <li><a href="{filename}.html" target="_blank">{caption}</a></li>\\n'
        
        index_html += """    </ul>
</body>
</html>"""
        
        (figures_dir / "index.html").write_text(index_html)
        print(f"\\n✅ Created index page: {figures_dir / 'index.html'}")
        print("   Open index.html in browser and screenshot each plot")
'''
    
    return code

if __name__ == "__main__":
    print("Alternative export method created.")
    print("See the code above - this exports plots as HTML files")
    print("that you can open in a browser and screenshot.")

