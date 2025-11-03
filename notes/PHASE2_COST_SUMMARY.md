# Phase 2 API Cost Summary

**Status:** ✅ All 5 models verified with official pricing  
**Date:** 2025-01-XX

---

## Current Phase 2 Costs

**6 scenarios × 5 iterations = 30 responses per model**

| Model | Cost (30 calls) |
|-------|----------------|
| GPT-4o-mini | **$0.009** (cheapest) |
| Gemini 2.5 Flash Lite | **$0.029** |
| Mistral Large | **$0.17** |
| Grok 3 | **$0.21** |
| Claude Sonnet 4 | **$0.27** (most expensive) |
| **TOTAL** | **~$0.69** |

---

## Verified Pricing (per million tokens)

### GPT-4o-mini (OpenAI)
- Input: $0.15 per million
- Output: $0.60 per million

### Gemini 2.5 Flash Lite (Google)
- Input: $0.30 per million
- Output: $2.50 per million (includes thinking tokens)

### Mistral Large (Mistral AI)
- Input: $2.00 per million
- Output: $6.00 per million

### Grok 3 (xAI)
- Input: $3.00 per million
- Output: $15.00 per million

### Claude Sonnet 4 (Anthropic)
- Input: $3.00 per million
- Output: $15.00 per million

---

## Expansion Cost Estimates

### Option 1: Add Low Temperatures (6 scenarios)
**150 additional calls** (5 models × 6 scenarios × 5 iterations)

- GPT-4o-mini: **~$0.045**
- Gemini 2.5 Flash Lite: **~$0.145**
- Mistral Large: **~$0.85**
- Grok 3: **~$1.05**
- Claude Sonnet 4: **~$1.35**
- **Total: ~$3.42**

### Option 2: Full Expansion (30 scenarios)
**1,500 total calls** (5 models × 30 scenarios × 10 iterations)

- GPT-4o-mini: **~$0.45**
- Gemini 2.5 Flash Lite: **~$1.45**
- Mistral Large: **~$8.50**
- Grok 3: **~$10.50**
- Claude Sonnet 4: **~$13.50**
- **Total: ~$34.40**

---

## Key Insights

1. **Current Phase 2 is very affordable:** Only ~$0.69 for all 5 models
2. **GPT-4o-mini is the cheapest:** 30x cheaper than Claude Sonnet 4
3. **Claude Sonnet 4 is most expensive:** But still reasonable at ~$0.27 for 30 calls
4. **Low-temperature expansion is cost-effective:** Only ~$3.42 to add 150 calls
5. **Full expansion requires budget:** ~$34.40 for complete parity with Phase 1

---

## Notes

- Input tokens estimated at 800 per call (system prompt ~200 + user prompt ~600)
- Output tokens measured from actual Phase 2 responses
- All pricing verified from official provider sources
- Costs may vary based on actual token usage and free tier credits

---

**Detailed pricing information:** See `PHASE2_API_PRICING.md`

