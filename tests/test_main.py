import pytest
from unittest.mock import patch
from src.main import main

@patch('src.main.os.getenv')
def test_main_output(mock_getenv, capfd):
    # Mock environment variables
    mock_getenv.side_effect = lambda key: {
        'API_KEY': 'mock_api_key',
        'DATABASE_URL': 'mock_database_url'
    }.get(key)
    
    main()
    captured = capfd.readouterr()
    assert "API Key: mock_api_key" in captured.out
    assert "Database URL: mock_database_url" in captured.out
