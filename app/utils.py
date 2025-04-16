import datetime
import json
import time
import feedparser
import numpy as np
import requests
import yfinance as yf

from flask import render_template, jsonify, request, session, redirect, url_for, flash
from app import cache

#########################################
# YARDIMCI FONKSİYONLAR (yfinance ile verilerin çekilmesi)
#########################################

@cache.memoize(timeout=60)
def get_exchange_rates():
    """
    Belirli para birimlerinin TRY karşılıklarını yfinance üzerinden alır.
    Yahoo Finance’de döviz çiftleri "USDTRY=X", "EURTRY=X" şeklinde işlemektedir.
    """
    currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD"]
    rates = {}
    for currency in currencies:
        ticker_symbol = f"{currency}TRY=X"
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                price = data["Close"].iloc[-1]
                rates[currency] = round(price, 2)
            else:
                rates[currency] = None
        except Exception as e:
            print(f"Error retrieving {ticker_symbol}: {e}")
            rates[currency] = None
    return rates

@cache.memoize(timeout=10)
def get_crypto_historical_data(crypto_id, days=30):
    """
    Kripto paranın tarihsel verilerini yfinance kullanarak çeker.
    crypto_id: "bitcoin", "ethereum", "ripple", "litecoin" gibi değerler beklenir.
    """
    crypto_ticker_map = {
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "ripple": "XRP-USD",
        "litecoin": "LTC-USD"
    }
    ticker_symbol = crypto_ticker_map.get(crypto_id.lower())
    if not ticker_symbol:
        print(f"Ticker for {crypto_id} not found")
        return []
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period=f"{days}d")
        formatted_prices = []
        for index, row in data.iterrows():
            formatted_prices.append({
                "time": int(index.timestamp() * 1000),  # milisaniye cinsinden
                "price": row["Close"]
            })
        return formatted_prices
    except Exception as e:
        print(f"{crypto_id} tarihsel data yfinance error:", e)
        return []

def get_crypto_predictions(crypto_id, days=30, forecast_days=7):
    data = get_crypto_historical_data(crypto_id, days)
    if not data:
        return []
    prices = [point['price'] for point in data]
    x = np.arange(len(prices))
    coeffs = np.polyfit(x, prices, 1)
    predictions = []
    last_timestamp = data[-1]['time']
    last_date = datetime.datetime.fromtimestamp(last_timestamp / 1000.0)
    for i in range(1, forecast_days + 1):
        pred_index = len(prices) + i - 1
        pred_price = np.polyval(coeffs, pred_index)
        pred_date = last_date + datetime.timedelta(days=i)
        predictions.append({
            "date": pred_date.strftime("%Y-%m-%d"),
            "predicted_price": round(pred_price, 2)
        })
    return predictions

def compute_rsi(prices, period=14):
    if len(prices) < period + 1:
        return [None] * len(prices)
    changes = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(change, 0) for change in changes]
    losses = [abs(min(change, 0)) for change in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rsi = [None] * period
    if avg_loss == 0:
        rsi.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))
    for i in range(period, len(changes)):
        gain = gains[i]
        loss = losses[i]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            rsi_val = 100
        else:
            rs = avg_gain / avg_loss
            rsi_val = 100 - (100 / (1 + rs))
        rsi.append(rsi_val)
    rsi = [None] + rsi
    return rsi

@cache.cached(timeout=10, key_prefix='bitcoin_price')
def get_bitcoin_price():
    try:
        btc_ticker = yf.Ticker("BTC-USD")
        btc_data = btc_ticker.history(period="1d")
        if not btc_data.empty:
            btc_price_usd = btc_data["Close"].iloc[-1]
        else:
            btc_price_usd = None
        exchange_rates = get_exchange_rates()
        usd_to_try = exchange_rates.get("USD", 1)
        if btc_price_usd is not None and usd_to_try is not None:
            return round(btc_price_usd * usd_to_try, 2)
        else:
            return None
    except Exception as e:
        print("Bitcoin yfinance error:", e)
        return None

@cache.cached(timeout=10, key_prefix='bitcoin_details')
def get_bitcoin_details():
    try:
        btc_ticker = yf.Ticker("BTC-USD")
        info = btc_ticker.info
        market_data = {
            "price_try": None,
            "market_cap_try": None,
            "volume_24h_try": None,
            "price_change_percentage_24h": None
        }
        btc_price_usd = info.get("regularMarketPrice")
        market_cap_usd = info.get("marketCap")
        volume_24h = info.get("volume")
        change_percent = info.get("regularMarketChangePercent")
        exchange_rates = get_exchange_rates()
        usd_to_try = exchange_rates.get("USD", 1)
        if btc_price_usd is not None:
            market_data["price_try"] = round(btc_price_usd * usd_to_try, 2)
        if market_cap_usd is not None:
            market_data["market_cap_try"] = round(market_cap_usd * usd_to_try, 2)
        if volume_24h is not None:
            market_data["volume_24h_try"] = round(volume_24h * usd_to_try, 2)
        market_data["price_change_percentage_24h"] = change_percent
        return market_data
    except Exception as e:
        print("Bitcoin detayları yfinance error:", e)
        return {}

