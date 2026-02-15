import logging
import os
import time
import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import Conflict, NetworkError

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
BRANCH_NAME = os.getenv("BRANCH_NAME", "main")

if REPO_NAME:
    DATA_URL = f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH_NAME}/data.json"
else:
    DATA_URL = None
    logger.error("錯誤: 未設定 REPO_NAME 環境變數，無法組建 DATA_URL")
# -----------------------

async def fetch_buttons():
    """從 GitHub 獲取最新的按鈕配置"""
    if not DATA_URL:
        return []

    try:
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        logger.error(f"無法獲取或解析 data.json ({DATA_URL}): {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /start 指令"""
    logger.info(f"收到來自 {update.effective_user.id} 的 /start 指令")
    
    button_data = await fetch_buttons()
    
    if not button_data:
        await update.message.reply_text("目前無法獲取群組列表，請檢查 Bot 設定或稍後再試。")
        return

    keyboard = []
    for item in button_data:
        desc = item.get("description", "未命名群組")
        link = item.get("link", "#")
        keyboard.append([InlineKeyboardButton(desc, url=link)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "各位落難哥布林，請點擊以下群組連結進入山洞",
        reply_markup=reply_markup
    )

def main():
    if not BOT_TOKEN:
        logger.error("錯誤: 未設定 BOT_TOKEN 環境變數")
        return
    
    if not REPO_NAME:
        logger.error("錯誤: 未設定 REPO_NAME 環境變數")

    logger.info(f"正在初始化 Bot Application... (目標 Repo: {REPO_NAME})")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    max_retries = 20
    retry_delay = 5

    logger.info("開始運行 Polling...")
    
    attempt = 0
    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
            break
        except Conflict:
            attempt += 1
            logger.warning(f"檢測到 Token 衝突 (Conflict)！可能是舊 Container 尚未關閉。正在重試 ({attempt})...")
            time.sleep(retry_delay)
        except NetworkError:
            attempt += 1
            logger.warning(f"網絡錯誤。正在重試 ({attempt})...")
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"發生未預期的錯誤: {e}")
            logger.info("5秒後重啟 Polling...")
            time.sleep(5)

if __name__ == '__main__':
    main()