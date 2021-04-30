from bs4 import BeautifulSoup
from finvizfinance.quote import finvizfinance, Statements
import requests
import yfinance as yf

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

def numberCovert(num):
    """covert number(str) to number(float)
    Args:
        num(str): number of string
    Return:
        num(float): number of string
    """
    if num == '-':
        return None
    elif num[-1] == '%':
        return float(num[:-1]) / 100
    elif num[-1] == 'B':
        return float(num[:-1]) * 1000000000
    elif num[-1] == 'M':
        return float(num[:-1]) * 1000000
    elif num[-1] == 'K':
        return float(num[:-1]) * 1000
    else:
        return float(''.join(num.split(',')))

MARKET_RETURN = 0.0851

class WACC:
    def __init__(self, ticker):
        self._ticker = ticker
        self.get_inputs()
    
    def get_inputs(self):
        income_statement_url = f'https://finance.yahoo.com/quote/{self._ticker}/financials?p={self._ticker}'
        response = requests.get(income_statement_url, headers=headers)

        # get interest expense
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('div', class_="D(tbrg)")
        row = table.find_all('div', {'data-test': 'fin-row'})[20]
        row = row.find_all('div', class_="Ta(c)")
        interest_expense = [i.text for i in row][1]
        self._interest_expense = numberCovert(interest_expense)/1000

        # get risk free rate
        stock = yf.Ticker("^TNX")
        self._risk_free = stock.info['previousClose'] / 100

        # get statements data
        stock = finvizfinance(self._ticker)
        stock_fundament = stock.TickerFundament()
        self._beta = numberCovert(stock_fundament['Beta'])
        self._market_cap = numberCovert(stock_fundament['Market Cap'])

        statements = Statements()
        income_statement = statements.getStatements(self._ticker, statement="I")
        statements = Statements()
        balance_sheet_statement = statements.getStatements(self._ticker, statement="B")
        self._tax_provision = numberCovert(income_statement.loc['Provision for Income Taxes'][1])
        self._pre_tax_income = numberCovert(income_statement.loc['Net Income Before Taxes'][1])
        self._total_debt = numberCovert(balance_sheet_statement.loc['Total Debt'][1])
    
    def calculate_wacc(self):
        # cost of debt
        self._cost_of_debt = self._interest_expense / self._total_debt
        effective_tax_rate = self._tax_provision / self._pre_tax_income
        cost_of_debt2 = self._cost_of_debt * (1-effective_tax_rate)

        # cost of equity
        self._cost_of_equity = self._risk_free + \
                               self._beta * (MARKET_RETURN - self._risk_free)

        # wacc
        total = self._total_debt + self._market_cap
        self._wacc = (self._total_debt/total) * cost_of_debt2 + \
                    (self._market_cap/total) * self._cost_of_equity
        return self._wacc

    def record_data(self):
        data = {}
        data['Interest Expense'] = self._interest_expense
        data['Market Cap'] = self._market_cap
        data['Total Debt'] = self._total_debt
        data['Tax Provision'] = self._tax_provision
        data['Pretax income'] = self._pre_tax_income
        data['Beta'] = self._beta
        data['Cost of Debt'] = self._cost_of_debt
        data['Cost of Equity'] = self._cost_of_equity
        data['WACC'] = self._wacc
        return data

if __name__ == '__main__':
    wacc_calculator = WACC('AAPL')
    wacc = wacc_calculator.calculate_wacc()
    data = wacc_calculator.record_data()
    print(data)


