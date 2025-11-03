
# Export All Plots for Word Document
from pathlib import Path
import plotly.graph_objects as go

# Create figures directory
figures_dir = Path("figures/word_report")
figures_dir.mkdir(parents=True, exist_ok=True)

print("Exporting plots...")

# Cell 1: Visual EDA plots
if 'fig_totals' in globals():
    fig_totals.write_image(figures_dir / "01_model_totals.png", width=800, height=500)
    print("✅ Exported: 01_model_totals.png")

if 'fig_iters' in globals():
    fig_iters.write_image(figures_dir / "02_iteration_coverage.png", width=1000, height=600)
    print("✅ Exported: 02_iteration_coverage.png")

if 'fig_temps' in globals():
    fig_temps.write_image(figures_dir / "03_temperature_coverage.png", width=1000, height=600)
    print("✅ Exported: 03_temperature_coverage.png")

if 'fig_align_overall' in globals():
    fig_align_overall.write_image(figures_dir / "04_alignment_distribution.png", width=800, height=500)
    print("✅ Exported: 04_alignment_distribution.png")

if 'fig_align_by_model' in globals():
    fig_align_by_model.write_image(figures_dir / "05_alignment_by_model.png", width=800, height=500)
    print("✅ Exported: 05_alignment_by_model.png")

# Cell 3: Temperature Effects
if 'fig_temp_lines' in globals():
    fig_temp_lines.write_image(figures_dir / "06_temperature_effects.png", width=1000, height=600)
    print("✅ Exported: 06_temperature_effects.png")

if 'fig_lowhigh' in globals():
    fig_lowhigh.write_image(figures_dir / "07_low_vs_high_temp.png", width=800, height=500)
    print("✅ Exported: 07_low_vs_high_temp.png")

# Cell 7-8: Judge Agreement
if 'fig_ag_overall' in globals():
    fig_ag_overall.write_image(figures_dir / "08_judge_agreement_overall.png", width=800, height=500)
    print("✅ Exported: 08_judge_agreement_overall.png")

if 'fig_ag_temp' in globals():
    fig_ag_temp.write_image(figures_dir / "09_judge_agreement_by_temp.png", width=1200, height=700)
    print("✅ Exported: 09_judge_agreement_by_temp.png")

# Cell 13: Pairwise Agreement
if 'fig_pair_heatmap' in globals():
    fig_pair_heatmap.write_image(figures_dir / "10_pairwise_agreement_heatmap.png", width=800, height=600)
    print("✅ Exported: 10_pairwise_agreement_heatmap.png")

if 'fig_pair_temp' in globals():
    fig_pair_temp.write_image(figures_dir / "11_pairwise_agreement_by_temp.png", width=1000, height=600)
    print("✅ Exported: 11_pairwise_agreement_by_temp.png")

# Cell 15: Framing Effects
if 'fig_framing_temp' in globals():
    fig_framing_temp.write_image(figures_dir / "12_framing_effects_by_temp.png", width=1200, height=800)
    print("✅ Exported: 12_framing_effects_by_temp.png")

if 'fig_framing_lowhigh' in globals():
    fig_framing_lowhigh.write_image(figures_dir / "13_framing_low_vs_high.png", width=1000, height=600)
    print("✅ Exported: 13_framing_low_vs_high.png")

# Cell 25: Intra-model consistency
if 'fig_var_box' in globals():
    fig_var_box.write_image(figures_dir / "14_intra_model_variance.png", width=800, height=500)
    print("✅ Exported: 14_intra_model_variance.png")

if 'fig_var_temp' in globals():
    fig_var_temp.write_image(figures_dir / "15_variance_by_temperature.png", width=800, height=500)
    print("✅ Exported: 15_variance_by_temperature.png")

# Cell 26: Model ranking
if 'fig_rank_heatmap' in globals():
    fig_rank_heatmap.write_image(figures_dir / "16_model_ranking_heatmap.png", width=1000, height=600)
    print("✅ Exported: 16_model_ranking_heatmap.png")

if 'fig_rank_box' in globals():
    fig_rank_box.write_image(figures_dir / "17_model_ranking_distribution.png", width=800, height=500)
    print("✅ Exported: 17_model_ranking_distribution.png")

# Cell 27: Synthesis
if 'fig_synth_scatter' in globals():
    fig_synth_scatter.write_image(figures_dir / "18_problematic_scenarios.png", width=1000, height=700)
    print("✅ Exported: 18_problematic_scenarios.png")

print(f"
✅ All plots exported to: {figures_dir}")
print(f"   Total files: {len(list(figures_dir.glob('*.png')))}")
