from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import trader
from datetime import datetime, timedelta
from alpaca_trade_api import REST
from finbert_utils import estimate_sentiment

API_KEY = ""
API_SECRET = ""
BASE_URL = ""

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

class MLTrader(Strategy):
    def initialize(self, symbol: str = "SPY", cash_at_risk: float = 0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        try:
            self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)
        except Exception as e:
            print(f"Error initializing Alpaca API: {e}")
            self.api = None
        self.news_cache = {}  # Caché para almacenar las noticias

    def get_news_cached(self, symbol, start_date, end_date):
        # Verificar si las noticias ya están en caché y si no, recuperarlas de la API
        key = (symbol, start_date, end_date)
        if key in self.news_cache:
            return self.news_cache[key]
        else:
            news = self.api.get_news(symbol=symbol, start=start_date, end=end_date)
            news_headlines = [ev.__dict__["_raw"]["headline"] for ev in news]
            self.news_cache[key] = news_headlines  # Almacenar en caché las noticias
            return news_headlines

    def get_dates(self):
        try:
            today = self.get_datetime()
            three_days_prior = today - timedelta(days=3)
            return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error getting dates: {e}")
            return None, None

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        if today is None or three_days_prior is None:
            return None, None
        news = self.get_news_cached(self.symbol, three_days_prior, today)  # Obtener noticias de la caché
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def position_sizing(self):
        try:
            cash = self.get_cash()
            last_price = self.get_last_price(self.symbol)
            quantity = round(cash * self.cash_at_risk / last_price, 0)
            return cash, last_price, quantity
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return None, None, None

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        if cash is None or last_price is None or quantity is None:
            return

        probability, sentiment = self.get_sentiment()
        if probability is None or sentiment is None:
            return

        try:
            if cash > last_price:
                if sentiment == "positive" and probability > .999:
                    if self.last_trade == "sell":
                        self.sell_all()
                    order = self.create_order(
                        self.symbol,
                        quantity,
                        "buy",
                        type="bracket",
                        take_profit_price=last_price * 1.20,
                        stop_loss_price=last_price * .95
                    )
                    self.submit_order(order)
                    self.last_trade = "buy"

                elif sentiment == "negative" and probability > .999:
                    if self.last_trade == "buy":
                        self.sell_all()
                    order = self.create_order(
                        self.symbol,
                        quantity,
                        "buy",
                        type="bracket",
                        take_profit_price=last_price * .8,
                        stop_loss_price=last_price * 1.05
                    )
                    self.submit_order(order)
                    self.last_trade = "sell"
        except Exception as e:
            print(f"Error executing trading strategy: {e}")

start_date = datetime(2020, 1, 1)
end_date = datetime(2023, 12, 31)
broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol": "SPY", "cash_at_risk": .5})

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY", "cash_at_risk": .5}
)

