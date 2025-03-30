import pytest
from unittest.mock import patch, MagicMock
from exchange_service.client import ExchangeRateClient
import requests
import os

@pytest.fixture
def mock_env():
    with patch.dict('os.environ', {
        'EXCHANGE_RATE_API_KEY': 'test_key',
        'EXCHANGE_RATE_BASE_URL': 'http://api.test'
    }):
        yield

class TestExchangeRateClient:
    @patch('requests.get')
    def test_get_latest_rates_success(self, mock_get, mock_env):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': True,
            'base': 'SGD',
            'rates': {'EUR': 0.85, 'GBP': 0.75}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test
        result = ExchangeRateClient.get_latest_rates('USD', 'EUR,GBP')
        
        # Assertions
        assert result['base'] == 'USD'
        assert 'EUR' in result['rates']
        mock_get.assert_called_with(
            'http://api.test/latest',
            params={'access_key': 'test_key', 'base': 'USD', 'symbols': 'EUR,GBP'}
        )

    @patch('requests.get')
    def test_get_latest_rates_failure(self, mock_get, mock_env):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API error")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            ExchangeRateClient.get_latest_rates('SGD')

    @patch.object(ExchangeRateClient, 'get_latest_rates')
    def test_convert_amount(self, mock_get_rates, mock_env):
        mock_get_rates.return_value = {
            'success': True,
            'rates': {'EUR': 0.85}
        }
        
        result = ExchangeRateClient.convert_amount('SGD', 'EUR', 100)
        
        assert result == 85.0
        mock_get_rates.assert_called_with('SGD', 'EUR')

    @patch.object(ExchangeRateClient, 'get_latest_rates')
    def test_convert_amount_missing_rate(self, mock_get_rates, mock_env):
        mock_get_rates.return_value = {
            'success': True,
            'rates': {'GBP': 0.75}  # No EUR rate
        }
        
        with pytest.raises(KeyError):
            ExchangeRateClient.convert_amount('SGD', 'EUR', 100)