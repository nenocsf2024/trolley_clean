#!/usr/bin/env python3
"""
Export plots from Phase 1 analysis notebook for arXiv submission.

This script helps export Plotly figures to PNG format suitable for LaTeX inclusion.

Requirements:
- plotly
- kaleido (for PNG export): pip install kaleido

Usage:
    python scripts/export_plots_for_arxiv.py
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def export_plotly_fig(fig, output_path, width=1200, height=800, scale=2, dpi=300):
    """
    Export a Plotly figure to PNG.
    
    Args:
        fig: Plotly figure object
        output_path: Path to save PNG file
        width: Width in pixels
        height: Height in pixels
        scale: Scale factor (2 = 2x resolution)
        dpi: DPI for output (informational, actual depends on scale)
    """
    try:
        import plotly.graph_objects as go
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export to PNG
        fig.write_image(
            str(output_path),
            width=width,
            height=height,
            scale=scale
        )
        
        print(f"✅ Exported: {output_path} ({width}x{height} at {scale}x scale)")
        return True
        
    except ImportError:
        print("❌ Error: kaleido package not installed.")
        print("   Install with: pip install kaleido")
        return False
    except Exception as e:
        print(f"❌ Error exporting {output_path}: {e}")
        return False


def main():
    """Main export function - customize based on your notebook figures."""
    
    print("=" * 80)
    print("Exporting Plots for arXiv Submission")
    print("=" * 80)
    print()
    
    figures_dir = project_root / "figures" / "arxiv"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Output directory: {figures_dir}")
    print()
    
    # NOTE: You'll need to load your figures from the notebook
    # This is a template - customize based on your actual figure objects
    
    print("To export figures from your notebook:")
    print()
    print("1. Run your notebook cells to generate all Plotly figures")
    print("2. Then run this code in a new notebook cell:")
    print()
    print("```python")
    print("# Export all figures")
    print("from scripts.export_plots_for_arxiv import export_plotly_fig")
    print("from pathlib import Path")
    print()
    print("figures_dir = Path('figures/arxiv')")
    print()
    print("# Example: Export temperature effects figure")
    print("# export_plotly_fig(fig_totals, figures_dir / 'temperature_effects.png')")
    print()
    print("# Export framing effects")
    print("# export_plotly_fig(fig_framing, figures_dir / 'framing_effects.png')")
    print()
    print("# Export judge agreement")
    print("# export_plotly_fig(fig_ag_overall, figures_dir / 'judge_agreement.png')")
    print("```")
    print()
    
    print("Alternatively, use plotly's built-in export:")
    print()
    print("```python")
    print("import plotly.graph_objects as go")
    print("from pathlib import Path")
    print()
    print("figures_dir = Path('figures/arxiv')")
    print("figures_dir.mkdir(parents=True, exist_ok=True)")
    print()
    print("# Export each figure")
    print("fig_totals.write_image(figures_dir / 'temperature_effects.png',")
    print("                        width=1200, height=800, scale=2)")
    print("fig_framing.write_image(figures_dir / 'framing_effects.png',")
    print("                        width=1200, height=800, scale=2)")
    print("# ... etc")
    print("```")
    print()
    
    print("Figure naming conventions for arXiv:")
    print("  ✅ Good: temperature_effects.png, framing_spread.png")
    print("  ❌ Bad:  temperature effects.png, plot@temp.png")
    print()
    print("=" * 80)
    print("See ARXIV_FIGURE_GUIDE.md for complete instructions")
    print("=" * 80)


if __name__ == "__main__":
    main()

