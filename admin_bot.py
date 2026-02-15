import logging
import os
import json
import html
import time
from github import Github
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import Conflict, NetworkError

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
FILE_PATH = "data.json"
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

g = Github(GITHUB_TOKEN)

def is_admin(user_id):
    return user_id == ADMIN_ID

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    try:
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        data = json.loads(contents.decoded_content.decode())

        if not data:
            await update.message.reply_text("List is empty.")
            return

        msg = "<b>Current Group List:</b>\n\n"
        for idx, item in enumerate(data):
            safe_desc = html.escape(item.get('description', 'Untitled'))
            link = item.get('link', '#')
            msg += f"{idx + 1}. {safe_desc}\n   🔗 {link}\n\n"
        
        msg += "Use <code>/del ID</code> to delete."
        
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"Error: {str(e)}")

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Format error.\nUse: <code>/add Name https://t.me/link</code>", parse_mode=ParseMode.HTML)
        return

    link = args[-1]
    desc = " ".join(args[:-1])

    try:
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        data = json.loads(contents.decoded_content.decode())

        new_item = {"description": desc, "link": link}
        data.append(new_item)

        repo.update_file(
            contents.path,
            f"AdminBot: Add {desc}",
            json.dumps(data, indent=2, ensure_ascii=False),
            contents.sha
        )

        safe_desc = html.escape(desc)
        await update.message.reply_text(f"✅ Added:\n{safe_desc}\n{link}", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"Error: {str(e)}")

async def delete_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    try:
        if not context.args:
             await update.message.reply_text("Please provide an ID, e.g., <code>/del 1</code>", parse_mode=ParseMode.HTML)
             return
             
        idx = int(context.args[0]) - 1
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid ID.", parse_mode=ParseMode.HTML)
        return

    try:
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        data = json.loads(contents.decoded_content.decode())

        if idx < 0 or idx >= len(data):
            await update.message.reply_text("ID not found.")
            return

        removed = data.pop(idx)

        repo.update_file(
            contents.path,
            f"AdminBot: Remove {removed['description']}",
            json.dumps(data, indent=2, ensure_ascii=False),
            contents.sha
        )

        safe_desc = html.escape(removed['description'])
        await update.message.reply_text(f"🗑 Deleted:\n{safe_desc}", parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    msg = (
        "🤖 <b>Admin Commands</b>\n\n"
        "/list - View list\n"
        "/add [Name] [Link] - Add group\n"
        "/del [ID] - Delete group\n"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def main():
    if not ADMIN_BOT_TOKEN:
        print("Error: ADMIN_BOT_TOKEN not found")
        return

    application = ApplicationBuilder().token(ADMIN_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_groups))
    application.add_handler(CommandHandler("add", add_group))
    application.add_handler(CommandHandler("del", delete_group))

    print("Admin Bot is running...")

    attempt = 0
    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
            break
        except Conflict:
            attempt += 1
            logger.warning(f"Conflict detected. Retrying ({attempt})...")
            time.sleep(5)
        except NetworkError:
            logger.warning("Network error. Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()