from flask import Flask
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Signal Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    # Start bot in a subprocess
    subprocess.Popen(["python", "bot.py"])
    
    # Start Flask server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)