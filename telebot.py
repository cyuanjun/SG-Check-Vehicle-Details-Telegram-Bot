from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
from dotenv import load_dotenv
import os, time

import scraper
import checksum



# dict to store user cooldowns for rate limiting
last_used = {}
USER_COOLDOWN_SEC = 15

# loading api key and bot username
load_dotenv()
API_KEY = os.getenv("TELE_API_KEY")

if not API_KEY:
    raise RuntimeError("TELE_API_KEY not set")



# function to show that app is still running
async def running(context):

    msg = f"[{datetime.now().isoformat(timespec='seconds')}] Bot is running..."
    log_event(msg)



# function to log events
def log_event(msg):
    print(msg)
    with open("bot_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# function to check if user is rate limted
def is_rate_limited(user_id):
    now = time.monotonic()
    last = last_used.get(user_id, 0)
    if now - last < USER_COOLDOWN_SEC:
        return True
    last_used[user_id] = now
    return False



# defining /start
async def start_command(update, context):

    # logging
    user = update.effective_user
    msg = f"[{datetime.now().isoformat(timespec='seconds')}] Handling /start from {user}, {user.id}"
    log_event(msg)

    await update.message.reply_text(
        "Check_Vehicle_Details_Bot started!\n\n"
        "Usage:\n"
        " - /check <vehicle_plate>\n\n"
        "Check out my Github for more information!\n"
        "https://github.com/cyuanjun/SG-Check-Vehicle-Details-Telegram-Bot \n"
    )



# defining /help
async def help_command(update, context):

    # logging
    user = update.effective_user
    msg = f"[{datetime.now().isoformat(timespec='seconds')}] Handling /help from {user}, {user.id}"
    log_event(msg)

    await update.message.reply_text(
        "================================\n"
        f"{'Help':^68}\n"
        "================================\n"
        "Enter a carplate to check vehicle details!\n"
        " - /check <vehicle_plate>\n"
        )



# defining /check <vehicle_plate>
async def check_command(update, context):

    user = update.effective_user
    if user is None:
        msg = "Please wait a bit before trying again."
        log_event(msg)
        await update.message.reply_text(msg)
        return
    
    user_id = user.id

    msg = f"[{datetime.now().isoformat(timespec='seconds')}] Handling /check from {user}, {user_id}"
    msg += f"\n                      User Input: {' '.join(context.args)}"
    log_event(msg)

    if not context.args:
        await update.message.reply_text("Usage: /check <vehicle_plate>")
        return

    if is_rate_limited(user_id):
        msg = "                      Rate limited to 15s/request to prevent spam."
        msg += "\n                      Please wait a bit before trying again."
        log_event(msg)
        await update.message.reply_text(msg)
        return
    
    reply = handle_check(plate)

    plate = context.args[0]
    await update.message.reply_text(
        reply,
        reply_to_message_id=update.message.message_id
        )



# handle /check logic
def handle_check(plate):
    plate = plate.upper()

    # run checksum on plate
    status_msg, valid_plate = checksum.plate_check(plate)

    # return result / error msg
    if valid_plate:
        result = scraper.main(plate)
        return result
    
    else: 
        return status_msg



# Error
async def error(update, context):
    msg = f"[{datetime.now().isoformat(timespec='seconds')}] Update {update} caused error {context.error}"
    log_event(msg)



def main():
    # create app and pass bot's token
    app = Application.builder().token(API_KEY).build()

    # command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check_command))

    # error handlers
    app.add_error_handler(error)

    # Polls bot
    msg = "=" * 200
    msg += f"\n[{datetime.now().isoformat(timespec='seconds')}] Bot Started"
    log_event(msg)
    app.job_queue.run_repeating(running, interval=60, first=3)

    try:
        app.run_polling(poll_interval=3)

    except Exception as e:
        msg = f"[{datetime.now().isoformat(timespec='seconds')}] Bot stopped unexpectedly: {e}"
        log_event(msg)
        raise

    finally:
        print("Bot stopped.")



if __name__ == "__main__":
    main()












