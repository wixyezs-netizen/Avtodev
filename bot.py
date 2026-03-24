#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(__file__))

from config import TELEGRAM_TOKEN, PROJECT_PATH, ALLOWED_USERS, AI_PROVIDER
from code_agent import CodeAgent

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация агента
agent = CodeAgent(PROJECT_PATH, provider=AI_PROVIDER)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Доступ запрещён")
        return
    
    await update.message.reply_text(
        "🤖 **AutoDev Bot**\n\n"
        f"📁 Проект: `{PROJECT_PATH}`\n"
        f"🧠 AI: Встроенный\n\n"
        "**Что я умею:**\n"
        "• Создавать функции и классы\n"
        "• Добавлять API endpoints\n"
        "• Редактировать конфиги\n"
        "• Создавать новые файлы\n\n"
        "**Примеры:**\n"
        "`Создай функцию get_users в файле app.py`\n"
        "`Добавь endpoint /health в main.py`\n"
        "`Создай класс DatabaseConnection`",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Доступ запрещён")
        return
    
    task = update.message.text
    logger.info(f"Новая задача от {user_id}: {task}")
    
    status_msg = await update.message.reply_text("🔄 **Анализирую задачу...**", parse_mode='Markdown')
    
    try:
        changes = await agent.execute_task(task)
        
        if "error" in changes:
            await status_msg.edit_text(f"❌ **Ошибка:**\n{changes['error']}", parse_mode='Markdown')
            return
        
        modified_files = agent.apply_changes(changes)
        
        if modified_files:
            result_text = (
                f"✅ **Готово!**\n\n"
                f"📝 **Изменения:**\n{changes.get('description', 'Нет описания')}\n\n"
                f"📁 **Файлы:**\n"
            )
            for file in modified_files:
                result_text += f"• `{file}`\n"
            
            await status_msg.edit_text(result_text, parse_mode='Markdown')
            logger.info(f"✅ Изменены: {modified_files}")
        else:
            await status_msg.edit_text("⚠️ **Нет изменений**\nПроверьте задачу.", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await status_msg.edit_text(f"❌ **Ошибка:**\n```\n{str(e)}\n```", parse_mode='Markdown')

def main():
    if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN":
        print("❌ Укажите TELEGRAM_TOKEN в файле .env")
        sys.exit(1)
    
    print(f"🤖 AutoDev Bot запущен!")
    print(f"📁 Проект: {PROJECT_PATH}")
    print("=" * 50)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()