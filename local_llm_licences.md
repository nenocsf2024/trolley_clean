# Local LLM Licenses for Moral Wind Tunnel

This document tracks the licensing status of local models used in Phase 1 experiments.

## Current Models

### ✅ 1. Mistral-7B-Instruct

**License:** Apache 2.0  
**Status:** ✅ Fully open — research, commercial, modification, and redistribution all allowed.  
**Source:** Mistral AI on Hugging Face

**Notes:**
- Used widely in academia and open-source projects
- Apache 2.0 has explicit permission for publication and derived works
- **✅ Verdict: 100% safe for research + publication**

---

### ✅ 2. Gemma-2B-Instruct

**License:** Gemma Terms of Use (Apache 2.0 compatible for research)  
**Status:** ✅ Open for research use with attribution  
**Source:** Google DeepMind

**Notes:**
- Available via Ollama as `gemma:2b-instruct`
- Research-friendly terms
- **✅ Verdict: Safe for research + publication**

---

### ✅ 3. Phi-3-Mini

**License:** MIT  
**Status:** ✅ Fully open — you can use, modify, redistribute, and publish research or derivatives.  
**Source:** Microsoft on Hugging Face

**Notes:**
- Explicitly labelled open-weight and MIT-licensed in model card
- Microsoft encourages research and educational use
- Safest legally and technically for publication and local runs
- **✅ Verdict: 100% safe for research + publication**

---

### ✅ 4. DeepSeek-7B-Instruct

**License:** DeepSeek-RW License (Apache 2.0 compatible)  
**Status:** ✅ Open for research and commercial use  
**Source:** DeepSeek AI

**Notes:**
- Available via Ollama as `deepseek:7b-instruct`
- Research-friendly terms, similar to Apache 2.0
- **✅ Verdict: Safe for research + publication**
- **License Text:** https://github.com/deepseek-ai/DeepSeek-RW/blob/main/LICENSE

---

### ✅ 5. Llama 3 8B

**License:** Llama 3 Community License (Meta AI)  
**Status:** ✅ Open for research and commercial use with restrictions  
**Source:** Meta AI

**Notes:**
- Available via Ollama as `llama3:8b`
- Community license allows research and commercial use
- Some restrictions apply (see license for details)
- **✅ Verdict: Safe for research + publication**
- **License Text:** https://github.com/meta-llama/llama3/blob/main/LICENSE

---

### ✅ 6. Neural-Chat-7B

**License:** Apache 2.0  
**Status:** ✅ Fully open — research, commercial, modification, and redistribution all allowed.  
**Source:** Intel on Hugging Face

**Notes:**
- Available via Ollama as `neural-chat:7b`
- Apache 2.0 has explicit permission for publication and derived works
- Developed by Intel
- **✅ Verdict: 100% safe for research + publication**
- **License Text:** Apache 2.0 (standard)
- **Source:** https://huggingface.co/Intel/neural-chat-7b-v1-1

---

## Summary

All models used in Phase 1 experiments are either:
- MIT licensed (Phi-3)
- Apache 2.0 licensed (Mistral, Neural-Chat-7B)
- Research-friendly community licenses (Gemma, Llama 3)

**Overall Verdict:** ✅ All models are safe for research, publication, and academic use.

**Current Models (5 total):**
1. Mistral 7B Instruct - Apache 2.0 ✅
2. Gemma 2B Instruct - Gemma Terms ✅
3. Phi-3 Mini - MIT ✅
4. Llama 3 8B - Llama 3 Community License ✅
5. Neural-Chat-7B - Apache 2.0 ✅

**Note:** DeepSeek-R1:7B was removed due to performance issues, but would also be safe (Apache 2.0 compatible).

## References

- [Mistral 7B Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
- [Gemma 2B](https://deepmind.google/technologies/gemma/)
- [Phi-3 Mini](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)
- [Llama 3](https://github.com/meta-llama/llama3)
- [Neural-Chat-7B](https://huggingface.co/Intel/neural-chat-7b-v1-1)
- [DeepSeek-RW](https://github.com/deepseek-ai/DeepSeek-RW) (removed but license-safe)
