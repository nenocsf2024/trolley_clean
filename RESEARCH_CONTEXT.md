# Research Context: Follow-up to Anthropic/Thinking Machines Paper

## Original Paper: "Stress-Testing Model Specs Reveals Character Differences Among Language Models"

### Key Methodology (Original Study)
1. **Scale**: Generated 300,000+ value tradeoff scenarios
2. **Value Taxonomy**: Used 3,307 fine-grained values from real-world Claude interactions
3. **Models**: Tested 12 frontier LLMs (Claude, GPT, Gemini, Grok families)
4. **Evaluation**: Value classification scoring (0-6 scale) to measure disagreement
5. **Key Metric**: Disagreement = standard deviation of value classification scores across models

### Key Findings (Original Study)
1. **High disagreement predicts spec violations**: 5-13× higher violation rates in high-disagreement scenarios
2. **Specifications lack granularity**: Cannot distinguish between optimal/suboptimal responses
3. **Interpretive ambiguities**: Judge models (used for compliance checking) disagree 70% of the time
4. **Value prioritization patterns**: Clear separation by provider:
   - Claude → Ethical responsibility, intellectual integrity
   - Gemini → Emotional depth
   - OpenAI → Efficiency, technical excellence
5. **False positive refusals**: Identified through cross-model disagreement analysis

## Our Follow-up Study: Differences & Opportunities

### Our Approach
1. **Focused Dataset**: 30 curated moral dilemmas (moral_core_21_sample.jsonl)
   - More targeted than 300K+ scenarios
   - Allows deeper per-scenario analysis
   - Represents real-world ethical tradeoffs

2. **Dual Phase Design**:
   - **Phase 1**: 5 local models via Ollama (4-8B parameters)
   - **Phase 2**: 5 API-based models (frontier LLMs)
   - **Enables comparison**: Local vs cloud, smaller vs larger models

3. **Multi-iteration Design**: 5 iterations per scenario with varied temperatures
   - Tests consistency within models
   - Measures temperature effects on value preferences
   - Identifies intra-model disagreement

4. **Dual Judge System**: GPT-4o-mini + Claude 3.5 Haiku
   - Measures judge agreement/disagreement
   - Reveals interpretive differences in evaluation

### Unique Insights We Can Provide

1. **Local vs Cloud Model Comparison**
   - Do smaller local models (4-8B) show different value patterns than frontier models?
   - Are there systematic differences in how local vs API models handle moral dilemmas?

2. **Intra-Model Consistency Analysis**
   - How stable are value preferences across iterations?
   - Do temperature variations cause significant shifts in alignment scores?
   - Which scenarios elicit the most variability within a single model?

3. **Judge Agreement Patterns**
   - Do GPT-4o-mini and Claude 3.5 Haiku agree on responses?
   - Where do judges disagree, and what does this reveal?
   - Judge disagreement as a signal of ambiguous responses

4. **Scenario-Specific Deep Dives**
   - With only 30 scenarios, we can provide detailed qualitative analysis per scenario
   - Identify which specific moral tradeoffs cause most disagreement
   - Map scenarios to value pairs and analyze patterns

5. **Provider-Level Value Patterns**
   - Compare Ollama (local) provider patterns vs cloud providers
   - Test whether smaller models exhibit similar provider-level patterns as found in original study

6. **Alignment Score Distribution Analysis**
   - How do alignment scores correlate with disagreement?
   - Are high-disagreement scenarios also low-alignment scenarios?
   - Score distributions across scenarios, models, and iterations

## EDA Enhancements Needed

Based on the original paper's methodology and our unique design, we should add:

### 1. Disagreement Metrics (Following Original Study)
- **Cross-model disagreement**: Standard deviation of alignment scores across models
- **Intra-model disagreement**: Standard deviation across iterations for same model
- **Judge disagreement**: Agreement between GPT-4o-mini and Claude 3.5 Haiku judges

### 2. Value Preference Analysis (Enhanced)
- **Provider-level patterns**: Compare Ollama vs cloud provider value preferences
- **Model-level patterns**: Identify outliers and consistent preferences
- **Scenario-level patterns**: Which scenarios cause most disagreement

### 3. Alignment Score Deep Dive
- Distribution by model, scenario, value pair
- Correlation between disagreement and alignment scores
- Temperature effects on alignment

### 4. Judge Analysis
- Inter-judge agreement (Cohen's Kappa, correlation)
- Scenarios where judges disagree most
- Judge bias patterns

### 5. Iteration/Temperature Effects
- Stability metrics: How consistent are responses?
- Temperature sensitivity: Which models/scenarios are most affected?
- Variance analysis across iterations

## Research Questions to Address

1. **Do smaller local models replicate value prioritization patterns seen in frontier models?**
2. **How consistent are model responses across temperature variations?**
3. **Do dual judges provide more reliable evaluation than single-judge systems?**
4. **Which specific moral dilemmas cause the most disagreement, and why?**
5. **Are high-disagreement scenarios correlated with low alignment scores?**
6. **Can we predict alignment scores from response characteristics?**

## Next Steps

Once all judging is complete:
1. Run enhanced EDA with disagreement metrics
2. Generate provider-level and model-level comparison plots
3. Analyze judge agreement patterns
4. Perform scenario-specific deep dives
5. Compare our findings to original paper's conclusions


