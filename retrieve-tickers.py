import csv
import logging
from ftplib import FTP
from io import BytesIO, TextIOWrapper
from typing import List
import pandas as pd
import sys
from datetime import datetime

logger = logging.getLogger(__name__)


# Returns a list of tickers through NASDAQ
def get_tickers() -> List[str]:
    logger.info(f"Querying for tickers.")

    raw = BytesIO()

    # FTP locations taken from https://quant.stackexchange.com/a/1862.
    with FTP('ftp.nasdaqtrader.com') as conn:
        conn.login()
        conn.retrbinary('RETR SymbolDirectory/nasdaqlisted.txt', raw.write)

    raw.seek(0)
    reader = csv.DictReader(TextIOWrapper(raw), delimiter='|')

    # After http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs:
    # - data['Test Issue'] == 'N' indicates the asset is not a test security
    # - data['Financial Status'] == 'N' indicates the asset is normal, and
    #   continues to meet the Nasdaq's requirements for listing.
    tickers = [row["Symbol"] for row in reader
               if row["Test Issue"] == "N"
               if row["Financial Status"] == "N"]

    logger.info(f"Obtained {len(tickers)} tickers.")

    return tickers

def main(output_dir):
    tickers = pd.DataFrame(get_tickers(), columns=['ticker'])
    todayDate = datetime.today().strftime('%Y%m%d')
    tickers.to_csv(output_dir+'/tickers_'+todayDate+'.csv', index=False)

if __name__ == '__main__':
    output_dir = sys.argv[1]
    main(output_dir)