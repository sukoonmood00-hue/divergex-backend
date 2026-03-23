import os
from flask import Flask, jsonify
import yfinance as yf
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "running", "message": "DivergeX AI Market Backend", "service": "Spider Quant Flask API"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Service is running correctly"})

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    try:
        stock = yf.Ticker(symbol.upper() + ".NS")  # NSE stocks
        data = stock.history(period="1mo")
        if data.empty:
            stock = yf.Ticker(symbol.upper())  # Try without .NS for US stocks
            data = stock.history(period="1mo")
        
        if data.empty:
            return jsonify({"error": f"No data found for {symbol}"}), 404
        
        latest = data.iloc[-1]
        return jsonify({
            "symbol": symbol.upper(),
            "price": float(latest['Close']),
            "change": float(latest['Close'] - data.iloc[-2]['Close']) if len(data) > 1 else 0,
            "change_percent": float((latest['Close'] - data.iloc[-2]['Close']) / data.iloc[-2]['Close'] * 100) if len(data) > 1 else 0,
            "volume": int(latest['Volume']),
            "high": float(latest['High']),
            "low": float(latest['Low']),
            "open": float(latest['Open'])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/market-overview')
def market_overview():
    try:
        # Indian market indices
        nifty = yf.Ticker("^NSEI")
        sensex = yf.Ticker("^BSESN")
        banknifty = yf.Ticker("^NSEBANK")
        
        def get_index_data(ticker):
            data = ticker.history(period="2d")
            if len(data) >= 2:
                latest = data.iloc[-1]
                prev = data.iloc[-2]
                return {
                    "price": round(float(latest['Close']), 2),
                    "change": round(float(latest['Close'] - prev['Close']), 2),
                    "change_percent": round(float((latest['Close'] - prev['Close']) / prev['Close'] * 100), 2)
                }
            return None
        
        return jsonify({
            "nifty50": get_index_data(nifty),
            "sensex": get_index_data(sensex),
            "banknifty": get_index_data(banknifty),
            "timestamp": pd.Timestamp.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-gainers')
def top_gainers():
    # Demo data for top gainers
    return jsonify({
        "gainers": [
            {"symbol": "ADANIENT", "change_percent": 5.2, "price": 2450.50},
            {"symbol": "TATASTEEL", "change_percent": 4.1, "price": 145.30},
            {"symbol": "SBIN", "change_percent": 3.8, "price": 625.75}
        ]
    })

@app.route('/api/top-losers')
def top_losers():
    # Demo data for top losers
    return jsonify({
        "losers": [
            {"symbol": "WIPRO", "change_percent": -2.1, "price": 445.20},
            {"symbol": "INFY", "change_percent": -1.8, "price": 1456.80},
            {"symbol": "TCS", "change_percent": -1.2, "price": 3542.50}
        ]
    })

@app.route('/api/sector-performance')
def sector_performance():
    return jsonify({
        "sectors": [
            {"name": "Banking", "change_percent": 1.2},
            {"name": "IT", "change_percent": -0.8},
            {"name": "Pharma", "change_percent": 0.5},
            {"name": "Auto", "change_percent": 1.5},
            {"name": "Energy", "change_percent": -0.3}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
