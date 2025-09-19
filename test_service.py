#!/usr/bin/env python3
"""
Test script for the Protein Structure Prediction Web Service
"""

import asyncio
import json
import time
from typing import Dict, Any

# Test sequence from the original assignment
TEST_SEQUENCE = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"

async def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
    except ImportError:
        print("⚠️ httpx not available, skipping health test")
        return False
    except Exception as e:
        print(f"❌ Health test error: {str(e)}")
        return False

async def test_prediction_endpoint():
    """Test the prediction endpoint"""
    print("🔬 Testing prediction endpoint...")
    
    try:
        import httpx
        
        # Prepare request
        request_data = {
            "sequence": TEST_SEQUENCE
        }
        
        async with httpx.AsyncClient() as client:
            print(f"📤 Sending prediction request for sequence: {TEST_SEQUENCE[:20]}...")
            
            start_time = time.time()
            response = await client.post(
                "http://localhost:8000/predict",
                json=request_data,
                timeout=300.0  # 5 minutes timeout
            )
            prediction_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Prediction successful!")
                print(f"   Prediction ID: {data['prediction_id']}")
                print(f"   Status: {data['status']}")
                print(f"   Execution Time: {prediction_time:.2f}s")
                
                # Show some result details
                result = data.get('result', {})
                if 'execution_summary' in result:
                    summary = result['execution_summary']
                    print(f"   Total Steps: {summary.get('total_steps', 'N/A')}")
                    print(f"   Completed Steps: {summary.get('completed_steps', 'N/A')}")
                
                return True
            else:
                print(f"❌ Prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except ImportError:
        print("⚠️ httpx not available, skipping prediction test")
        return False
    except Exception as e:
        print(f"❌ Prediction test error: {str(e)}")
        return False

async def test_invalid_sequence():
    """Test validation with invalid sequence"""
    print("🚫 Testing invalid sequence validation...")
    
    try:
        import httpx
        
        # Test with invalid characters
        invalid_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG123"
        
        request_data = {
            "sequence": invalid_sequence
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/predict",
                json=request_data
            )
            
            if response.status_code == 422:  # Validation error
                print("✅ Invalid sequence properly rejected")
                return True
            else:
                print(f"❌ Invalid sequence not properly validated: {response.status_code}")
                return False
                
    except ImportError:
        print("⚠️ httpx not available, skipping validation test")
        return False
    except Exception as e:
        print(f"❌ Validation test error: {str(e)}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Protein Structure Prediction Service Tests")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Invalid Sequence Validation", test_invalid_sequence),
        ("Prediction Endpoint", test_prediction_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Service is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the service logs for details.")
    
    return passed == total

def main():
    """Main function"""
    print("Protein Structure Prediction Service Test Suite")
    print()
    
    try:
        success = asyncio.run(run_all_tests())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
