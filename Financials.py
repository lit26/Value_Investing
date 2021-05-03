from finvizfinance.quote import finvizfinance, Statements

class Financials:
    def __init__(self, ticker):
        self._ticker = ticker
        self.getFinancials()

    def getFinancials(self):
        # get from finvizfinance
        fstock = finvizfinance(self._ticker)
        self.stock_fundament = fstock.TickerFundament()

        # get statements
        statements = Statements()
        self.income_statement = statements.getStatements(self._ticker,
                                                         statement="I")
        self.balance_sheet_statement = statements.getStatements(self._ticker,
                                                                statement="B")