"""
Test script to evaluate GPT-4o-mini's Shona (ChiShona) language capability
for EcoCash Assistant use cases.
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import os
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, List, Tuple
from datetime import datetime

# Load environment variables
load_dotenv()

# Test prompts in Shona
SHONA_TEST_PROMPTS = {
    "basic_greeting": {
        "prompt": "Mhoro",
        "expected": "Should understand greeting and respond appropriately",
        "category": "Basic Communication"
    },
    "basic_help": {
        "prompt": "Ndinoda rubatsiro",
        "expected": "Should understand request for help",
        "category": "Basic Communication"
    },
    "balance_query_simple": {
        "prompt": "Ndinoda kuona mari yangu",
        "expected": "Should understand request to see balance/money",
        "category": "Financial Queries"
    },
    "balance_query_formal": {
        "prompt": "Ndinoda kuona mari yemuhomwe yangu",
        "expected": "Should understand formal request for wallet balance",
        "category": "Financial Queries"
    },
    "transactions_query": {
        "prompt": "Ndinoda kuona zvishandiswa zvangu",
        "expected": "Should understand request to see transactions",
        "category": "Financial Queries"
    },
    "recent_transactions": {
        "prompt": "Ndinoda kuona zvishandiswa zvichangobva",
        "expected": "Should understand request for recent transactions",
        "category": "Financial Queries"
    },
    "transaction_help": {
        "prompt": "Ndinoda rubatsiro nezve chishandiso changu",
        "expected": "Should understand request for transaction help",
        "category": "Complex Requests"
    },
    "transaction_issue": {
        "prompt": "Mari yangu yakabviswa asi mutengesi haana kugamuchira",
        "expected": "Should understand complex issue: money deducted but merchant didn't receive",
        "category": "Complex Requests"
    },
    "transaction_with_merchant": {
        "prompt": "Ndinoda rubatsiro nezve chishandiso changu kuna Coffee Shop",
        "expected": "Should understand request for help with specific merchant transaction",
        "category": "Complex Requests"
    },
    "mixed_language": {
        "prompt": "Mhoro, I need help with my balance",
        "expected": "Should handle mixed Shona-English input",
        "category": "Mixed Language"
    }
}

# System message similar to production
SYSTEM_MESSAGE = """You are the Ecocash Assistant, a helpful and empathetic AI relationship manager for Ecocash fintech services in Zimbabwe.
You help users manage their wallet, view transactions, and resolve issues.

Available capabilities:
- Check wallet balance
- View transaction history
- Get transaction details
- Create support tickets

