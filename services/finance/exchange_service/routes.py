from flask import Blueprint, request, jsonify
from .client import ExchangeRateClient
from typing import Optional

bp = Blueprint('exchange', __name__, url_prefix='/exchange')

@bp.route('/rates', methods=['GET'])
def get_rates():
    base_currency = request.args.get('base', 'SGD')
    target_currencies = request.args.get('symbols')
    
    try:
        rates = ExchangeRateClient.get_latest_rates(base_currency, target_currencies)
        return jsonify(rates)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/convert', methods=['GET'])
def convert_currency():
    from_currency = request.args.get('from')
    to_currency = request.args.get('to')
    amount = float(request.args.get('amount'))
    
    if not all([from_currency, to_currency, amount]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        converted_amount = ExchangeRateClient.convert_amount(from_currency, to_currency, amount)
        return jsonify({
            'from': from_currency,
            'to': to_currency,
            'original_amount': amount,
            'converted_amount': converted_amount,
            'rate': converted_amount / amount
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400