@cache.cached(timeout=10, key_prefix='multi_crypto')
def get_multi_crypto_data():
    crypto_tickers = {
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "ripple": "XRP-USD",
        "litecoin": "LTC-USD",
        "cardano": "ADA-USD",
        "binance coin": "BNB-USD",
        "dogecoin": "DOGE-USD",
        "polkadot": "DOT-USD",
        "solana": "SOL-USD",
        "avalanche": "AVAX-USD"
    }
    crypto_dict = {}
    exchange_rates = get_exchange_rates()
    usd_to_try = exchange_rates.get("USD", 1)
    for crypto, ticker_symbol in crypto_tickers.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                price_usd = data["Close"].iloc[-1]
                price_try = round(price_usd * usd_to_try, 2)
                info = ticker.info
                market_cap = info.get("marketCap")
                volume = info.get("volume")
                change_percent = info.get("regularMarketChangePercent")
                crypto_dict[crypto] = {
                    "price_try": price_try,
                    "market_cap_try": round(market_cap * usd_to_try, 2) if market_cap else "N/A",
                    "volume_24h_try": round(volume * usd_to_try, 2) if volume else "N/A",
                    "price_change_percentage_24h": change_percent if change_percent is not None else "N/A"
                }
            else:
                crypto_dict[crypto] = {}
        except Exception as e:
            print(f"Error retrieving data for {crypto}: {e}")
            crypto_dict[crypto] = {}
    return crypto_dict

@cache.cached(timeout=10, key_prefix='multi_crypto_usd')
def get_multi_crypto_data_usd():
    crypto_tickers = {
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "ripple": "XRP-USD"
    }
    crypto_dict = {}
    for crypto, ticker_symbol in crypto_tickers.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                price_usd = data["Close"].iloc[-1]
                crypto_dict[crypto] = round(price_usd, 2)
            else:
                crypto_dict[crypto] = None
        except Exception as e:
            print(f"Error retrieving USD data for {crypto}: {e}")
            crypto_dict[crypto] = None
    return crypto_dict

@cache.cached(timeout=10, key_prefix='asset_prices')
def get_asset_prices():
    exchange_rates = get_exchange_rates()
    usd_to_try = exchange_rates.get("USD", 1)

    # Altın verisi için (GC=F)
    try:
        gold_ticker = yf.Ticker("GC=F")
        # 2 günlük veriyi kontrol ediyoruz
        gold_data = gold_ticker.history(period="2d")
        if not gold_data.empty:
            gold_price_usd = gold_data["Close"].iloc[-1]
        else:
            gold_price_usd = None
    except Exception as e:
        print("Gold yfinance error:", e)
        gold_price_usd = None

    # Gümüş verisi için (SI=F)
    try:
        silver_ticker = yf.Ticker("SI=F")
        silver_data = silver_ticker.history(period="2d")
        if not silver_data.empty:
            silver_price_usd = silver_data["Close"].iloc[-1]
        else:
            silver_price_usd = None
    except Exception as e:
        print("Silver yfinance error:", e)
        silver_price_usd = None

    if gold_price_usd is not None:
        gold_price_try_per_ounce = gold_price_usd * usd_to_try
        gold_price_try_per_gram = gold_price_try_per_ounce / 31.1035
    else:
        gold_price_try_per_ounce = None
        gold_price_try_per_gram = None

    if silver_price_usd is not None:
        silver_price_try_per_ounce = silver_price_usd * usd_to_try
        silver_price_try_per_gram = silver_price_try_per_ounce / 31.1035
    else:
        silver_price_try_per_ounce = None
        silver_price_try_per_gram = None

    # BIST 100 için (^XU100)
    try:
        bist_ticker = yf.Ticker("^XU100")
        bist_data = bist_ticker.history(period="2d")
        if not bist_data.empty:
            bist100 = round(bist_data["Close"].iloc[-1], 2)
        else:
            bist100 = "N/A"
    except Exception as e:
        print("BIST 100 yfinance error:", e)
        bist100 = "N/A"

    return {
        "gram_altin": round(gold_price_try_per_gram, 2) if gold_price_try_per_gram is not None else 0,
        "ons_altin": round(gold_price_try_per_ounce, 2) if gold_price_try_per_ounce is not None else 0,
        "gumus": round(silver_price_try_per_gram, 2) if silver_price_try_per_gram is not None else 0,
        "bist100": bist100 if isinstance(bist100, (int, float)) else 0
    }

#########################################
# ORİJİNAL PİYASA HABERLERİ (MARKET NEWS) KODU
#########################################

@cache.cached(timeout=10, key_prefix='market_news')
def get_market_news():
    from app.config import Config
    API_URL = Config.API_URL
    try:
        response = requests.get(API_URL, timeout=10)
        print("API yanıt kodu:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            formatted_news = []
            for entry in data.get("results", []):
                formatted_news.append({
                    "url": entry.get("url"),
                    "title": entry.get("title"),
                    "description": entry.get("description")
                })
            return formatted_news
        else:
            print("Haber API hatası:", response.status_code)
            return []
    except requests.exceptions.RequestException as e:
        print("Haber verisi çekilirken hata:", e)
        return []
