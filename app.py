import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
# Enable CORS for all routes, allowing your static site to call this API
CORS(app)

# Configuration for APIs
API_CONFIG = {
    'av': {
        'base': 'https://www.alphavantage.co/query',
        'key': os.environ.get('AV_KEY', 'JQQUUJQRAX8TLXSM')
    },
    'ms': {
        'base': 'http://api.marketstack.com/v1',
        'key': os.environ.get('MS_KEY', 'adc91e9b5f1decaabf6d74dc20a4416f')
    },
    'fmp': {
        'base': 'https://financialmodelingprep.com/api/v3',
        'key': os.environ.get('FMP_KEY', 'zZ5zECyopZEcPtKvkqlb1R52jv2vFusj')
    },
    'fh': {
        'base': 'https://finnhub.io/api/v1',
        'key': os.environ.get('FH_KEY', 'd22igc9r01qr7ajlkob0d22igc9r01qr7ajlkobg')
    }
}

@app.route('/proxy/<service>', methods=['GET'])
def proxy(service):
    if service not in API_CONFIG:
        return jsonify({'error': 'Invalid service'}), 400
    
    config = API_CONFIG[service]
    params = request.args.to_dict()
    
    # Inject API Key into parameters based on service requirements
    if service == 'av':
        params['apikey'] = config['key']
        url = config['base']
    elif service == 'ms':
        params['access_key'] = config['key']
        url = f"{config['base']}/eod" # Hardcoded for EOD as per your static site needs
    elif service == 'fmp':
        # FMP embeds ticker in URL path usually, handling 'symbol' param specially
        symbol = params.get('symbol')
        if not symbol: return jsonify({'error': 'Symbol required'}), 400
        url = f"{config['base']}/historical-price-full/{symbol}"
        params['apikey'] = config['key']
        # Remove symbol from params to avoid double sending if needed, though FMP ignores extra params usually
    elif service == 'fh':
        params['token'] = config['key']
        url = f"{config['base']}/stock/candle"

    try:
        # Make the server-side request
        resp = requests.get(url, params=params)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Render provides a PORT env var
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
