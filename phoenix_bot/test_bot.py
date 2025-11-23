#!/usr/bin/env python3
"""
Basic tests for PROJECT PHOENIX Telegram Bot
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domain.models import User, GameSession, Transaction, UserRank, UserRole
from src.application.user_service import UserService
from src.application.game_service import GameService
from src.application.admin_service import AdminService
from src.infrastructure.repositories import UserRepository, GameSessionRepository, TransactionRepository


class TestUserService:
    """Test user service functionality"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.user_repo = MagicMock(spec=UserRepository)
        self.transaction_repo = MagicMock(spec=TransactionRepository)
        self.user_service = UserService(self.user_repo, self.transaction_repo)
    
    @pytest.mark.asyncio
    async def test_register_user(self):
        """Test user registration"""
        # Mock data
        self.user_repo.get_by_telegram_id.return_value = None
        self.user_repo.create = AsyncMock(return_value=User(
            telegram_id=123456789,
            first_name="Test",
            username="testuser",
            referral_code="ABC123XYZ"
        ))
        self.transaction_repo.create = AsyncMock()
        
        # Test registration
        result = await self.user_service.register_user(
            telegram_id=123456789,
            first_name="Test",
            username="testuser"
        )
        
        assert result is not None
        assert result.telegram_id == 123456789
        assert result.first_name == "Test"
        assert result.username == "testuser"
        assert result.referral_code is not None
        
        # Verify user was created
        self.user_repo.create.assert_called_once()
        # Verify transaction was created
        self.transaction_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_claim_daily_bonus(self):
        """Test claiming daily bonus"""
        # Mock user with no previous bonus claim
        mock_user = User(
            telegram_id=123456789,
            first_name="Test",
            chips=100,
            referrals_count=2
        )
        
        self.user_repo.get_by_telegram_id.return_value = mock_user
        self.user_repo.update = AsyncMock(return_value=mock_user.copy(update={"chips": 220}))  # 100 + 100 + (2*10)
        self.transaction_repo.create = AsyncMock()
        
        result = await self.user_service.claim_daily_bonus(123456789)
        
        assert result is not None
        assert result["success"] is True
        assert result["amount"] == 120  # base 100 + 2 referrals * 10 each
        assert "new_balance" in result


class TestGameService:
    """Test game service functionality"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.session_repo = MagicMock(spec=GameSessionRepository)
        self.user_repo = MagicMock(spec=UserRepository)
        self.transaction_repo = MagicMock(spec=TransactionRepository)
        self.game_service = GameService(self.session_repo, self.user_repo, self.transaction_repo)
    
    @pytest.mark.asyncio
    async def test_start_blackjack_session(self):
        """Test starting a blackjack session"""
        # Mock users
        player1 = User(telegram_id=123, first_name="Player1", chips=1000)
        player2 = User(telegram_id=456, first_name="Player2", chips=1000)
        
        self.user_repo.get_by_telegram_id = AsyncMock(side_effect=[player1, player2])
        self.session_repo.create = AsyncMock(return_value=GameSession(
            session_id="test_session",
            game_type="blackjack",
            participants=[123, 456]
        ))
        
        result = await self.game_service.start_blackjack_session(123, 456, 100, -1001)
        
        assert result is not None
        assert result.session_id == "test_session"
        assert result.game_type == "blackjack"
        assert 123 in result.participants
        assert 456 in result.participants


class TestAdminService:
    """Test admin service functionality"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.user_repo = MagicMock(spec=UserRepository)
        self.transaction_repo = MagicMock(spec=TransactionRepository)
        self.admin_service = AdminService(self.user_repo, self.transaction_repo)
    
    @pytest.mark.asyncio
    async def test_adjust_balance(self):
        """Test admin balance adjustment"""
        # Mock admin user
        admin_user = User(
            telegram_id=123456789,
            first_name="Admin",
            role="ADMIN",
            chips=1000
        )
        
        # Mock target user
        target_user = User(
            telegram_id=987654321,
            first_name="Target",
            chips=500
        )
        
        self.user_repo.get_by_telegram_id = AsyncMock(side_effect=[admin_user, target_user])
        self.user_repo.update = AsyncMock(return_value=target_user.copy(update={"chips": 1500}))
        self.transaction_repo.create = AsyncMock()
        
        result = await self.admin_service.adjust_balance(123456789, 987654321, 1000, "Test adjustment")
        
        assert result is not None
        assert result["success"] is True
        assert result["new_balance"] == 1500


def run_tests():
    """Run all tests"""
    print("🧪 Running PROJECT PHOENIX Bot Tests...")
    
    # Run tests with pytest
    import subprocess
    result = subprocess.run(['python', '-m', 'pytest', __file__, '-v'], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed:")
        print(result.stdout)
        print(result.stderr)


if __name__ == "__main__":
    run_tests()