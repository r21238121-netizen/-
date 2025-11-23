# PROJECT PHOENIX - Project Structure Documentation

## Overview
This document describes the complete structure and implementation of PROJECT PHOENIX, a Telegram gaming bot that creates a complete virtual economy and gaming ecosystem.

## Architecture Overview

```
phoenix_bot/
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── setup.sh                   # Setup script
├── test_bot.py                # Test suite
├── PROJECT_STRUCTURE.md       # This document
└── src/                       # Source code
    ├── __init__.py
    ├── core/                  # Core framework components
    │   ├── __init__.py
    │   └── config.py          # Application settings and configuration
    ├── domain/                # Business logic and domain models
    │   ├── __init__.py
    │   └── models.py          # Pydantic models for domain entities
    ├── infrastructure/        # Data access and external services
    │   ├── __init__.py
    │   ├── database.py        # Database models and connection manager
    │   └── repositories.py    # Data access layer implementations
    ├── application/           # Application services (use cases)
    │   ├── __init__.py
    │   ├── user_service.py    # User management and profile operations
    │   ├── game_service.py    # Game session and gameplay logic
    │   └── admin_service.py   # Administrative operations
    ├── adapters/              # External interface adapters
    │   ├── __init__.py
    │   └── telegram_handler.py # Telegram bot command handlers
    ├── admin/                 # Admin-specific modules (future)
    │   └── __init__.py
    └── monitoring/            # Observability components (future)
        └── __init__.py
```

## Component Details

### Core Layer
- **config.py**: Application settings using Pydantic BaseSettings with environment variable support
  - Telegram bot token
  - Database configuration
  - Game parameters (starting chips, bonuses, etc.)
  - Rate limiting settings

### Domain Layer
- **models.py**: Pydantic models representing business entities
  - User: Player profiles with ranks, levels, balances
  - GameSession: Active game sessions with participants and state
  - Transaction: Financial transactions with audit trail
  - Clan: Player groups for team-based activities
  - Achievement: Player accomplishments and rewards

### Infrastructure Layer
- **database.py**: SQLAlchemy ORM models and async database manager
  - UserDB: Database representation of users
  - GameSessionDB: Database representation of game sessions
  - TransactionDB: Database representation of transactions
  - ClanDB: Database representation of clans
  - AchievementDB: Database representation of achievements
  - DatabaseManager: Async database connection and session management

- **repositories.py**: Data access implementations
  - UserRepository: User CRUD operations
  - GameSessionRepository: Game session management
  - TransactionRepository: Transaction logging
  - ClanRepository: Clan management
  - AchievementRepository: Achievement tracking

### Application Layer
- **user_service.py**: User-related business logic
  - User registration with referral tracking
  - Daily bonus claiming
  - Profile management
  - Balance operations
  - Referral system

- **game_service.py**: Game-related business logic
  - Game session creation (Blackjack, Dice, RPS, etc.)
  - Game result processing
  - Reward distribution
  - Slot machine implementation

- **admin_service.py**: Administrative business logic
  - Balance adjustments
  - User banning/unbanning
  - Role management
  - Chat statistics
  - Message broadcasting

### Adapters Layer
- **telegram_handler.py**: Telegram bot interface
  - Command handlers (/start, /balance, /top, etc.)
  - Game command processing
  - Admin command processing
  - Message routing to services

## Game Features Implemented

### Player Features
1. **Profile System**
   - Level progression
   - Rank system (Новичок → Легенда)
   - Statistics tracking

2. **Economy System**
   - Virtual chips (non-withdrawable)
   - Daily bonuses
   - Referral rewards
   - Game winnings

3. **Social Features**
   - Referral system with rewards
   - Global and chat-specific leaderboards
   - Clan creation (planned)

4. **Games Implemented**
   - Blackjack (PvP)
   - Dice Arena (PvP)
   - RPS+ (5 variants) (PvP)
   - Slot Machine (PvE)

### Admin Features
1. **God Mode Admin Panel**
   - Balance adjustments
   - User management
   - Game control
   - Chat statistics
   - Broadcasting

2. **Command Set**
   - `/adm balance @user +5000` - Adjust balances
   - `/adm ban @user 1h` - Ban users
   - `/adm game blackjack disable` - Control games
   - `/adm stats` - View statistics
   - `/adm broadcast` - Send messages

## Technical Features

### Security & Compliance
- Anti-cheat mechanisms
- Rate limiting (1 session/minute per user)
- Telegram policy compliant (no real money)
- GDPR-ready account deletion

### Scalability
- Async architecture with asyncio
- Database connection pooling
- Redis caching support (planned)
- Microservice-ready architecture

### Monitoring
- Structured logging with structlog
- Performance metrics (planned)
- Error tracking

## Implementation Status

### ✅ Core Features
- [x] User registration and profiles
- [x] Basic economy system
- [x] Referral system
- [x] Daily bonus system
- [x] Game session management
- [x] Transaction logging
- [x] Admin command system
- [x] Basic games (Blackjack, Dice, RPS, Slot Machine)

### 🔄 In Progress
- [ ] Complete game implementations
- [ ] Clan system
- [ ] Advanced admin features
- [ ] Anti-cheat mechanisms

### 📋 Planned Features
- [ ] Clan tournaments
- [ ] Seasonal events
- [ ] Achievements system
- [ ] Web dashboard
- [ ] Advanced analytics

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: python-telegram-bot (v20.8+)
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic
- **Async**: asyncio, asyncpg
- **Caching**: Redis (planned)
- **Queue**: Celery (planned)
- **Monitoring**: Prometheus + Grafana (planned)

## Deployment

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment: `cp .env.example .env` and edit values
4. Run the bot: `python src/main.py`

## Development Guidelines

- All business logic in application layer
- Database operations through repositories
- Domain models define the business entities
- Adapters handle external interfaces
- Async operations throughout
- Comprehensive error handling
- Structured logging
- Type hints for all functions

## Testing Strategy

- Unit tests for services
- Integration tests for database operations
- Mock-based testing for external dependencies
- End-to-end tests for critical flows

## Security Considerations

- Input validation on all user inputs
- Rate limiting to prevent abuse
- SQL injection prevention through ORM
- Proper error handling without information leakage
- Environment-based configuration