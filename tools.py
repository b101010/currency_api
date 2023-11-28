import zipfile
import requests
import io
import os
import logging
from requests.exceptions import HTTPError
import pandas as pd


class ZipDownloader:
    """
    A class for downloading and retrieving a file from a given URL.

    Args:
        url (str): The URL from which to download the file.

    Methods:
        get_file(): Downloads the file from the specified URL and returns its content as a BytesIO object.

    """

    def __init__(self, url: str):
        self.url = url

    def get_file(self) -> io.BytesIO:
        """
        Downloads the file from the specified URL and returns its content as a BytesIO object.

        Returns:
            io.BytesIO: The content of the downloaded file as a BytesIO object.

        Raises:
            HTTPError: If the HTTP response status code is not 200.
        """

        try:
            response = self._make_request()
            self._check_response(response)

            zipped_data = io.BytesIO(response.content)
            logging.info(f"File successfully downloaded: {self.url}")
            return zipped_data

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise

    def _make_request(self) -> requests.Response:
        """
        Makes a request to the specified URL and returns the response object.

        Returns:
            requests.Response: The response object from the HTTP request.

        Raises:
            requests.RequestException: If an error occurs during the request.
        """

        try:
            return requests.get(self.url)
        except requests.RequestException as e:
            logging.error(f"Error making request: {str(e)}")
            raise

    def _check_response(self, response: requests.Response):
        """
        Checks the HTTP response status code. Raises HTTPError if the code is not 200.

        Args:
            response (requests.Response): The HTTP response object.

        Raises:
            HTTPError: If the HTTP response status code is not 200.
        """

        if response.status_code != 200:
            raise HTTPError(f"HTTP error {response.status_code}")


class Unzipper:
    """
    A class for extracting a specific file from a zipped data.

    Args:
        file_to_extract (str): The name of the file to be extracted.
        zipped_data (io.BytesIO): The zipped data as a BytesIO object.

    Methods:
        get_data(): Extracts the specified file from the zipped data and returns its content as a BytesIO object.

    """

    def __init__(self, file_to_extract: str, zipped_data: io.BytesIO):
        self.zipped_data = zipped_data
        self.file_to_extract = file_to_extract

    def get_data(self) -> io.BytesIO:
        """
        Extracts the specified file from the zipped data and returns its content as a BytesIO object.

        Returns:
            io.BytesIO: The content of the extracted file as a BytesIO object.

        Raises:
            FileNotFoundError: If the specified file is not found in the zipped data.
        """

        try:
            with zipfile.ZipFile(self.zipped_data, 'r') as zip_ref:
                return self._extract_file(zip_ref)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise

    def _extract_file(self, zip_ref: zipfile.ZipFile) -> io.BytesIO:
        """
        Extracts the specified file from the provided ZipFile object.

        Args:
            zip_ref (zipfile.ZipFile): The ZipFile object representing the zipped data.

        Returns:
            io.BytesIO: The content of the extracted file as a BytesIO object.

        Raises:
            FileNotFoundError: If the specified file is not found in the zipped data.
        """

        try:
            for info in zip_ref.infolist():
                if info.filename == self.file_to_extract:
                    with zip_ref.open(info) as file:
                        file_contents = io.BytesIO(file.read())
                        logging.info(
                            f"File successfully unzipped: {self.file_to_extract}")
                        return file_contents

            raise FileNotFoundError(
                f"Specified file not found: {self.file_to_extract}")
        except Exception as e:
            logging.error(f"Error extracting file: {str(e)}")
            raise


class CurrencyExtractor:
    """
    A class for extracting currency values based on a specific date from a DataFrame.

    Args:
        date (str): The date for which the currency value is to be extracted.
        currency (str): The currency for which the value is to be extracted.
        df (pd.DataFrame): The DataFrame containing currency data.

    Methods:
        get_value(): Extracts the currency value for the specified date and currency.

    """

    def __init__(self, date: str, currency: str, df: pd.DataFrame):
        self.date = date
        self.currency = currency
        self.df = df

    def get_value(self) -> dict:
        """
        Extracts the currency value for the specified date and currency.

        Returns:
            dict: A dictionary containing the currency, date, and value.

        Raises:
            Exception: If currency data is not available for the specified date and currency.
        """

        try:
            self._validate_inputs()

            result = self.df.loc[self.df['Date']
                                 == self.date, self.currency].values
            if pd.isna(result[0]):
                raise Exception(
                    f"Currency data not available: {self.currency}, {self.date}")

            result_dict = {
                'currency': self.currency,
                'date': self.date,
                'value': result[0]
            }

            return result_dict
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise

    def _validate_inputs(self):
        """
        Validates the inputs by checking if the currency and date are available in the DataFrame.

        Raises:
            Exception: If currency or date is not available in the DataFrame.
        """

        if self.currency not in self.df.columns.values or self.currency == 'Date':
            raise Exception(f"Currency not available: {self.currency}")

        if self.date not in self.df['Date'].values:
            raise Exception(f"Date not available: {self.date}")
