from flask import Flask
import threading
import os
import asyncio
from bot import main as bot_main

app = Flask(__name__)

@app.route('/')
def home():
    return "Signal Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Run the bot with asyncio"""
    asyncio.run(bot_main())

if __name__ == "__main__":
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Start Flask server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)