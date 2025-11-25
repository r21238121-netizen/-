#!/usr/bin/env python3
"""
Main entry point for the BingX trading bot.
This script properly initializes the client with config file validation.
"""
import asyncio
import sys
from bingx_client_updated import BingXClient
from config import config

def validate_api_keys():
    """Проверяет, что API ключи не являются значениями по умолчанию"""
    if config.API_KEY == "YOUR_API_KEY_HERE" or config.SECRET_KEY == "YOUR_SECRET_HERE":
        print("❌ API ключи не настроены! Пожалуйста, обновите config.py с вашими реальными ключами.")
        return False
    if not config.API_KEY or not config.SECRET_KEY:
        print("❌ Один или оба API ключа отсутствуют!")
        return False
    return True

async def test_api_connection(client):
    """Проверяет работоспособность API ключей"""
    try:
        print("🔍 Проверка API ключей...")
        balance = await client.get_balance()
        if 'code' in balance and balance['code'] != 0:
            print(f"❌ Ошибка API: {balance.get('msg', 'Неизвестная ошибка')}")
            return False
        print("✅ API ключи валидны, подключение успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при проверке API: {e}")
        return False

async def main():
    print("🚀 Starting BingX Trading Bot...")
    print("🔐 Checking API credentials from config file...")
    
    # Проверка API ключей перед инициализацией клиента
    if not validate_api_keys():
        print("❌ Завершение работы из-за отсутствия корректных API ключей")
        sys.exit(1)
    
    try:
        # Initialize the client
        client = BingXClient(mode=config.get_mode())  # Can be "swap" or "spot"
        
        print("✅ API credentials validated successfully!")
        print(f"📊 Trading mode: {client.mode}")
        print(f"🔗 Connected to: {client.base_url}")
        
        # Test the API connection
        if not await test_api_connection(client):
            print("❌ Завершение работы из-за проблем с API ключами")
            await client.close()
            sys.exit(1)
        
        # Example operations - uncomment as needed
        print("\n📋 Available operations:")
        print("   1. Get balance")
        print("   2. Get positions (swap mode only)")
        print("   3. Get ticker data")
        print("   4. Place orders")
        print("   5. Get PnL")
        print("   6. Close positions (swap mode only)")
        
        # Example: Get balance
        print("\n💰 Retrieving account balance...")
        balance = await client.get_balance()
        print(f"Balance response: {balance}")
        
        # Close the client session
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("🎯 BingX Trading Bot Initialization")
    print("⚠️  Make sure to update your config.py file with your actual API credentials before running!")
    print()
    asyncio.run(main())