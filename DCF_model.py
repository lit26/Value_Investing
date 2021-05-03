from bs4 import BeautifulSoup
import requests

from Financials import Financials
from WACC import WACC
from util import headers, numberCovert

MARKET_GROWTH_RATE = 0.025

class DCF_model:
    def __init__(self, ticker, wacc, stock_fundament, balance_sheet_statement):
        self._ticker = ticker
        self._wacc = wacc
        self._stock_fundament = stock_fundament
        self._balance_sheet_statement = balance_sheet_statement
        self.get_inputs()

    def get_inputs(self):
        fcf_url = f'https://finance.yahoo.com/quote/{self._ticker}/cash-flow?p={self._ticker}'
        response = requests.get(fcf_url, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')

        row = soup.find_all('div', {'data-test': 'fin-row'})[-1]
        row = row.find_all('div', class_="Ta(c)")
        self._fcf_list = [numberCovert(i.text) for i in row[1:]][::-1]

    def value_calculate(self):
        pct_list = []
        for i in range(1, len(self._fcf_list)):
            pct_list.append(self._fcf_list[i]/self._fcf_list[i-1]-1)
        mean_growth = sum(pct_list) / len(pct_list)

        self._fcf_list.append(self._fcf_list[-1]*(1+mean_growth))
        self._fcf_list.append(self._fcf_list[-1] * (1 + mean_growth))
        terminal_value = self._fcf_list[-1] * (1 + MARKET_GROWTH_RATE) / (self._wacc - MARKET_GROWTH_RATE)
        cf_list = self._fcf_list[-2:]

        dcf_list = []
        for i in range(2):
            dcf_list.append(cf_list[i]/((1+self._wacc)**(i+1)))
        dcf_list.append(terminal_value/((1+self._wacc)**2))

        sum_fcf = sum(dcf_list) / 1000
        cash = numberCovert(self._balance_sheet_statement.loc['Cash and Equivalents'][0])
        debt = numberCovert(self._balance_sheet_statement.loc['Long Term Debt'][0])
        equity_value = sum_fcf - debt + cash

        share_outstanding = numberCovert(self._stock_fundament['Shs Outstand']) / 1000000

        price_per_share = equity_value / share_outstanding

        current_price = numberCovert(self._stock_fundament['Price'])

        if price_per_share > current_price:
            return {'Price Per Share': price_per_share,
                    'Current': current_price,
                    'Action': 'Buy',
                    'Upside': price_per_share/current_price - 1}
        else:
            return {'Price Per Share': price_per_share,
                    'Current': current_price,
                    'Action': 'Sell',
                    'Upside': price_per_share/current_price - 1}


if __name__ == '__main__':
    # calculate wacc
    ticker = 'AAPL'
    financials = Financials(ticker)
    wacc_calculator = WACC(ticker,
                           financials.stock_fundament,
                           financials.income_statement,
                           financials.balance_sheet_statement)
    wacc = wacc_calculator.calculate_wacc()
    print(f'WACC: {wacc}')

    # DCF model
    dcf_model = DCF_model(ticker,
                          wacc,
                          financials.stock_fundament,
                          financials.balance_sheet_statement)
    result = dcf_model.value_calculate()
    print(result)