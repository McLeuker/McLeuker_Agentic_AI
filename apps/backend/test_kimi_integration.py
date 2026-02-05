"""
Quick test script for Kimi K2.5 integration
Run this to verify the hybrid brain is working correctly.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import settings
from src.core.kimi_client import kimi_client
from src.core.hybrid_brain import hybrid_brain, TaskType


async def test_kimi_client():
    """Test Kimi client connectivity."""
    print("\n🧪 Testing Kimi Client...")
    print("=" * 60)
    
    if not settings.is_kimi_configured():
        print("❌ Kimi not configured. Please add MOONSHOT_API_KEY to .env")
        return False
    
    try:
        response = await kimi_client.execute(
            query="Say 'Hello from Kimi K2.5!' in one sentence.",
            temperature=0.7
        )
        
        if response.success:
            print(f"✅ Kimi client working!")
            print(f"   Response: {response.content[:100]}...")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Cost: ${response.cost:.6f}")
            return True
        else:
            print(f"❌ Kimi client error: {response.error}")
            return False
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


async def test_hybrid_brain():
    """Test hybrid brain routing."""
    print("\n🧪 Testing Hybrid Brain...")
    print("=" * 60)
    
    test_queries = [
        {
            "query": "What is fashion?",
            "expected_type": TaskType.REASONING,
            "description": "Pure reasoning query"
        },
        {
            "query": "Generate Python code to analyze CSV data",
            "expected_type": TaskType.EXECUTION,
            "description": "Pure execution query"
        },
        {
            "query": "Analyze fashion trends and create a report",
            "expected_type": TaskType.HYBRID,
            "description": "Hybrid query"
        }
    ]
    
    all_passed = True
    
    for test in test_queries:
        print(f"\n📝 Test: {test['description']}")
        print(f"   Query: {test['query']}")
        
        try:
            response = await hybrid_brain.think(
                query=test['query'],
                task_type=test['expected_type']
            )
            
            if response.success:
                print(f"   ✅ Success!")
                print(f"   Models used: {response.models_used}")
                if response.cost > 0:
                    print(f"   Cost: ${response.cost:.6f}")
                print(f"   Response: {response.content[:100]}...")
            else:
                print(f"   ❌ Failed: {response.error}")
                all_passed = False
        
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            all_passed = False
    
    return all_passed


async def test_model_availability():
    """Test model availability."""
    print("\n🔍 Checking Model Availability...")
    print("=" * 60)
    
    models = settings.get_available_models()
    
    for model_name, model_info in models.items():
        status = "✅" if model_info['available'] else "❌"
        print(f"{status} {model_name.upper()}")
        print(f"   Model: {model_info['model']}")
        print(f"   Role: {model_info['role']}")
        print(f"   Available: {model_info['available']}")
    
    print(f"\n🔧 Multi-model ready: {settings.is_multi_model_ready()}")
    print(f"🔧 Hybrid enabled: {settings.ENABLE_MULTI_MODEL}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 McLeuker AI - Kimi K2.5 Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Model availability
    await test_model_availability()
    
    # Test 2: Kimi client
    kimi_ok = await test_kimi_client()
    
    # Test 3: Hybrid brain (only if Kimi is working)
    if kimi_ok:
        hybrid_ok = await test_hybrid_brain()
    else:
        print("\n⚠️  Skipping hybrid brain tests (Kimi not available)")
        hybrid_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Kimi Client: {'✅ PASS' if kimi_ok else '❌ FAIL'}")
    print(f"Hybrid Brain: {'✅ PASS' if hybrid_ok else '❌ FAIL or SKIPPED'}")
    print("\n" + "=" * 60)
    
    if kimi_ok and hybrid_ok:
        print("🎉 All tests passed! Kimi integration is working correctly.")
    elif kimi_ok:
        print("⚠️  Kimi client works, but hybrid brain needs attention.")
    else:
        print("❌ Kimi client not working. Check your MOONSHOT_API_KEY in .env")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
