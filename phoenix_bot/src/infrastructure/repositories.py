from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
import json

from src.domain.entities import User, GameSession, Clan, GameResult
from src.domain.repositories import UserRepository, GameRepository, SessionRepository, ClanRepository
from src.infrastructure.database import UserDB, GameSessionDB, ClanDB, GameResultDB
from src.domain.entities import UserRole, GameType, GameStatus


class SQLAlchemyUserRepository(UserRepository):
    """Репозиторий пользователей на основе SQLAlchemy"""
    
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        async with self.session_factory() as session:
            stmt = select(UserDB).where(UserDB.id == user_id)
            result = await session.execute(stmt)
            user_db = result.scalar_one_or_none()
            if user_db:
                return self._map_db_to_entity(user_db)
        return None
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        async with self.session_factory() as session:
            stmt = select(UserDB).where(UserDB.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user_db = result.scalar_one_or_none()
            if user_db:
                return self._map_db_to_entity(user_db)
        return None
    
    async def create(self, user: User) -> User:
        async with self.session_factory() as session:
            user_db = UserDB(
                id=user.id,
                telegram_id=user.telegram_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                level=user.level,
                chips=user.chips,
                stars=user.stars,
                experience=user.experience,
                wins=user.wins,
                losses=user.losses,
                draws=user.draws,
                referrals_count=user.referrals_count,
                total_bets=user.total_bets,
                role=user.role.value,
                is_banned=user.is_banned,
                is_active=user.is_active,
                last_daily_bonus=user.last_daily_bonus,
                referrer_id=user.referrer_id,
                clan_id=user.clan_id
            )
            session.add(user_db)
            await session.commit()
            await session.refresh(user_db)
            return self._map_db_to_entity(user_db)
    
    async def update(self, user_id: str, **kwargs) -> Optional[User]:
        async with self.session_factory() as session:
            stmt = update(UserDB).where(UserDB.id == user_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()
            
            stmt = select(UserDB).where(UserDB.id == user_id)
            result = await session.execute(stmt)
            user_db = result.scalar_one_or_none()
            if user_db:
                return self._map_db_to_entity(user_db)
        return None
    
    async def delete(self, user_id: str) -> bool:
        async with self.session_factory() as session:
            stmt = delete(UserDB).where(UserDB.id == user_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def get_top_users(self, limit: int = 10) -> List[User]:
        async with self.session_factory() as session:
            stmt = select(UserDB).order_by(UserDB.chips.desc()).limit(limit)
            result = await session.execute(stmt)
            users_db = result.scalars().all()
            return [self._map_db_to_entity(user_db) for user_db in users_db]
    
    async def get_chat_top_users(self, chat_id: str, limit: int = 10) -> List[User]:
        # Для упрощения возвращаем глобальный топ, т.к. в схеме нет прямой связи пользователь-чат
        # В реальном приложении потребуется дополнительная таблица связи
        return await self.get_top_users(limit)
    
    async def increment_referrals(self, user_id: str) -> Optional[User]:
        async with self.session_factory() as session:
            stmt = update(UserDB).where(UserDB.id == user_id).values(
                referrals_count=UserDB.referrals_count + 1
            )
            await session.execute(stmt)
            await session.commit()
            
            stmt = select(UserDB).where(UserDB.id == user_id)
            result = await session.execute(stmt)
            user_db = result.scalar_one_or_none()
            if user_db:
                return self._map_db_to_entity(user_db)
        return None
    
    def _map_db_to_entity(self, user_db: UserDB) -> User:
        """Преобразование DB объекта в доменную сущность"""
        return User(
            id=user_db.id,
            telegram_id=user_db.telegram_id,
            username=user_db.username,
            first_name=user_db.first_name,
            last_name=user_db.last_name,
            level=user_db.level,
            chips=user_db.chips,
            stars=user_db.stars,
            experience=user_db.experience,
            wins=user_db.wins,
            losses=user_db.losses,
            draws=user_db.draws,
            referrals_count=user_db.referrals_count,
            total_bets=user_db.total_bets,
            role=UserRole(user_db.role),
            is_banned=user_db.is_banned,
            is_active=user_db.is_active,
            created_at=user_db.created_at,
            updated_at=user_db.updated_at,
            last_daily_bonus=user_db.last_daily_bonus,
            referrer_id=user_db.referrer_id,
            clan_id=user_db.clan_id
        )


class SQLAlchemyGameRepository(GameRepository):
    """Репозиторий игр на основе SQLAlchemy"""
    
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory
    
    async def get_by_id(self, game_id: str) -> Optional[GameSession]:
        async with self.session_factory() as session:
            stmt = select(GameSessionDB).where(GameSessionDB.id == game_id)
            result = await session.execute(stmt)
            game_db = result.scalar_one_or_none()
            if game_db:
                return self._map_db_to_entity(game_db)
        return None
    
    async def create(self, game_session: GameSession) -> GameSession:
        async with self.session_factory() as session:
            game_db = GameSessionDB(
                id=game_session.id,
                game_type=game_session.game_type.value,
                status=game_session.status.value,
                players=json.dumps(game_session.players),
                bet_amount=game_session.bet_amount,
                chat_id=game_session.chat_id,
                created_at=game_session.created_at,
                started_at=game_session.started_at,
                finished_at=game_session.finished_at,
                winner_id=game_session.winner_id,
                game_metadata=json.dumps(game_session.metadata) if game_session.metadata else None
            )
            session.add(game_db)
            await session.commit()
            await session.refresh(game_db)
            return self._map_db_to_entity(game_db)
    
    async def update(self, game_id: str, **kwargs) -> Optional[GameSession]:
        async with self.session_factory() as session:
            # Преобразуем enum значения в строки для обновления
            update_values = {}
            for key, value in kwargs.items():
                if isinstance(value, (GameType, GameStatus, UserRole)):
                    update_values[key] = value.value
                elif key == 'players' or key == 'game_metadata':
                    update_values[key] = json.dumps(value) if value else None
                else:
                    update_values[key] = value
            
            stmt = update(GameSessionDB).where(GameSessionDB.id == game_id).values(**update_values)
            await session.execute(stmt)
            await session.commit()
            
            stmt = select(GameSessionDB).where(GameSessionDB.id == game_id)
            result = await session.execute(stmt)
            game_db = result.scalar_one_or_none()
            if game_db:
                return self._map_db_to_entity(game_db)
        return None
    
    async def delete(self, game_id: str) -> bool:
        async with self.session_factory() as session:
            stmt = delete(GameSessionDB).where(GameSessionDB.id == game_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def get_active_games(self, chat_id: str) -> List[GameSession]:
        async with self.session_factory() as session:
            stmt = select(GameSessionDB).where(
                GameSessionDB.chat_id == chat_id,
                GameSessionDB.status.in_(['active', 'waiting'])
            )
            result = await session.execute(stmt)
            games_db = result.scalars().all()
            return [self._map_db_to_entity(game_db) for game_db in games_db]
    
    async def get_user_active_games(self, user_id: str) -> List[GameSession]:
        async with self.session_factory() as session:
            stmt = select(GameSessionDB).where(
                GameSessionDB.status.in_(['active', 'waiting'])
            )
            result = await session.execute(stmt)
            games_db = result.scalars().all()
            # Фильтруем по пользователю на уровне приложения, т.к. players хранится как JSON
            user_games = []
            for game_db in games_db:
                players = json.loads(game_db.players) if game_db.players else []
                if user_id in players:
                    user_games.append(self._map_db_to_entity(game_db))
            return user_games
    
    async def save_result(self, result: GameResult) -> GameResult:
        async with self.session_factory() as session:
            result_db = GameResultDB(
                id=result.game_id,  # Используем game_id как id результата для простоты
                game_id=result.game_id,
                winner_id=result.winner_id,
                loser_id=result.loser_id,
                game_type=result.game_type.value,
                bet_amount=result.bet_amount,
                timestamp=result.timestamp,
                metadata=json.dumps(result.metadata) if result.metadata else None
            )
            session.add(result_db)
            await session.commit()
            await session.refresh(result_db)
            return self._map_result_db_to_entity(result_db)
    
    async def get_game_results(self, user_id: str, limit: int = 10) -> List[GameResult]:
        async with self.session_factory() as session:
            stmt = select(GameResultDB).where(
                (GameResultDB.winner_id == user_id) | (GameResultDB.loser_id == user_id)
            ).order_by(GameResultDB.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            results_db = result.scalars().all()
            return [self._map_result_db_to_entity(result_db) for result_db in results_db]
    
    def _map_db_to_entity(self, game_db: GameSessionDB) -> GameSession:
        """Преобразование DB объекта в доменную сущность"""
        return GameSession(
            id=game_db.id,
            game_type=GameType(game_db.game_type),
            status=GameStatus(game_db.status),
            players=json.loads(game_db.players) if game_db.players else [],
            bet_amount=game_db.bet_amount,
            chat_id=game_db.chat_id,
            created_at=game_db.created_at,
            started_at=game_db.started_at,
            finished_at=game_db.finished_at,
            winner_id=game_db.winner_id,
            metadata=json.loads(game_db.game_metadata) if game_db.game_metadata else None
        )
    
    def _map_result_db_to_entity(self, result_db: GameResultDB) -> GameResult:
        """Преобразование DB объекта результата в доменную сущность"""
        return GameResult(
            game_id=result_db.game_id,
            winner_id=result_db.winner_id,
            loser_id=result_db.loser_id,
            game_type=GameType(result_db.game_type),
            bet_amount=result_db.bet_amount,
            timestamp=result_db.timestamp,
            metadata=json.loads(result_db.metadata) if result_db.metadata else None
        )


class SQLAlchemySessionRepository(SessionRepository):
    """Репозиторий сессий на основе SQLAlchemy"""
    
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory
    
    async def get_by_id(self, session_id: str) -> Optional[GameSession]:
        async with self.session_factory() as session:
            stmt = select(GameSessionDB).where(GameSessionDB.id == session_id)
            result = await session.execute(stmt)
            session_db = result.scalar_one_or_none()
            if session_db:
                return self._map_db_to_entity(session_db)
        return None
    
    async def create(self, session: GameSession) -> GameSession:
        async with self.session_factory() as session:
            session_db = GameSessionDB(
                id=session.id,
                game_type=session.game_type.value,
                status=session.status.value,
                players=json.dumps(session.players),
                bet_amount=session.bet_amount,
                chat_id=session.chat_id,
                created_at=session.created_at,
                started_at=session.started_at,
                finished_at=session.finished_at,
                winner_id=session.winner_id,
                game_metadata=json.dumps(session.metadata) if session.metadata else None
            )
            session.add(session_db)
            await session.commit()
            await session.refresh(session_db)
            return self._map_db_to_entity(session_db)
    
    async def update(self, session_id: str, **kwargs) -> Optional[GameSession]:
        async with self.session_factory() as session:
            # Преобразуем enum значения в строки для обновления
            update_values = {}
            for key, value in kwargs.items():
                if isinstance(value, (GameType, GameStatus, UserRole)):
                    update_values[key] = value.value
                elif key == 'players' or key == 'game_metadata':
                    update_values[key] = json.dumps(value) if value else None
                else:
                    update_values[key] = value
            
            stmt = update(GameSessionDB).where(GameSessionDB.id == session_id).values(**update_values)
            await session.execute(stmt)
            await session.commit()
            
            stmt = select(GameSessionDB).where(GameSessionDB.id == session_id)
            result = await session.execute(stmt)
            session_db = result.scalar_one_or_none()
            if session_db:
                return self._map_db_to_entity(session_db)
        return None
    
    async def delete(self, session_id: str) -> bool:
        async with self.session_factory() as session:
            stmt = delete(GameSessionDB).where(GameSessionDB.id == session_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def get_active_sessions(self) -> List[GameSession]:
        async with self.session_factory() as session:
            stmt = select(GameSessionDB).where(
                GameSessionDB.status.in_(['active', 'waiting'])
            )
            result = await session.execute(stmt)
            sessions_db = result.scalars().all()
            return [self._map_db_to_entity(session_db) for session_db in sessions_db]
    
    async def get_user_session(self, user_id: str) -> Optional[GameSession]:
        async with self.session_factory() as session:
            stmt = select(GameSessionDB).where(
                GameSessionDB.status.in_(['active', 'waiting'])
            )
            result = await session.execute(stmt)
            sessions_db = result.scalars().all()
            # Фильтруем по пользователю на уровне приложения, т.к. players хранится как JSON
            for session_db in sessions_db:
                players = json.loads(session_db.players) if session_db.players else []
                if user_id in players:
                    return self._map_db_to_entity(session_db)
            return None
    
    def _map_db_to_entity(self, session_db: GameSessionDB) -> GameSession:
        """Преобразование DB объекта в доменную сущность"""
        return GameSession(
            id=session_db.id,
            game_type=GameType(session_db.game_type),
            status=GameStatus(session_db.status),
            players=json.loads(session_db.players) if session_db.players else [],
            bet_amount=session_db.bet_amount,
            chat_id=session_db.chat_id,
            created_at=session_db.created_at,
            started_at=session_db.started_at,
            finished_at=session_db.finished_at,
            winner_id=session_db.winner_id,
            metadata=json.loads(session_db.game_metadata) if session_db.game_metadata else None
        )


class SQLAlchemyClanRepository(ClanRepository):
    """Репозиторий кланов на основе SQLAlchemy"""
    
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory
    
    async def get_by_id(self, clan_id: str) -> Optional[Clan]:
        async with self.session_factory() as session:
            stmt = select(ClanDB).where(ClanDB.id == clan_id)
            result = await session.execute(stmt)
            clan_db = result.scalar_one_or_none()
            if clan_db:
                return self._map_db_to_entity(clan_db)
        return None
    
    async def get_by_name(self, name: str) -> Optional[Clan]:
        async with self.session_factory() as session:
            stmt = select(ClanDB).where(ClanDB.name == name)
            result = await session.execute(stmt)
            clan_db = result.scalar_one_or_none()
            if clan_db:
                return self._map_db_to_entity(clan_db)
        return None
    
    async def create(self, clan: Clan) -> Clan:
        async with self.session_factory() as session:
            clan_db = ClanDB(
                id=clan.id,
                name=clan.name,
                owner_id=clan.owner_id,
                members=json.dumps(clan.members),
                level=clan.level,
                reputation=clan.reputation,
                created_at=clan.created_at
            )
            session.add(clan_db)
            await session.commit()
            await session.refresh(clan_db)
            return self._map_db_to_entity(clan_db)
    
    async def update(self, clan_id: str, **kwargs) -> Optional[Clan]:
        async with self.session_factory() as session:
            update_values = {}
            for key, value in kwargs.items():
                if key == 'members':
                    update_values[key] = json.dumps(value) if value else None
                else:
                    update_values[key] = value
            
            stmt = update(ClanDB).where(ClanDB.id == clan_id).values(**update_values)
            await session.execute(stmt)
            await session.commit()
            
            stmt = select(ClanDB).where(ClanDB.id == clan_id)
            result = await session.execute(stmt)
            clan_db = result.scalar_one_or_none()
            if clan_db:
                return self._map_db_to_entity(clan_db)
        return None
    
    async def delete(self, clan_id: str) -> bool:
        async with self.session_factory() as session:
            stmt = delete(ClanDB).where(ClanDB.id == clan_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def get_user_clan(self, user_id: str) -> Optional[Clan]:
        async with self.session_factory() as session:
            # Получаем все кланы и ищем, где пользователь является членом
            stmt = select(ClanDB)
            result = await session.execute(stmt)
            clans_db = result.scalars().all()
            for clan_db in clans_db:
                members = json.loads(clan_db.members) if clan_db.members else []
                if user_id in members:
                    return self._map_db_to_entity(clan_db)
            return None
    
    async def get_top_clans(self, limit: int = 10) -> List[Clan]:
        async with self.session_factory() as session:
            stmt = select(ClanDB).order_by(ClanDB.reputation.desc()).limit(limit)
            result = await session.execute(stmt)
            clans_db = result.scalars().all()
            return [self._map_db_to_entity(clan_db) for clan_db in clans_db]
    
    def _map_db_to_entity(self, clan_db: ClanDB) -> Clan:
        """Преобразование DB объекта в доменную сущность"""
        return Clan(
            id=clan_db.id,
            name=clan_db.name,
            owner_id=clan_db.owner_id,
            members=json.loads(clan_db.members) if clan_db.members else [],
            level=clan_db.level,
            reputation=clan_db.reputation,
            created_at=clan_db.created_at,
            updated_at=clan_db.updated_at
        )