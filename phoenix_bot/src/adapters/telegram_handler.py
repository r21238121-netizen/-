from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, CallbackQueryHandler
)
from typing import Dict, Any, List
import re
from datetime import datetime

from src.domain.entities import User, GameType, UserRole
from src.application.game_service import GameService
from src.application.user_service import UserService
from src.admin.admin_service import TelegramAdminService


class TelegramHandler:
    """Обработчик Telegram команд и сообщений"""
    
    def __init__(
        self,
        game_service: GameService,
        admin_service: TelegramAdminService,
        user_service: UserService,
        config: Any
    ):
        self.game_service = game_service
        self.admin_service = admin_service
        self.user_service = user_service
        self.config = config
        self.application = None
    
    def setup_handlers(self, application: Application):
        """Настройка обработчиков команд"""
        self.application = application
        
        # Основные команды
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("profile", self.profile_command))
        application.add_handler(CommandHandler("balance", self.balance_command))
        application.add_handler(CommandHandler("top", self.top_command))
        application.add_handler(CommandHandler("daily", self.daily_bonus_command))
        
        # Игровые команды
        application.add_handler(CommandHandler("blackjack", self.blackjack_command))
        application.add_handler(CommandHandler("dice", self.dice_command))
        application.add_handler(CommandHandler("rps", self.rps_command))
        application.add_handler(CommandHandler("duel", self.duel_command))
        
        # Админ команды
        application.add_handler(CommandHandler("adm", self.admin_command))
        
        # Обработка сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Проверяем, есть ли реферал в команде
        referrer_id = None
        if context.args and len(context.args) > 0:
            # В реальной системе реферал передается как ID пользователя
            pass
        
        # Регистрируем пользователя
        created_user = await self.user_service.register_user(
            user.id, user.username, user.first_name, user.last_name, referrer_id
        )
        
        if created_user:
            message = f"""
🎮 Добро пожаловать в Phoenix Bot, {user.first_name}!

У вас {created_user.chips} фишек
Уровень: {created_user.level} ({created_user.get_rank()})
        
Основные команды:
/profile - ваш профиль
/balance - баланс
/top - топ игроков
/daily - ежедневный бонус

Игры:
/blackjack - Блэкджек
/dice - Кости
/rps - Камень-ножницы-бумага
/duel - дуэль с другом

Для администраторов:
/adm - команды администратора
            """.strip()
        else:
            message = "Ошибка при регистрации. Попробуйте еще раз."
        
        await update.message.reply_text(message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        message = """
🎮 Помощь по Phoenix Bot

Основные команды:
/profile - ваш профиль и статистика
/balance - ваш баланс
/top - топ игроков
/daily - получить ежедневный бонус

Игровые команды:
/blackjack [ставка] - игра в блэкджек
/dice [ставка] - игра в кости
/rps [ставка] - камень-ножницы-бумага
/duel @username [ставка] - дуэль с другом

Для администраторов:
/adm balance @username [сумма] - установить баланс
/adm ban @username - заблокировать пользователя
/adm unban @username - разблокировать пользователя
/adm role @username [moderator/admin] - установить роль
/adm stats - статистика чата
/adm end_session [id] - завершить сессию
        """
        await update.message.reply_text(message)
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /profile"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        message = f"""
👤 Профиль {user.first_name} (@{user.username or 'не указан'})

🏆 Уровень: {db_user.level} ({db_user.get_rank()})
💎 Фишки: {db_user.chips}
⭐ Звезды: {db_user.stars}
经验值 Опыт: {db_user.experience}/{db_user.get_next_level_exp()}

📊 Статистика:
Побед: {db_user.wins}
Поражений: {db_user.losses}
Ничьих: {db_user.draws}
Рефералов: {db_user.referrals_count}
Всего ставок: {db_user.total_bets}
        """
        await update.message.reply_text(message)
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /balance"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        message = f"💰 Ваш баланс: {db_user.chips} фишек"
        await update.message.reply_text(message)
    
    async def top_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /top"""
        users = await self.user_service.get_top_users(10)
        
        if not users:
            await update.message.reply_text("Еще нет зарегистрированных пользователей")
            return
        
        message = "🏆 Топ игроков:\n"
        for i, user in enumerate(users, 1):
            message += f"{i}. {user.first_name} - {user.chips} фишек (уровень {user.level})\n"
        
        await update.message.reply_text(message)
    
    async def daily_bonus_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /daily"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        updated_user = await self.user_service.claim_daily_bonus(db_user.id)
        if updated_user:
            message = f"✅ Вы получили ежедневный бонус! На вашем счету теперь {updated_user.chips} фишек."
        else:
            message = "❌ Вы уже получали ежедневный бонус за последние 24 часа."
        
        await update.message.reply_text(message)
    
    async def blackjack_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /blackjack"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        if db_user.is_banned:
            await update.message.reply_text("❌ Вы заблокированы и не можете играть")
            return
        
        # Получаем ставку из аргументов
        bet_amount = 100  # ставка по умолчанию
        if context.args and len(context.args) > 0:
            try:
                bet_amount = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ Неверная сумма ставки")
                return
        
        # Проверяем ограничения ставки
        if bet_amount < 10 or bet_amount > 10000:
            await update.message.reply_text("❌ Ставка должна быть от 10 до 10000 фишек")
            return
        
        if db_user.chips < bet_amount:
            await update.message.reply_text("❌ Недостаточно фишек для ставки")
            return
        
        # В реальной реализации здесь будет логика создания сессии блэкджека
        message = f"🃏 Игра Блэкджек начата! Ставка: {bet_amount} фишек"
        await update.message.reply_text(message)
    
    async def dice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /dice"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        if db_user.is_banned:
            await update.message.reply_text("❌ Вы заблокированы и не можете играть")
            return
        
        # Получаем ставку из аргументов
        bet_amount = 100  # ставка по умолчанию
        if context.args and len(context.args) > 0:
            try:
                bet_amount = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ Неверная сумма ставки")
                return
        
        # Проверяем ограничения ставки
        if bet_amount < 10 or bet_amount > 10000:
            await update.message.reply_text("❌ Ставка должна быть от 10 до 10000 фишек")
            return
        
        if db_user.chips < bet_amount:
            await update.message.reply_text("❌ Недостаточно фишек для ставки")
            return
        
        # В реальной реализации здесь будет логика создания сессии костей
        message = f"🎲 Игра Кости начата! Ставка: {bet_amount} фишек"
        await update.message.reply_text(message)
    
    async def rps_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /rps"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        if db_user.is_banned:
            await update.message.reply_text("❌ Вы заблокированы и не можете играть")
            return
        
        # Получаем ставку из аргументов
        bet_amount = 100  # ставка по умолчанию
        if context.args and len(context.args) > 0:
            try:
                bet_amount = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ Неверная сумма ставки")
                return
        
        # Проверяем ограничения ставки
        if bet_amount < 10 or bet_amount > 10000:
            await update.message.reply_text("❌ Ставка должна быть от 10 до 10000 фишек")
            return
        
        if db_user.chips < bet_amount:
            await update.message.reply_text("❌ Недостаточно фишек для ставки")
            return
        
        # В реальной реализации здесь будет логика создания сессии КНБ
        message = f"✂️ Игра Камень-Ножницы-Бумага начата! Ставка: {bet_amount} фишек"
        await update.message.reply_text(message)
    
    async def duel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /duel"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        if db_user.is_banned:
            await update.message.reply_text("❌ Вы заблокированы и не можете играть")
            return
        
        # Команда должна быть в формате /duel @username [ставка]
        if len(context.args) < 2:
            await update.message.reply_text("❌ Использование: /duel @username [ставка]")
            return
        
        target_username = context.args[0].lstrip('@')
        try:
            bet_amount = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Неверная сумма ставки")
            return
        
        # Проверяем ограничения ставки
        if bet_amount < 10 or bet_amount > 10000:
            await update.message.reply_text("❌ Ставка должна быть от 10 до 10000 фишек")
            return
        
        if db_user.chips < bet_amount:
            await update.message.reply_text("❌ Недостаточно фишек для ставки")
            return
        
        # В реальной реализации здесь будет поиск соперника и создание сессии
        message = f"⚔️ Вызов {target_username} на дуэль! Ставка: {bet_amount} фишек"
        await update.message.reply_text(message)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка админ-команды /adm"""
        user = update.effective_user
        db_user = await self.user_service.get_user(user.id)
        
        if not db_user:
            await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
            return
        
        # Проверяем права администратора
        if db_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.MODERATOR]:
            await update.message.reply_text("❌ У вас нет прав администратора")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите подкоманду. Используйте /help для списка команд")
            return
        
        command = context.args[0].lower()
        
        if command == "balance":
            await self._handle_admin_balance(update, context, db_user)
        elif command == "ban":
            await self._handle_admin_ban(update, context, db_user)
        elif command == "unban":
            await self._handle_admin_unban(update, context, db_user)
        elif command == "role":
            await self._handle_admin_role(update, context, db_user)
        elif command == "stats":
            await self._handle_admin_stats(update, context, db_user)
        elif command == "end_session":
            await self._handle_admin_end_session(update, context, db_user)
        else:
            await update.message.reply_text(f"❌ Неизвестная подкоманда: {command}")
    
    async def _handle_admin_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_user: User):
        """Обработка подкоманды /adm balance"""
        if len(context.args) < 3:
            await update.message.reply_text("❌ Использование: /adm balance @username [сумма]")
            return
        
        target_username = context.args[1].lstrip('@')
        try:
            amount = int(context.args[2])
        except ValueError:
            await update.message.reply_text("❌ Неверная сумма")
            return
        
        # В реальной системе нужно найти пользователя по username
        # Пока используем заглушку
        target_user = await self.user_service.get_user(update.effective_user.id)  # Заглушка
        if not target_user:
            await update.message.reply_text(f"❌ Пользователь @{target_username} не найден")
            return
        
        result = await self.admin_service.handle_balance_command(
            admin_user, target_user.id, amount, "set"
        )
        
        await update.message.reply_text(result["message"])
    
    async def _handle_admin_ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_user: User):
        """Обработка подкоманды /adm ban"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ Использование: /adm ban @username")
            return
        
        target_username = context.args[1].lstrip('@')
        
        # В реальной системе нужно найти пользователя по username
        # Пока используем заглушку
        target_user = await self.user_service.get_user(update.effective_user.id)  # Заглушка
        if not target_user:
            await update.message.reply_text(f"❌ Пользователь @{target_username} не найден")
            return
        
        result = await self.admin_service.handle_ban_command(
            admin_user, target_user.id
        )
        
        await update.message.reply_text(result["message"])
    
    async def _handle_admin_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_user: User):
        """Обработка подкоманды /adm unban"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ Использование: /adm unban @username")
            return
        
        target_username = context.args[1].lstrip('@')
        
        # В реальной системе нужно найти пользователя по username
        # Пока используем заглушку
        target_user = await self.user_service.get_user(update.effective_user.id)  # Заглушка
        if not target_user:
            await update.message.reply_text(f"❌ Пользователь @{target_username} не найден")
            return
        
        result = await self.admin_service.handle_unban_command(
            admin_user, target_user.id
        )
        
        await update.message.reply_text(result["message"])
    
    async def _handle_admin_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_user: User):
        """Обработка подкоманды /adm role"""
        if len(context.args) < 3:
            await update.message.reply_text("❌ Использование: /adm role @username [moderator/admin]")
            return
        
        target_username = context.args[1].lstrip('@')
        role_str = context.args[2].lower()
        
        if role_str == "moderator":
            role = UserRole.MODERATOR
        elif role_str == "admin":
            role = UserRole.ADMIN
        elif role_str == "player":
            role = UserRole.PLAYER
        else:
            await update.message.reply_text("❌ Допустимые роли: moderator, admin, player")
            return
        
        # В реальной системе нужно найти пользователя по username
        # Пока используем заглушку
        target_user = await self.user_service.get_user(update.effective_user.id)  # Заглушка
        if not target_user:
            await update.message.reply_text(f"❌ Пользователь @{target_username} не найден")
            return
        
        result = await self.admin_service.handle_role_command(
            admin_user, target_user.id, role
        )
        
        await update.message.reply_text(result["message"])
    
    async def _handle_admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_user: User):
        """Обработка подкоманды /adm stats"""
        chat_id = update.effective_chat.id
        
        result = await self.admin_service.handle_chat_stats_command(
            admin_user, str(chat_id)
        )
        
        await update.message.reply_text(result["message"])
    
    async def _handle_admin_end_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_user: User):
        """Обработка подкоманды /adm end_session"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ Использование: /adm end_session [session_id]")
            return
        
        session_id = context.args[1]
        
        result = await self.admin_service.handle_force_end_session(
            admin_user, session_id
        )
        
        await update.message.reply_text(result["message"])
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных сообщений"""
        # В будущем можно добавить обработку сообщений для игр
        pass