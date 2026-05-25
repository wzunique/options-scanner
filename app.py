"""
Options Flow Scanner Backend - Railway Optimized Version
Real-time options data from yfinance with scoring algorithm
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import os
import sys

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Global state
scan_results = []
is_scanning = False
scan_lock = threading.Lock()

# Popular stocks to scan
STOCK_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA', 'SPY', 'QQQ', 'IWM', 'XLE']

class OptionsScanner:
    def __init__(self):
        self.results = []
    
    def calculate_score(self, vol_oi, ask_side, sweep, otm, iv_sync, consecutive, price_still):
        """Calculate score based on conditions"""
        score = 0
        
        if vol_oi > 1.5:  # Volume >> OI
            score += 20
        elif vol_oi > 1.2:
            score += 15
        
        if ask_side:
            score += 17
        
        if sweep:
            score += 17
        
        if otm:
            score += 14
        
        if iv_sync:
            score += 14
        
        if price_still:
            score += 12
        
        # Consecutive occurrences (max +6)
        score += min(6, consecutive)
        
        return min(100, score)
    
    def get_options_data(self, symbol):
        """Fetch options data from yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get stock price
            hist = ticker.history(period='1d')
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Get expirations
            expirations = ticker.options
            if not expirations:
                return None
            
            # Get nearest expiration
            exp_date = expirations[0]
            options_chain = ticker.option_chain(exp_date)
            
            calls = options_chain.calls
            puts = options_chain.puts
            
            # Calculate metrics
            total_call_volume = calls['volume'].sum()
            total_put_volume = puts['volume'].sum()
            total_call_oi = calls['openInterest'].sum()
            total_put_oi = puts['openInterest'].sum()
            
            vol_oi_ratio = (total_call_volume + total_put_volume) / max(1, total_call_oi + total_put_oi)
            
            # Detect conditions
            ask_side = (calls['ask'] > calls['bid']).sum() > len(calls) * 0.6
            sweep = (calls['volume'] > calls['openInterest']).sum() > 0
            
            # OTM detection
            otm_calls = calls[calls['strike'] > current_price * 1.02]
            otm = len(otm_calls[otm_calls['volume'] > 0]) > 0
            
            # IV sync
            avg_iv = calls['impliedVolatility'].mean()
            iv_sync = avg_iv > 0.3
            
            # Price still
            price_still = True
            
            # Consecutive
            consecutive = min(8, int(total_call_volume / 100) if total_call_volume > 0 else 0)
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'expiration': exp_date,
                'vol_oi_ratio': round(vol_oi_ratio, 2),
                'total_volume': int(total_call_volume + total_put_volume),
                'total_oi': int(total_call_oi + total_put_oi),
                'avg_iv': round(avg_iv, 3),
                'ask_side': ask_side,
                'sweep': sweep,
                'otm': otm,
                'iv_sync': iv_sync,
                'price_still': price_still,
                'consecutive': consecutive
            }
        
        except Exception as e:
            print(f"Error fetching {symbol}: {e}", file=sys.stderr)
            return None
    
    def scan_all(self):
        """Scan all symbols and return ranked results"""
        global is_scanning, scan_results
        
        is_scanning = True
        results = []
        
        for symbol in STOCK_SYMBOLS:
            try:
                data = self.get_options_data(symbol)
                if data:
                    # Calculate score
                    score = self.calculate_score(
                        vol_oi=data['vol_oi_ratio'],
                        ask_side=data['ask_side'],
                        sweep=data['sweep'],
                        otm=data['otm'],
                        iv_sync=data['iv_sync'],
                        consecutive=data['consecutive'],
                        price_still=data['price_still']
                    )
                    
                    # Determine status
                    if score >= 85:
                        status = 'excellent'
                    elif score >= 70:
                        status = 'good'
                    elif score >= 50:
                        status = 'fair'
                    else:
                        status = 'poor'
                    
                    results.append({
                        'id': len(results) + 1,
                        'symbol': symbol,
                        'score': score,
                        'status': status,
                        'timestamp': datetime.now().isoformat(),
                        'data': data,
                        'conditions': {
                            'volumeOI': data['vol_oi_ratio'] > 1.5,
                            'askSide': data['ask_side'],
                            'sweep': data['sweep'],
                            'otm': data['otm'],
                            'ivSync': data['iv_sync'],
                            'priceStill': data['price_still'],
                            'consecutive': data['consecutive']
                        }
                    })
            
            except Exception as e:
                print(f"Error processing {symbol}: {e}", file=sys.stderr)
                continue
            
            time.sleep(0.5)  # Rate limiting
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        with scan_lock:
            scan_results = results
        
        is_scanning = False
        return results

scanner = OptionsScanner()

# Routes
@app.route('/', methods=['GET'])
def index():
    """Health check and info"""
    return jsonify({
        'status': 'ok',
        'service': 'Options Flow Scanner',
        'version': '2.0',
        'endpoints': [
            'GET /',
            'GET /health',
            'POST /api/scan',
            'GET /api/results',
            'GET /api/symbol/<symbol>',
            'GET /api/status'
        ]
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok'}), 200

@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start background scan"""
    global is_scanning
    
    if is_scanning:
        return jsonify({'error': 'Scan already in progress'}), 400
    
    # Run scan in background
    thread = threading.Thread(target=scanner.scan_all)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'scanning started'}), 200

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get current scan results"""
    with scan_lock:
        return jsonify({
            'results': scan_results,
            'is_scanning': is_scanning,
            'total': len(scan_results),
            'excellent': sum(1 for r in scan_results if r['status'] == 'excellent'),
            'good': sum(1 for r in scan_results if r['status'] == 'good')
        }), 200

@app.route('/api/symbol/<symbol>', methods=['GET'])
def get_symbol_data(symbol):
    """Get data for specific symbol"""
    data = scanner.get_options_data(symbol.upper())
    if data:
        return jsonify(data), 200
    return jsonify({'error': 'Failed to fetch data'}), 404

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get scanning status"""
    return jsonify({
        'is_scanning': is_scanning,
        'results_count': len(scan_results)
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Railway production deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

