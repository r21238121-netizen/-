#!/usr/bin/env python3
"""
Test script to verify that the BingX client properly loads API keys from .env file
and validates them during initialization.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_env_loading():
    """Test that environment variables are properly loaded from .env file"""
    print("🔍 Testing .env file loading...")
    
    api_key = os.getenv('BINGX_API_KEY')
    secret = os.getenv('BINGX_SECRET')
    mode = os.getenv('BINGX_MODE', 'swap')
    
    print(f"API Key: {'✅ Loaded' if api_key else '❌ Not found'}")
    print(f"Secret: {'✅ Loaded' if secret else '❌ Not found'}")
    print(f"Mode: {mode}")
    
    if not api_key or not secret:
        print("\n❌ ERROR: API credentials not found in .env file!")
        print("Please update your .env file with your actual API credentials.")
        return False
    
    if api_key == 'your_api_key_here' or secret == 'your_secret_here':
        print("\n❌ ERROR: Using default placeholder values in .env file!")
        print("Please update your .env file with your actual API credentials.")
        return False
    
    print("\n✅ Environment variables loaded successfully!")
    return True

async def test_client_initialization():
    """Test that the BingX client properly validates API keys during initialization"""
    print("\n🔍 Testing BingX client initialization...")
    
    try:
        from bingx_client_updated import BingXClient
        
        # This should fail if API keys are not properly set
        client = BingXClient(mode="swap")
        
        print(f"✅ Client initialized successfully with mode: {client.mode}")
        print(f"✅ API Key: {client.api_key[:8]}... (masked)")
        print(f"✅ Base URL: {client.base_url}")
        
        return True
        
    except ValueError as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during client initialization: {e}")
        return False

async def main():
    print("🧪 Testing .env file and BingX client initialization\n")
    
    # Test environment loading
    env_ok = test_env_loading()
    
    if not env_ok:
        return False
    
    # Test client initialization
    client_ok = await test_client_initialization()
    
    if env_ok and client_ok:
        print("\n🎉 All tests passed! The BingX client is ready to use with your API credentials.")
        print("\n📝 Remember to:")
        print("   1. Replace 'your_api_key_here' and 'your_secret_here' in .env with your actual credentials")
        print("   2. Never commit the .env file to version control")
        print("   3. Keep your API credentials secure")
        return True
    else:
        print("\n💥 Some tests failed. Please check your .env file and configuration.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)