import os
from datetime import datetime
import pandas as pd
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
from dotenv_vault import load_dotenv
from lightweight_charts import Chart

# Загружаем конфигурацию
load_dotenv()


class BinanceChart:
    def __init__(self, symbol="BTCUSDT", interval="1m"):
        self.symbol = symbol
        self.interval = interval
        self.chart = Chart()
        self.df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        self.ws_client = SpotWebsocketAPIClient(stream_url='wss://ws-api.testnet.binance.vision/ws-api/v3')

    def handle_kline_message(self, message):
        if 'k' in message:
            kline = message['k']
            if kline['x']:  # если свеча закрыта
                new_row = pd.DataFrame([{
                    'time': datetime.fromtimestamp(kline['t'] / 1000),
                    'open': float(kline['o']),
                    'high': float(kline['h']),
                    'low': float(kline['l']),
                    'close': float(kline['c']),
                    'volume': float(kline['v'])
                }])
                self.df = pd.concat([self.df, new_row], ignore_index=True)
                self.chart.set(self.df)

    def start(self):
        #self.ws_client.start()
        self.ws_client.klines(
            symbol=self.symbol,
            interval=self.interval,
            callback=self.handle_kline_message
        )
        self.chart.show(block=True)

    def stop(self):
        self.ws_client.stop()


def main():
    chart_app = BinanceChart()
    try:
        chart_app.start()
    except KeyboardInterrupt:
        chart_app.stop()


if __name__ == "__main__":
    main()
