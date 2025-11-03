#!/usr/bin/env python3
"""
Isolated test of Mistral API free tier behavior.

Tests:
1. API connectivity
2. Rate limits (free tier)
3. Request success/failure patterns
4. Appropriate delays needed
5. Error handling

Run before large-scale operations to verify free tier compatibility.
"""

import os
import time
import sys
from pathlib import Path
from typing import Dict, Any
import requests
from datetime import datetime


def load_env_from_dotenv(dotenv_path: Path) -> None:
    """Load environment variables from .env file."""
    if not dotenv_path.exists():
        return
    with dotenv_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()


def test_mistral_api_call(prompt: str, model: str = "mistral-large-latest", delay: float = 0.5) -> Dict[str, Any]:
    """Test a single Mistral API call."""
    url = "https://api.mistral.ai/v1/chat/completions"
    api_key = os.environ.get("MISTRAL_API_KEY")
    
    if not api_key:
        return {
            "success": False,
            "error": "MISTRAL_API_KEY not found in environment",
            "status_code": None,
        }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 100,
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    start_time = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        result = {
            "success": resp.status_code == 200,
            "status_code": resp.status_code,
            "response_time": elapsed,
            "headers": dict(resp.headers),
        }
        
        if resp.status_code == 200:
            data = resp.json()
            result["tokens"] = data.get("usage", {})
            result["content_length"] = len(data.get("choices", [{}])[0].get("message", {}).get("content", ""))
        elif resp.status_code == 429:
            result["error"] = "Rate limit exceeded"
            result["retry_after"] = resp.headers.get("Retry-After")
        else:
            try:
                result["error"] = resp.json().get("error", {}).get("message", resp.text[:200])
            except:
                result["error"] = resp.text[:200]
        
        time.sleep(delay)  # Respect rate limits
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout (>30s)",
            "status_code": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": None,
        }
    
    return result


def main():
    """Run isolated Mistral API tests."""
    base_dir = Path(__file__).resolve().parent.parent
    load_env_from_dotenv(base_dir / ".env")
    
    print("=" * 70)
    print("MISTRAL FREE TIER BEHAVIOR TEST")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("❌ ERROR: MISTRAL_API_KEY not found")
        print("   Set it in .env file or environment variable")
        return 1
    
    print(f"✓ API key found: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    # Test 1: Single call
    print("TEST 1: Single API call")
    print("-" * 70)
    result1 = test_mistral_api_call("Say 'test' if you can read this.", delay=0)
    print(f"Status: {result1.get('status_code', 'N/A')}")
    print(f"Success: {result1.get('success', False)}")
    if result1.get('success'):
        print(f"Response time: {result1.get('response_time', 0):.2f}s")
        print(f"Tokens used: {result1.get('tokens', {})}")
    else:
        print(f"Error: {result1.get('error', 'Unknown')}")
        if result1.get('status_code') == 429:
            print(f"  Retry-After: {result1.get('retry_after', 'N/A')}")
    print()
    
    # Test 2: Rapid calls (test rate limits)
    print("TEST 2: Rapid consecutive calls (testing rate limits)")
    print("-" * 70)
    rapid_results = []
    delays_tested = [0.5, 1.0, 2.0]
    
    for delay in delays_tested:
        print(f"\nTesting with {delay}s delay between calls:")
        results = []
        for i in range(5):
            print(f"  Call {i+1}/5...", end=" ", flush=True)
            result = test_mistral_api_call(f"Test call {i+1}. Respond with 'OK'.", delay=delay)
            results.append(result)
            if result.get('success'):
                print(f"✓ ({result.get('response_time', 0):.2f}s)")
            elif result.get('status_code') == 429:
                print(f"✗ Rate limited (429)")
                break
            else:
                print(f"✗ {result.get('error', 'Error')}")
        
        success_count = sum(1 for r in results if r.get('success'))
        rate_limit_count = sum(1 for r in results if r.get('status_code') == 429)
        
        print(f"  Summary: {success_count}/5 successful, {rate_limit_count} rate limited")
        
        if rate_limit_count > 0:
            print(f"  ⚠️  {delay}s delay is TOO FAST for free tier")
        elif success_count == 5:
            print(f"  ✓ {delay}s delay appears safe")
        
        rapid_results.append((delay, results))
        
        # Wait before next delay test
        if delay < delays_tested[-1]:
            print(f"\n  Waiting 10s before next test...")
            time.sleep(10)
    
    print()
    
    # Test 3: Check rate limit headers
    print("TEST 3: Rate limit information")
    print("-" * 70)
    if result1.get('success'):
        headers = result1.get('headers', {})
        print(f"Rate limit headers from API:")
        for key in ['x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset']:
            value = headers.get(key) or headers.get(key.replace('-', '_'))
            if value:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: Not provided")
    print()
    
    # Summary and recommendations
    print("=" * 70)
    print("SUMMARY AND RECOMMENDATIONS")
    print("=" * 70)
    print()
    
    if result1.get('success'):
        print("✓ API is working")
        
        # Analyze rate limits
        safe_delay = None
        for delay, results in rapid_results:
            if all(r.get('success') for r in results):
                safe_delay = delay
                break
        
        if safe_delay:
            print(f"✓ Recommended delay: {safe_delay}s between calls")
            print(f"  This gives ~{60/safe_delay:.0f} requests/minute")
        else:
            print("⚠️  All tested delays triggered rate limits")
            print("  Recommend: Use 10-12s delay (5-6 requests/minute) for safety")
        
    else:
        print("❌ API test failed")
        if result1.get('status_code') == 401:
            print("  → Check API key is valid")
        elif result1.get('status_code') == 429:
            print("  → Rate limited on first call - account may be throttled")
        else:
            print(f"  → Error: {result1.get('error', 'Unknown')}")
        print()
        print("⚠️  Cannot proceed with large-scale operations")
        return 1
    
    print()
    print("Next steps:")
    print("  • If API works: Proceed with commit and low-temp iterations")
    print("  • If rate limits: Adjust delays in run_phase2_api.py")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

