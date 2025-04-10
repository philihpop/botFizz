import os
from threading import Thread
from time import sleep
import time

from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.updater import Updater
from telegram.update import Update

from scraper import FizzScraper
REPLACE_WITH_YOUR_TELEGRAM_TOKEN = 'REPLACE_WITH_YOUR_TELEGRAM_TOKEN'
PORT = int(os.environ.get('PORT', 8443))
telegram_token = os.environ.get("TG_TOKEN", "REPLACE_WITH_YOUR_TELEGRAM_TOKEN")
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 120))  # Default 2 minutes (120 seconds)


class TelegramHandler:
    def __init__(self):
        self.stop_thread = False
        self.running_thread = None
        self.scraper = FizzScraper()
        self.updater = Updater(telegram_token, use_context=True)

        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler('start', self.start))
        dp.add_handler(CommandHandler('help', self.help))
        dp.add_handler(CommandHandler('check', self.check_fizz))
        dp.add_handler(CommandHandler('stop', self.stop))

    def start_polling(self):
        self.updater.start_polling()

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hello! I'm The Fizz Leiden Room Monitor. I'll check periodically if rooms become available and notify you."
        )
        
        # Don't start a new thread if one is already running
        if self.running_thread and self.running_thread.is_alive():
            update.message.reply_text("Monitoring is already active!")
            return
            
        self.stop_thread = False
        self.running_thread = Thread(target=self.monitor_daemon, args=(update, context))
        self.running_thread.start()
        update.message.reply_text(f"Started monitoring The Fizz Leiden. Checking every {CHECK_INTERVAL} seconds.")

    def help(self, update: Update, context: CallbackContext):
        update.message.reply_text("""
*The Fizz Leiden Room Monitor*

Available Commands:
• /start - Start monitoring for room availability
• /check - Check availability right now
• /help - Show this help message
• /stop - Stop the monitoring

I'll notify you when rooms become available at The Fizz Leiden.
        """, parse_mode='Markdown')

    def monitor_daemon(self, update: Update, context: CallbackContext):
        last_notified = 0  # Time since last notification
        
        while not self.stop_thread:
            try:
                result = self.scraper.check_availability()
                
                # If rooms are available and we haven't notified recently
                if result.get("available", False) and (time.time() - last_notified) > 1200:  # Notify once per hour max
                    message = f"🎉 *ROOMS AVAILABLE at The Fizz Leiden!* 🎉\n\n{result['message']}\n\nCheck now: {result['url']}"
                    update.message.reply_text(message, parse_mode='Markdown')
                    last_notified = time.time()
                    
                # Sleep for the check interval
                sleep(CHECK_INTERVAL)
                
            except Exception as e:
                error_msg = f"Error in monitor thread: {str(e)}"
                print(error_msg)
                try:
                    update.message.reply_text(f"⚠️ Error: {error_msg}\nWill try again in 5 minutes.")
                except:
                    pass
                sleep(300)  # Sleep 5 minutes on error
        
        update.message.reply_text("Monitoring stopped.")

    def check_fizz(self, update: Update, context: CallbackContext):
        update.message.reply_text("Checking The Fizz Leiden now...")
        
        result = self.scraper.check_availability()
        
        if result.get("available", False):
            message = f"🎉 *ROOMS AVAILABLE!* 🎉\n\n{result['message']}\n\nCheck now: {result['url']}"
        elif "error" in result:
            message = f"⚠️ *Error checking availability*\n\n{result['error']}"
        else:
            message = f"😔 {result['message']}"
            
        update.message.reply_text(message, parse_mode='Markdown')

    def stop(self, update: Update, context: CallbackContext):
        if not self.running_thread or not self.running_thread.is_alive():
            update.message.reply_text("No monitoring is currently active.")
            return
            
        update.message.reply_text("Stopping the monitoring...")
        self.stop_thread = True
        self.running_thread.join()
        update.message.reply_text("Monitoring has been stopped.")


if __name__ == "__main__":
    handler = TelegramHandler()
    print("Running locally")
    handler.start_polling()