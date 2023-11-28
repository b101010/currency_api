import os
from dotenv import load_dotenv
import pandas as pd
from tools import ZipDownloader, Unzipper, CurrencyExtractor
import logging
from flask import Flask, request, jsonify

load_dotenv()

logging.basicConfig(
    filename=os.getenv("LOG_FILE"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)


# create zipDownloader instance
zip_downloader = ZipDownloader(os.getenv("ZIP_URL"))

# create unzipper instance
unzipper = Unzipper(os.getenv("FILE_TO_EXTRACT"), zip_downloader.get_file())

# create dataframe
df = pd.read_csv(unzipper.get_data())

# drop columns where all values = nan
df.dropna(axis=1, how='all', inplace=True)


@app.route("/<date>/<currency>", methods=['GET'])
def endpoint(date, currency):
    try:
        # Create currency extractor instance
        currency_extractor = CurrencyExtractor(date, currency, df)
        result = currency_extractor.get_value()

        return jsonify(result)

    except BaseException:
        error = {
            'error': 'Something wrong happend, please read the log for more information',
        }

        return jsonify(error), 404


if __name__ == '__main__':
    app.run()
