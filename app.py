"""
Options Flow Scanner Backend - Enhanced with Call/Put Ratio + CORS Fix
"""

from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import threading
import time
import os
import sys

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

scan_results = []
is_scanning = False
scan_lock = threading.Lock()

STOCK_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA', 'SPY', 'QQQ', 'IWM', 'XLE']

class OptionsScanner:
    def calculate_score(self, vol_oi, ask_side, sweep, otm, iv_sync, consecutive, price_still):
        score = 0
        if vol_oi > 1.5:
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
        score += min(6, consecutive)
        return min(100, score)
    
    def get_options_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            expirations = ticker.options
            if not expirations:
                return None
            
            exp_date = expirations[0]
            options_chain = ticker.option_chain(exp_date)
            calls = options_chain.calls
            puts = options_chain.puts
            
            total_call_volume = calls['volume'].sum()
            total_put_volume = puts['volume'].sum()
            total_call_oi = calls['openInterest'].sum()
            total_put_oi = puts['openInterest'].sum()
            
            call_put_volume_ratio = total_call_volume / max(1, total_put_volume)
            call_put_oi_ratio = total_call_oi / max(1, total_put_oi)
            
            vol_oi_ratio = (total_call_volume + total_put_volume) / max(1, total_call_oi + total_put_oi)
            ask_side = (calls['ask'] > calls['bid']).sum() > len(calls) * 0.6
            sweep = (calls['volume'] > calls['openInterest']).sum() > 0
            otm_calls = calls[calls['strike'] > current_price * 1.02]
            otm = len(otm_calls[otm_calls['volume'] > 0]) > 0
            avg_call_iv = calls['impliedVolatility'].mean()
            avg_put_iv = puts['impliedVolatility'].mean()
            iv_sync = avg_call_iv > 0.3
            price_still = True
            consecutive = min(8, int(total_call_volume / 100) if total_call_volume > 0 else 0)
            
            iv_call_put_ratio = avg_call_iv / max(0.001, avg_put_iv)
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'expiration': exp_date,
                'vol_oi_ratio': round(vol_oi_ratio, 2),
                'total_volume': int(total_call_volume + total_put_volume),
                'total_oi': int(total_call_oi + total_put_oi),
                'call_volume': int(total_call_volume),
                'put_volume': int(total_put_volume),
                'call_volume_ratio': round(call_put_volume_ratio, 2),
                'call_oi': int(total_call_oi),
                'put_oi': int(total_put_oi),
                'call_oi_ratio': round(call_put_oi_ratio, 2),
                'avg_call_iv': round(avg_call_iv, 3),
                'avg_put_iv': round(avg_put_iv, 3),
                'iv_call_put_ratio': round(iv_call_put_ratio, 2),
                'ask_side': ask_side,
                'sweep': sweep,
                'otm': otm,
                'iv_sync': iv_sync,
                'price_still': price_still,
                'consecutive': consecutive
            }
        except Exception as e:
            print(f"Error {symbol}: {e}", file=sys.stderr)
            return None
    
    def scan_all(self):
        global is_scanning, scan_results
        is_scanning = True
        results = []
        
        for symbol in STOCK_SYMBOLS:
            try:
                data = self.get_options_data(symbol)
                if data:
                    score = self.calculate_score(
                        vol_oi=data['vol_oi_ratio'],
                        ask_side=data['ask_side'],
                        sweep=data['sweep'],
                        otm=data['otm'],
                        iv_sync=data['iv_sync'],
                        consecutive=data['consecutive'],
                        price_still=data['price_still']
                    )
                    
                    status = 'excellent' if score >= 85 else 'good' if score >= 70 else 'fair' if score >= 50 else 'poor'
                    
                    results.append({
                        'id': len(results) + 1,
                        'symbol': symbol,
                        'score': score,
                        'status': status,
                        'timestamp': __import__('datetime').datetime.now().isoformat(),
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
            
            time.sleep(0.5)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        with scan_lock:
            scan_results = results
        
        is_scanning = False

scanner = OptionsScanner()

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    return jsonify({'status': 'ok', 'service': 'Options Flow Scanner'}), 200

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/scan', methods=['POST', 'OPTIONS'])
def start_scan():
    global is_scanning
    if is_scanning:
        return jsonify({'error': 'Scan in progress'}), 400
    thread = threading.Thread(target=scanner.scan_all)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started'}), 200

@app.route('/api/results', methods=['GET', 'OPTIONS'])
def get_results():
    with scan_lock:
        return jsonify({
            'results': scan_results,
            'is_scanning': is_scanning,
            'total': len(scan_results),
            'excellent': sum(1 for r in scan_results if r['status'] == 'excellent'),
            'good': sum(1 for r in scan_results if r['status'] == 'good')
        }), 200

@app.route('/api/symbol/<symbol>', methods=['GET', 'OPTIONS'])
def get_symbol_data(symbol):
    data = scanner.get_options_data(symbol.upper())
    return jsonify(data) if data else jsonify({'error': 'Failed'}), 200 if data else 404

@app.route('/api/status', methods=['GET', 'OPTIONS'])
def get_status():
    return jsonify({'is_scanning': is_scanning, 'count': len(scan_results)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
