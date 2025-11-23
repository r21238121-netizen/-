from typing import Optional, Dict, Any
from datetime import datetime

from src.domain.entities import User, GameType, UserRole
from src.application.admin_service import AdminService
from src.application.user_service import UserService


class TelegramAdminService:
    """Сервис администратора для работы с командами Telegram"""
    
    def __init__(self, admin_service: AdminService, user_service: UserService):
        self.admin_service = admin_service
        self.user_service = user_service
    
    async def handle_balance_command(
        self, 
        admin_user: User, 
        target_user_id: str, 
        amount: int,
        operation: str = "set"  # "set", "add"
    ) -> Dict[str, Any]:
        """Обработать команду изменения баланса"""
        # Проверяем права администратора
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        if operation == "set":
            result = await self.admin_service.set_user_balance(
                admin_user.id, target_user_id, amount
            )
        elif operation == "add":
            result = await self.admin_service.add_to_balance(
                admin_user.id, target_user_id, amount
            )
        else:
            return {
                "success": False,
                "message": "Неверная операция"
            }
        
        if result:
            return {
                "success": True,
                "message": f"Баланс пользователя обновлен: {result.chips} фишек",
                "new_balance": result.chips
            }
        else:
            return {
                "success": False,
                "message": "Не удалось обновить баланс пользователя"
            }
    
    async def handle_ban_command(
        self, 
        admin_user: User, 
        target_user_id: str,
        reason: str = "unknown"
    ) -> Dict[str, Any]:
        """Обработать команду бана пользователя"""
        # Проверяем права
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.MODERATOR]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        result = await self.admin_service.ban_user(
            admin_user.id, target_user_id, reason
        )
        
        if result:
            return {
                "success": True,
                "message": f"Пользователь {result.username or result.id} заблокирован"
            }
        else:
            return {
                "success": False,
                "message": "Не удалось заблокировать пользователя"
            }
    
    async def handle_unban_command(
        self, 
        admin_user: User, 
        target_user_id: str
    ) -> Dict[str, Any]:
        """Обработать команду разбана пользователя"""
        # Проверяем права
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        result = await self.admin_service.unban_user(
            admin_user.id, target_user_id
        )
        
        if result:
            return {
                "success": True,
                "message": f"Пользователь {result.username or result.id} разблокирован"
            }
        else:
            return {
                "success": False,
                "message": "Не удалось разблокировать пользователя"
            }
    
    async def handle_role_command(
        self, 
        admin_user: User, 
        target_user_id: str,
        new_role: UserRole
    ) -> Dict[str, Any]:
        """Обработать команду изменения роли пользователя"""
        # Проверяем права
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        # Назначаем новую роль
        result = await self.admin_service.set_user_role(
            admin_user.id, target_user_id, new_role
        )
        
        if result:
            return {
                "success": True,
                "message": f"Роль пользователя {result.username or result.id} изменена на {new_role.value}"
            }
        else:
            return {
                "success": False,
                "message": "Не удалось изменить роль пользователя"
            }
    
    async def handle_game_control_command(
        self, 
        admin_user: User, 
        game_type: GameType,
        action: str  # "enable", "disable"
    ) -> Dict[str, Any]:
        """Обработать команду управления игрой"""
        # Проверяем права
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        if action == "disable":
            success = await self.admin_service.disable_game(
                admin_user.id, game_type
            )
            message = f"Игра {game_type.value} отключена"
        elif action == "enable":
            success = await self.admin_service.enable_game(
                admin_user.id, game_type
            )
            message = f"Игра {game_type.value} включена"
        else:
            return {
                "success": False,
                "message": "Неверное действие"
            }
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            return {
                "success": False,
                "message": "Не удалось выполнить операцию"
            }
    
    async def handle_user_stats_command(
        self, 
        admin_user: User, 
        target_user_id: str
    ) -> Dict[str, Any]:
        """Обработать команду получения статистики пользователя"""
        # Проверяем права
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.MODERATOR]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        stats = await self.admin_service.get_user_stats(target_user_id)
        
        if stats:
            user_info = stats["user_info"]
            game_stats = stats["game_stats"]
            
            message = f"""
📊 Статистика пользователя:
ID: {user_info["id"]}
Telegram ID: {user_info["telegram_id"]}
Имя: {user_info["first_name"]} {user_info["last_name"] or ""}
Имя пользователя: @{user_info["username"]} 
Уровень: {user_info["level"]}
Фишки: {user_info["chips"]}
Звезды: {user_info["stars"]}
Опыт: {user_info["experience"]}
Роль: {user_info["role"]}
Заблокирован: {'Да' if user_info["is_banned"] else 'Нет'}
Рефералов: {user_info["referrals_count"]}
Дата регистрации: {user_info["created_at"]}

🎮 Игровая статистика:
Побед: {game_stats["wins"]}
Поражений: {game_stats["losses"]}
Ничьих: {game_stats["draws"]}
Всего ставок: {game_stats["total_bets"]}
            """.strip()
            
            return {
                "success": True,
                "message": message,
                "stats": stats
            }
        else:
            return {
                "success": False,
                "message": "Не удалось получить статистику пользователя"
            }
    
    async def handle_chat_stats_command(
        self, 
        admin_user: User, 
        chat_id: str
    ) -> Dict[str, Any]:
        """Обработать команду получения статистики чата"""
        # Проверяем права
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.MODERATOR]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        stats = await self.admin_service.get_chat_stats(chat_id)
        
        if stats:
            message = f"""
📈 Статистика чата {chat_id}:
Всего пользователей: {stats["total_users"]}
Активных игр: {stats["active_games"]}

🏆 Топ пользователей:
            """.strip()
            
            for i, user in enumerate(stats["top_users"][:5], 1):
                message += f"\n{i}. @{user['username']} - {user['chips']} фишек (уровень {user['level']})"
            
            if stats["active_games_list"]:
                message += f"\n\n🎮 Активные игры:"
                for game in stats["active_games_list"]:
                    message += f"\n- {game['game_type']} ({game['bet_amount']} фишек) - {game['players']}"
            
            return {
                "success": True,
                "message": message,
                "stats": stats
            }
        else:
            return {
                "success": False,
                "message": "Не удалось получить статистику чата"
            }
    
    async def handle_force_end_session(
        self, 
        admin_user: User, 
        session_id: str
    ) -> Dict[str, Any]:
        """Обработать команду принудительного завершения сессии"""
        # Проверяем права
        if admin_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.MODERATOR]:
            return {
                "success": False,
                "message": "Недостаточно прав для выполнения операции"
            }
        
        success = await self.admin_service.force_end_session(
            admin_user.id, session_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Сессия {session_id} принудительно завершена"
            }
        else:
            return {
                "success": False,
                "message": "Не удалось завершить сессию"
            }