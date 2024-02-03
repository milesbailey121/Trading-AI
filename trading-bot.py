from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import timedelta

API_KEY = "PKVTV7HKR8VUCMNLDCRD"
API_SECRET = "ic42LjK1abaemEHQUT1of5EItbcNg4cc4G111Rax"
BASE_URL = "https://paper-api.alpaca.markets"

ALPCA_CREDS = {
    "API_KEY":API_KEY,
    "API_SECRET":API_SECRET,
    "PAPER": True
}

class MLStrategy(Strategy):
    def initialize(self, symbol:str = "SPY", cash_at_risk:float=.5): # Lifecylce
        self.symbol = symbol # SPY index
        self.sleeptime = "24H" # Trade Freqeuency
        self.last_trade = None # Last Trade 
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url = BASE_URL, key_id = API_KEY, secret_key = API_SECRET)
        
    def position_sizing(self): # Cash Managment strategies 
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        #The formula guides how much of our cash balance we use per trade. 
        #Cash at risk of 0.5 means that for each trade it's using 50% of our remaning cash balance
        quantity = round(cash * self.cash_at_risk / last_price)
        return cash,last_price,quantity
    
    def get_news(self):
        self.api.get_news()
    
    def on_trading_iteration(self): # On tick
        cash,last_price,quantity = self.position_sizing()
        if cash > last_price:
            if self.last_trade == None:
                order = self.create_order(
                    self.symbol,
                    quantity,#Num of orders
                    "buy",
                    type="braket",
                    take_profit_price=last_price*1.20,
                    stop_loss_limit_price=last_price*.95
                )
                self.submit_order(order)
                self.last_trade = "buy"

start_date = datetime(2023,12,15)
end_date = datetime(2023,12,31)

broker = Alpaca(ALPCA_CREDS)



stratgey = MLStrategy(name="mlstrat",broker=broker, 
                      parameters={"symbol":"SPY",
                                  "cash_at_risk":.5})

stratgey.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters= {"symbol":"SPY",
                "cash_at_risk":.5}
)