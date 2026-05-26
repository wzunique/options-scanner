import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'message': 'Options Scanner Backend'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/scan', methods=['POST'])
def scan():
    return jsonify({'status': 'started'}), 200

@app.route('/api/results', methods=['GET'])
def results():
    return jsonify({'results': [], 'is_scanning': False, 'total': 0}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}", file=sys.stderr)
    sys.stderr.flush()
    
    # Production mode - no debug, threaded
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True,
        use_reloader=False
    )
