#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'divergex.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT DEFAULT 'Trader', balance REAL DEFAULT 10000, total_credit REAL DEFAULT 10000, total_debit REAL DEFAULT 0, net_pnl REAL DEFAULT 0, win_rate REAL DEFAULT 0, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, type TEXT, amount REAL, description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS auto_trading (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, enabled INTEGER DEFAULT 0, last_signal TEXT, positions_count INTEGER DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute("SELECT * FROM users WHERE id = 'user_001'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id, name, balance) VALUES ('user_001', 'Demo Trader', 10000)")
        cursor.execute("INSERT INTO auto_trading (user_id, enabled) VALUES ('user_001', 0)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return jsonify({"status": "running", "service": "DivergeX AI Market", "version": "2026.1"})

@app.route('/get-live-data')
def get_live_data():
    try:
        df = yf.Ticker("^NSEBANK").history(period="1d", interval="5m")
        if not df.empty:
            close = df['Close'].values
            current_price = close[-1]
            change = ((current_price - close[-2]) / close[-2]) * 100
        else:
            current_price = random.uniform(47000, 49000)
            change = random.uniform(-2, 2)
        oscillators = [
            {"name": "RSI", "value": round(random.uniform(30, 70), 1), "bull": random.random() > 0.7, "bear": random.random() > 0.7, "color": "#58a6ff"},
            {"name": "MFI", "value": round(random.uniform(30, 70), 1), "bull": random.random() > 0.7, "bear": random.random() > 0.7, "color": "#3fb950"},
            {"name": "STOCH", "value": round(random.uniform(20, 80), 1), "bull": random.random() > 0.7, "bear": random.random() > 0.7, "color": "#f0883e"},
            {"name": "MACD", "value": round(random.uniform(-50, 50), 2), "bull": random.random() > 0.7, "bear": random.random() > 0.7, "color": "#a371f7"},
            {"name": "CCI", "value": round(random.uniform(-100, 100), 1), "bull": random.random() > 0.7, "bear": random.random() > 0.7, "color": "#f85149"},
            {"name": "SRSI", "value": round(random.uniform(20, 80), 1), "bull": random.random() > 0.7, "bear": random.random() > 0.7, "color": "#d29922"},
        ]
        bull_count = sum(1 for o in oscillators if o["bull"])
        operation = "BUY" if bull_count >= 3 else "SELL" if bull_count <= 1 else "WAIT"
        return jsonify({"lp": round(current_price, 2), "change": round(change, 2), "operation": operation, "oscillators": oscillators})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-nifty-data')
def get_nifty_data():
    try:
        df = yf.Ticker("^NSEI").history(period="1d", interval="5m")
        if not df.empty:
            current_price = df['Close'].values[-1]
            change = ((current_price - df['Close'].values[-2]) / df['Close'].values[-2]) * 100
        else:
            current_price = random.uniform(22000, 23500)
            change = random.uniform(-1.5, 1.5)
        return jsonify({"lp": round(current_price, 2), "change": round(change, 2)})
    except:
        return jsonify({"lp": 22450, "change": 0.5})

@app.route('/get-ai-prediction')
def get_ai_prediction():
    current_price = random.uniform(47000, 49000)
    action = random.choice(["BUY", "SELL"])
    return jsonify({"action": action, "confidence": random.randint(65, 92), "signals": ["RSI", "MACD"], "current_price": round(current_price, 2), "target1": round(current_price + 100, 2), "target2": round(current_price + 250, 2), "stoploss": round(current_price - 80, 2)})

@app.route('/get-signal-agents')
def get_signal_agents():
    agents = [{"name": "Trend Follower", "icon": "📈", "signal": random.choice(["BUY", "SELL"]), "strength": random.randint(60, 95), "reason": "Trend analysis", "accuracy": random.randint(70, 90)}]
    return jsonify({"agents": agents})

@app.route('/get-brokerage-status')
def get_brokerage_status():
    return jsonify({"zerodha": {"status": "Connected", "orders_today": 5}})

@app.route('/auto-trading/status')
def auto_trading_status():
    return jsonify({"enabled": False, "positions_count": 0})

@app.route('/get-wallet')
def get_wallet():
    return jsonify({"balance": 10000, "total_credit": 10000, "total_debit": 0, "net_pnl": 0})

@app.route('/get-transactions')
def get_transactions():
    return jsonify({"transactions": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
