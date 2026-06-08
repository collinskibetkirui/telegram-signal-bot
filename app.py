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
    # Create a new event loop for this thread and run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_main())

if __name__ == "__main__":
    # Start the bot in a separate daemon thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Start the Flask server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)