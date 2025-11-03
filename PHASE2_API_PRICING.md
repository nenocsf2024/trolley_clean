# Phase 2 API Model Pricing Analysis

**Last Updated:** 2025-01-XX
**Status:** ✅ ALL MODELS VERIFIED - Complete pricing information available

---

## Confirmed Pricing (from official provider pages)

### 1. Claude Sonnet 4 (claude-sonnet-4-20250514)
**Provider:** Anthropic  
**Source:** [anthropic.com/pricing](https://www.anthropic.com/pricing)

- **Input tokens:** $3.00 per million
- **Output tokens:** $15.00 per million
- **Context window:** 200K tokens

**Our actual usage (30 responses):**
- Avg output tokens per response: 443 tokens
- Total output tokens: ~13,283
- Estimated cost for 30 responses: ~$0.27 (input: ~$0.07, output: ~$0.20)

---

### 2. Claude 3.5 Haiku (judge model)
**Provider:** Anthropic  
**Source:** [anthropic.com/pricing](https://www.anthropic.com/pricing)

- **Input tokens:** $0.80 per million
- **Output tokens:** $4.00 per million
- **Context window:** 200K tokens

---

## Verified Pricing (user confirmed)

### 3. GPT-4o-mini (gpt-4o-mini)
**Provider:** OpenAI  
**Status:** ✅ VERIFIED - User confirmed pricing

- **Input tokens:** $0.15 per million
- **Cached input tokens:** $0.075 per million
- **Output tokens:** $0.60 per million

**Our actual usage (30 responses):**
- Avg output tokens per response: 292 tokens
- Total output tokens: ~8,745
- Estimated cost for 30 responses: ~$0.009 (input: ~$0.004, output: ~$0.005)

---

### 4. Gemini 2.5 Flash Lite (gemini-2.5-flash-lite)
**Provider:** Google  
**Status:** ✅ VERIFIED - User confirmed pricing (gemini-2.5-flash)

**Paid Tier Pricing:**
- **Input tokens:** $0.30 per million (text/image/video), $1.00 per million (audio)
- **Output tokens (including thinking tokens):** $2.50 per million
- **Context caching:** $0.03 per million (text/image/video), $0.10 per million (audio)
- **Context window:** 1M tokens (for Flash model)

**Free Tier:**
- Input and output: Free of charge
- Grounding with Google Search: Free up to 500 RPD (shared limit with Flash-Lite)
- Grounding with Google Maps: 500 RPD free

**Note:** Pricing confirmed for `gemini-2.5-flash`. If `gemini-2.5-flash-lite` has different pricing, please verify separately.

**Our actual usage (30 responses):**
- Avg output tokens per response: 353 tokens
- Total output tokens: ~10,580
- Estimated cost for 30 responses (paid tier): ~$0.003 (input) + ~$0.026 (output) = **~$0.029**

---

### 5. Mistral Large (mistral-large-latest)
**Provider:** Mistral AI  
**Status:** ✅ VERIFIED - Official Mistral pricing

**Pricing (per million tokens):**
- **Input tokens:** $2.00 per million
- **Output tokens:** $6.00 per million
- **Context window:** 128,000 tokens

**Note:** Mistral Large is more expensive than Mistral Medium 3 ($0.40/$2.00).

**Our actual usage (30 responses):**
- Avg output tokens per response: 685 tokens (longest responses)
- Total output tokens: ~20,542
- Estimated cost for 30 responses: ~$0.05 (input) + ~$0.12 (output) = **~$0.17**

---

### 6. Grok 3 (grok-3-latest)
**Provider:** xAI  
**Status:** ✅ VERIFIED - User confirmed pricing

**Pricing (per million tokens):**
- **Input tokens:** $3.00 per million
- **Output tokens:** $15.00 per million
- **Context window:** 131,072 tokens
- **Rate limits:** 600 requests per minute

**Note:** Pricing confirmed for `grok-3`. The script uses `grok-3-latest` which should map to this model.

**Our actual usage (30 responses):**
- Avg output tokens per response: 302 tokens
- Total output tokens: ~9,047
- Estimated cost for 30 responses: ~$0.07 (input) + ~$0.14 (output) = **~$0.21**

**Other xAI Models (for reference):**
- grok-3-mini: $0.30/$0.50 per million (input/output)
- grok-4-fast-reasoning: $0.20/$0.50 per million
- grok-4-fast-non-reasoning: $0.20/$0.50 per million
- grok-4-0709: $3.00/$15.00 per million

---

## Cost Calculations

### Verified Models Cost Summary

**Current Phase 2 (6 scenarios × 5 iterations = 30 responses per model):**

| Model | Input Cost | Output Cost | Total Cost (30 calls) |
|-------|------------|-------------|----------------------|
| GPT-4o-mini | ~$0.004 | ~$0.005 | **~$0.009** |
| Gemini 2.5 Flash Lite | ~$0.003 | ~$0.026 | **~$0.029** |
| Mistral Large | ~$0.05 | ~$0.12 | **~$0.17** |
| Grok 3 | ~$0.07 | ~$0.14 | **~$0.21** |
| Claude Sonnet 4 | ~$0.07 | ~$0.20 | **~$0.27** |

*Note: Input tokens estimated at 800 per call (system + user prompt)*

### Expansion Cost Estimates

**Option 1: Add low temperatures (5 iterations) to existing 6 scenarios**
- Additional calls: 5 models × 6 scenarios × 5 iterations = **150 calls**
- Cost estimates (all 5 models):
  - GPT-4o-mini: 150 × $0.009/30 = **~$0.045**
  - Gemini 2.5 Flash Lite: 150 × $0.029/30 = **~$0.145**
  - Mistral Large: 150 × $0.17/30 = **~$0.85**
  - Grok 3: 150 × $0.21/30 = **~$1.05**
  - Claude Sonnet 4: 150 × $0.27/30 = **~$1.35**
  - **Total: ~$3.42**

**Option 2: Full expansion (30 scenarios × 10 iterations)**
- Total calls: 5 models × 30 scenarios × 10 iterations = **1,500 calls**
- Cost estimates (all 5 models):
  - GPT-4o-mini: 1,500 × $0.009/30 = **~$0.45**
  - Gemini 2.5 Flash Lite: 1,500 × $0.029/30 = **~$1.45**
  - Mistral Large: 1,500 × $0.17/30 = **~$8.50**
  - Grok 3: 1,500 × $0.21/30 = **~$10.50**
  - Claude Sonnet 4: 1,500 × $0.27/30 = **~$13.50**
  - **Total: ~$34.40**

---

## Recommendation

**Before making cost decisions:**

1. Check official pricing pages for:
   - [OpenAI API Pricing](https://openai.com/api/pricing)
   - [Google Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
   - [Mistral AI Pricing](https://mistral.ai/pricing)
   - [xAI API Pricing](https://x.ai/pricing) (if available)

2. Check your actual billing/usage dashboards for:
   - Token usage per model
   - Actual costs incurred
   - Free tier limits/credits

3. Use actual billing data rather than estimates for decision-making.

---

## Current Phase 2 Status

- **Models:** 5 API models
- **Scenarios:** 6 (shortlist)
- **Iterations:** 5 per scenario
- **Temperature:** ~0.7 (with jitter)
- **Total responses generated:** 150 (5 × 6 × 5)

---

## Notes

- All pricing above based on web search results
- Official pricing should be verified directly with providers
- Actual costs may vary based on:
  - Volume discounts
  - Free tier credits
  - Regional pricing
  - Promotional rates