Respond naturally and helpfully. If the user speaks Shona, you can respond in Shona if you are able to."""


async def test_shona_prompt(
    llm: AzureChatOpenAI,
    test_name: str,
    prompt: str,
    category: str,
    expected: str
) -> Dict:
    """Test a single Shona prompt and evaluate the response."""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Category: {category}")
    print(f"Prompt (Shona): {prompt}")
    print(f"Expected: {expected}")
    print(f"{'='*60}")
    
    try:
        # Test without system message first (basic capability)
        response_basic = await llm.ainvoke([HumanMessage(content=prompt)])
        basic_response_text = response_basic.content
        
        # Test with system message (production-like scenario)
        response_with_system = await llm.ainvoke([
            SystemMessage(content=SYSTEM_MESSAGE),
            HumanMessage(content=prompt)
        ])
        system_response_text = response_with_system.content
        
        # Evaluate responses
        result = {
            "test_name": test_name,
            "category": category,
            "prompt": prompt,
            "expected": expected,
            "basic_response": basic_response_text,
            "system_response": system_response_text,
            "response_language_basic": detect_language(basic_response_text),
            "response_language_system": detect_language(system_response_text),
            "understanding_score": evaluate_understanding(prompt, basic_response_text, system_response_text),
            "quality_score": evaluate_quality(basic_response_text, system_response_text),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n✅ Response (Basic): {basic_response_text[:200]}...")
        print(f"   Language: {result['response_language_basic']}")
        print(f"\n✅ Response (With System): {system_response_text[:200]}...")
        print(f"   Language: {result['response_language_system']}")
        print(f"\n📊 Understanding Score: {result['understanding_score']}/5")
        print(f"📊 Quality Score: {result['quality_score']}/5")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "test_name": test_name,
            "category": category,
            "prompt": prompt,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def detect_language(text: str) -> str:
    """Detect if response is in Shona, English, or Mixed."""
    text_lower = text.lower()
    
    # Common Shona words/phrases
    shona_indicators = [
        "mhoro", "ndinoda", "rubatsiro", "mari", "zvishandiswa", 
        "muhomwe", "chishandiso", "mutengesi", "zvichangobva",
        "ndiri", "ndine", "pane", "zvakaitika", "zvakadaro"
    ]
    
    # Count Shona indicators
    shona_count = sum(1 for word in shona_indicators if word in text_lower)
    
    # Common English words
    english_indicators = [
        "hello", "help", "balance", "transaction", "wallet", "money",
        "can", "will", "should", "please", "thank", "you"
    ]
    english_count = sum(1 for word in english_indicators if word in text_lower)
    
    if shona_count > english_count and shona_count > 2:
        return "Shona"
    elif english_count > shona_count and english_count > 2:
        return "English"
    elif shona_count > 0 and english_count > 0:
        return "Mixed"
    else:
        return "Unknown"


def evaluate_understanding(prompt: str, basic_response: str, system_response: str) -> int:
    """Evaluate if the model understood the Shona prompt (1-5 scale)."""
    score = 0
    
    # Check if response addresses the prompt topic
    prompt_lower = prompt.lower()
    response_lower = (basic_response + " " + system_response).lower()
    
    # Key concepts from prompts
    if "mari" in prompt_lower or "balance" in prompt_lower:
        if "balance" in response_lower or "money" in response_lower or "mari" in response_lower:
            score += 2
    if "zvishandiswa" in prompt_lower or "transaction" in prompt_lower:
        if "transaction" in response_lower or "zvishandiswa" in response_lower:
            score += 2
    if "rubatsiro" in prompt_lower or "help" in prompt_lower:
        if "help" in response_lower or "rubatsiro" in response_lower or "assist" in response_lower:
            score += 2
    
    # If response is relevant and helpful
    if len(response_lower) > 20:  # Not just a generic response
        score += 1
    
    return min(score, 5)


def evaluate_quality(basic_response: str, system_response: str) -> int:
    """Evaluate response quality (1-5 scale)."""
    score = 0
    
    # Check response length (too short might indicate poor understanding)
    if len(basic_response) > 50:
        score += 1
    if len(system_response) > 50:
        score += 1
    
    # Check for helpful content
    helpful_indicators = ["can", "will", "help", "check", "view", "show", "provide"]
    if any(indicator in basic_response.lower() for indicator in helpful_indicators):
        score += 1
    if any(indicator in system_response.lower() for indicator in helpful_indicators):
        score += 1
    
    # Check for coherent response (not just error or generic)
    if "error" not in basic_response.lower() and "sorry" not in basic_response.lower():
        score += 1
    
    return min(score, 5)


async def run_all_tests():
    """Run all Shona language tests."""
    print("="*60)
    print("GPT-4o-mini Shona Language Capability Test")
    print("="*60)
    print(f"\nModel: gpt-4o-mini (Azure OpenAI)")
    print(f"Azure Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT', 'Not set')}")
    print(f"API Key: {'✅ Set' if os.getenv('AZURE_OPENAI_API_KEY') else '❌ Missing'}")
    print(f"Total Tests: {len(SHONA_TEST_PROMPTS)}")
    print("\n" + "="*60)
    
    # Azure OpenAI configuration
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://azureopenai-uswest-sandbox.openai.azure.com/")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    if not azure_api_key:
        print("❌ ERROR: AZURE_OPENAI_API_KEY not found in environment")
        print("   Please set AZURE_OPENAI_API_KEY in your .env file")
        return
    
    # Initialize Azure OpenAI LLM (same as production)
    llm = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        api_key=azure_api_key,
        api_version=azure_api_version,
        temperature=0.7,
        max_tokens=4096,
    )
    
    results = []
    
    # Run all tests
    for test_name, test_data in SHONA_TEST_PROMPTS.items():
        result = await test_shona_prompt(
            llm=llm,
            test_name=test_name,
            prompt=test_data["prompt"],
            category=test_data["category"],
            expected=test_data["expected"]
        )
        results.append(result)
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    # Generate summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    successful_tests = len([r for r in results if "error" not in r])
    avg_understanding = sum([r.get("understanding_score", 0) for r in results if "understanding_score" in r]) / max(successful_tests, 1)
    avg_quality = sum([r.get("quality_score", 0) for r in results if "quality_score" in r]) / max(successful_tests, 1)
    
    # Language distribution
    languages_basic = [r.get("response_language_basic", "Unknown") for r in results if "response_language_basic" in r]
    languages_system = [r.get("response_language_system", "Unknown") for r in results if "response_language_system" in r]
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"\nAverage Understanding Score: {avg_understanding:.2f}/5")
    print(f"Average Quality Score: {avg_quality:.2f}/5")
    print(f"\nResponse Languages (Basic):")
    for lang in set(languages_basic):
        print(f"  - {lang}: {languages_basic.count(lang)}")
    print(f"\nResponse Languages (With System):")
    for lang in set(languages_system):
        print(f"  - {lang}: {languages_system.count(lang)}")
    
    # Save results
    save_results(results)
    
    return results


def save_results(results: List[Dict]):
    """Save test results to markdown file."""
    output_file = "SHONA_TEST_RESULTS.md"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# GPT-4o-mini Shona Language Test Results\n\n")
        f.write(f"**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model**: gpt-4o-mini\n")
        f.write(f"**Total Tests**: {len(results)}\n\n")
        
        # Summary
        successful = [r for r in results if "error" not in r]
        avg_understanding = sum([r.get("understanding_score", 0) for r in successful if "understanding_score" in r]) / max(len(successful), 1)
        avg_quality = sum([r.get("quality_score", 0) for r in successful if "quality_score" in r]) / max(len(successful), 1)
        
        f.write("## Summary\n\n")
        f.write(f"- **Successful Tests**: {len(successful)}/{len(results)}\n")
        f.write(f"- **Average Understanding Score**: {avg_understanding:.2f}/5\n")
        f.write(f"- **Average Quality Score**: {avg_quality:.2f}/5\n\n")
        
        # Detailed results by category
        categories = {}
        for result in results:
            cat = result.get("category", "Unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        for category, cat_results in categories.items():
            f.write(f"## {category}\n\n")
            
            for result in cat_results:
                f.write(f"### {result.get('test_name', 'Unknown')}\n\n")
                f.write(f"**Prompt (Shona)**: `{result.get('prompt', 'N/A')}`\n\n")
                f.write(f"**Expected**: {result.get('expected', 'N/A')}\n\n")
                
                if "error" in result:
                    f.write(f"**❌ Error**: {result['error']}\n\n")
                else:
                    f.write(f"**Response (Basic)**:\n")
                    f.write(f"```\n{result.get('basic_response', 'N/A')}\n```\n\n")
                    f.write(f"**Response (With System)**:\n")
                    f.write(f"```\n{result.get('system_response', 'N/A')}\n```\n\n")
                    f.write(f"**Language (Basic)**: {result.get('response_language_basic', 'Unknown')}\n\n")
                    f.write(f"**Language (System)**: {result.get('response_language_system', 'Unknown')}\n\n")
                    f.write(f"**Understanding Score**: {result.get('understanding_score', 0)}/5\n\n")
                    f.write(f"**Quality Score**: {result.get('quality_score', 0)}/5\n\n")
                
                f.write("---\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        
        if avg_understanding >= 4:
            f.write("✅ **GPT-4o-mini shows good understanding of Shona prompts**\n\n")
        elif avg_understanding >= 3:
            f.write("⚠️ **GPT-4o-mini shows moderate understanding of Shona prompts**\n\n")
        else:
            f.write("❌ **GPT-4o-mini shows limited understanding of Shona prompts**\n\n")
        
        shona_responses = [r for r in successful if r.get("response_language_system") == "Shona"]
        if len(shona_responses) > len(successful) * 0.5:
            f.write("✅ **Model can respond in Shona** - Consider implementing Shona language support\n\n")
        elif len(shona_responses) > 0:
            f.write("⚠️ **Model sometimes responds in Shona** - May need prompting to encourage Shona responses\n\n")
        else:
            f.write("❌ **Model primarily responds in English** - May need frontend translation instead\n\n")
        
        f.write("### Implementation Options\n\n")
        f.write("1. **If understanding is good (≥4)**: Implement Shona language support with LLM responding in Shona\n")
        f.write("2. **If understanding is moderate (3-4)**: Use frontend translations + prompt LLM to respond in Shona\n")
        f.write("3. **If understanding is poor (<3)**: Use frontend-only translations, keep LLM in English\n\n")
    
    print(f"\n✅ Results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

