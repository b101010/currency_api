import pytest
import io
import pandas as pd
import numpy as np
import requests
import zipfile
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError
from tools import ZipDownloader, CurrencyExtractor, Unzipper


def test_zip_downloader_get_file_successful_download():

    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.content = b'0123456789'

    # Mock the requests.get method
    with patch('tools.requests.get') as mock_get:
        mock_get.return_value = mock_response

        zip_downloader = ZipDownloader('http://whatever.com/file.zip')
        result = zip_downloader.get_file()

        # Check if the result is an instance of BytesIO
        assert isinstance(result, io.BytesIO)

        # Check if the content is as expected
        assert result.getvalue() == b'0123456789'


def test_zip_downloader_get_file_http_error():

    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.content = b'0123456789'

    # Mock the requests.get method
    with patch('tools.requests.get') as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(HTTPError, match='HTTP error 404'):
            zip_downloader = ZipDownloader('http://whatever.com/file.zip')
            zip_downloader.get_file()


@pytest.fixture
def sample_dataframe():
    # Create sample dataframe
    data = {
        'Date': ['2023-11-20', '2023-11-21', '2023-11-22'],
        'USD': ['3.1415', '1.4142', '2.7182'],
        'SEK': ['6.6260', '9.1093', np.nan]
    }
    return pd.DataFrame(data)


def test_currency_extractor_correct_result(sample_dataframe):
    currency_extractor = CurrencyExtractor(
        '2023-11-20', 'USD', sample_dataframe)
    result = currency_extractor.get_value()

    assert result == {
        'currency': 'USD',
        'date': '2023-11-20',
        'value': '3.1415'}


def test_currency_extractor_wrong_date(sample_dataframe):
    currency_extractor = CurrencyExtractor(
        '2023-11-19', 'USD', sample_dataframe)

    with pytest.raises(Exception, match="Date not available: 2023-11-19"):
        currency_extractor.get_value()


def test_currency_extractor_wrong_currency(sample_dataframe):
    currency_extractor = CurrencyExtractor(
        '2023-11-20', 'ASD', sample_dataframe)

    with pytest.raises(Exception, match="Currency not available: ASD"):
        currency_extractor.get_value()


def test_currency_extractor_nan_value(sample_dataframe):
    currency_extractor = CurrencyExtractor(
        '2023-11-22', 'SEK', sample_dataframe)

    with pytest.raises(Exception, match="Currency data not available: SEK, 2023-11-22"):
        currency_extractor.get_value()


@pytest.fixture
def sample_zip():
    # Create sample zip
    zip_buffer = io.BytesIO()

    file_contents = b'navigare necesse est'

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zip_file:
        zip_file.writestr('filename.txt', file_contents)

    return zip_buffer


def test_unzipper(sample_zip):
    unzipper = Unzipper('filename.txt', sample_zip)

    assert isinstance(unzipper.get_data(), io.BytesIO)
    assert unzipper.get_data().getvalue() == b'navigare necesse est'
