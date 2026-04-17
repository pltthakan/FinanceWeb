<<<<<<< HEAD
import datetime
from flask import render_template, jsonify, request, session, redirect, url_for, flash, Blueprint
import yfinance as yf
from app import app
from app.utils import (get_exchange_rates, get_bitcoin_price, get_bitcoin_details,
                       get_multi_crypto_data, get_multi_crypto_data_usd, get_asset_prices, get_market_news,
                       get_crypto_historical_data, compute_rsi)

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')

@app.template_filter('timestamp_to_date')
def timestamp_to_date_filter(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    return date.strftime("%d/%m/%Y %H:%M")

@app.context_processor
def inject_live_rates(): # Her sayfa yüklendiğinde bazı canlı verileri şablonlara otomatik gönderir
    exchange_rates = get_exchange_rates()
    asset_prices = get_asset_prices()
    crypto_usd = get_multi_crypto_data_usd() or {}

    live_rates = {
        "USD": exchange_rates.get("USD", "N/A"),
        "EUR": exchange_rates.get("EUR", "N/A"),
        "GBP": exchange_rates.get("GBP", "N/A"),
        "GramAltin": asset_prices.get("gram_altin", "N/A"),
        "OnsAltin": asset_prices.get("ons_altin", "N/A"),
        "Gumus": asset_prices.get("gumus", "N/A"),
        "BIST100": asset_prices.get("bist100", "N/A"),
        "BTCUSD": crypto_usd.get("bitcoin", "N/A"),
        "ETHUSD": crypto_usd.get("ethereum", "N/A"),
        "XRPUSD": crypto_usd.get("ripple", "N/A")
    }
    return dict(live_rates=live_rates)

@assets_bp.route('/<asset_name>')
def asset_detail(asset_name): # Belirli bir varlığın detaylarını gösterir
    asset_mapping = {
        "USD": "USDTRY=X",
        "EUR": "EURTRY=X",
        "GBP": "GBPTRY=X",
        "GramAltin": "GC=F",
        "OnsAltin": "GC=F",
        "Gumus": "SI=F",
        "BIST100": "^XU100",
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "XRPUSD": "XRP-USD"
    }
    if asset_name not in asset_mapping:
        flash("Geçersiz varlık.", "danger")
        return redirect(url_for("home"))
    ticker_symbol = asset_mapping[asset_name]
    ticker = yf.Ticker(ticker_symbol)
    try:
        info = ticker.info
    except Exception as e:
        flash("Varlık bilgileri alınırken hata oluştu.", "danger")
        return redirect(url_for("home"))
    details = {
        "Mevcut Fiyat": info.get("regularMarketPrice"),
        "Alış": info.get("bid"),
        "Satış": info.get("ask"),
        "Günün En Düşük Değeri": info.get("dayLow"),
        "Günün En Yüksek Değeri": info.get("dayHigh")
    }
    if details["Alış"] is not None and details["Satış"] is not None and details["Alış"] != 0:
        diff_percent = ((details["Satış"] - details["Alış"]) / details["Alış"]) * 100
        details["Fark (%)"] = round(diff_percent, 2)
    else:
        details["Fark (%)"] = None
    return render_template("asset_detail.html", asset_name=asset_name, details=details)

@app.route('/asset/<asset_name>/chart/<timeframe>')
def asset_chart(asset_name, timeframe):
    asset_mapping = {
        "USD": "USDTRY=X",
        "EUR": "EURTRY=X",
        "GBP": "GBPTRY=X",
        "GramAltin": "GC=F",
        "OnsAltin": "GC=F",
        "Gumus": "SI=F",
        "BIST100": "^XU100",
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "XRPUSD": "XRP-USD"
    }

    if asset_name not in asset_mapping:
        return jsonify({"error": "Geçersiz varlık."}), 400

    ticker_symbol = asset_mapping[asset_name]
    ticker = yf.Ticker(ticker_symbol)
    valid_timeframes = {"1d", "5d", "1mo", "1y", "5y", "max"}
    if timeframe not in valid_timeframes:
        return jsonify({"error": "Geçersiz zaman dilimi."}), 400

    try:
        df = ticker.history(period=timeframe)
        if df.empty:
            return jsonify({"error": "Veri bulunamadı."}), 404
    except Exception as e:
        return jsonify({"error": "Veriler alınırken hata oluştu."}), 500

    labels = df.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    prices = df["Close"].tolist()

    return jsonify({"labels": labels, "prices": prices})

@app.route('/')
def home():
    exchange_rates = get_exchange_rates()
    bitcoin_price = get_bitcoin_price()
    bitcoin_details = get_bitcoin_details()
    multi_crypto = get_multi_crypto_data()
    asset_prices = get_asset_prices()
    market_news = get_market_news()
    alarm = session.get("alarm", None)
    from app.models import Comment
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    return render_template("index.html",
                           exchange_rates=exchange_rates,
                           bitcoin_price=bitcoin_price,
                           bitcoin_details=bitcoin_details,
                           other_crypto=multi_crypto,
                           asset_prices=asset_prices,
                           market_news=market_news,
                           alarm=alarm,
                           comments=comments)

@app.route('/api/data')
def api_data():
    exchange_rates = get_exchange_rates()
    bitcoin_price = get_bitcoin_price()
    bitcoin_details = get_bitcoin_details()
    multi_crypto = get_multi_crypto_data()
    asset_prices = get_asset_prices()
    market_news = get_market_news()
    alarm = session.get("alarm", None)
    alarm_triggered = False
    if alarm and bitcoin_details.get("price_try") is not None:
        threshold = alarm.get("threshold")
        alarm_type = alarm.get("type")
        current_price = bitcoin_details.get("price_try")
        if alarm_type == "above" and current_price >= threshold:
            alarm_triggered = True
        elif alarm_type == "below" and current_price <= threshold:
            alarm_triggered = True
    return jsonify({
        "exchange_rates": exchange_rates,
        "bitcoin_price": bitcoin_price,
        "bitcoin_details": bitcoin_details,
        "other_crypto": multi_crypto,
        "asset_prices": asset_prices,
        "market_news": market_news,
        "alarm_triggered": alarm_triggered
    })

@app.route('/api/historical')
def api_historical():
    crypto = request.args.get("crypto", "bitcoin")
    days = request.args.get("days", 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    historical_data = get_crypto_historical_data(crypto, days)
    return jsonify(historical_data)

@app.route('/set_alarm', methods=["POST"])
def set_alarm():
    try:
        threshold = float(request.form.get("threshold"))
        alarm_type = request.form.get("alarm_type")
        session["alarm"] = {"threshold": threshold, "type": alarm_type}
    except Exception as e:
        print("Alarm ayarlanırken hata:", e)
    return redirect(url_for("home"))

@app.route('/clear_alarm', methods=["POST"])
def clear_alarm():
    session.pop("alarm", None)
    return redirect(url_for("home"))

@app.route('/converter', methods=["GET", "POST"])
def converter(): # para birimi dönüştürüü
    result = None
    exchange_rates = get_exchange_rates()
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount"))
            from_currency = request.form.get("from_currency")
            to_currency = request.form.get("to_currency")
            rate_from = exchange_rates.get(from_currency)
            rate_to = exchange_rates.get(to_currency)
            if rate_from and rate_to:
                amount_in_usd = amount / rate_from
                result = round(amount_in_usd * rate_to, 4)
        except Exception as e:
            print("Dönüştürücü işleminde hata:", e)
    return render_template("converter.html", result=result, exchange_rates=exchange_rates)

@app.route('/analysis')
def analysis():
    crypto_ids = ["bitcoin", "ethereum", "ripple", "litecoin"]
    historical_data = {}
    technical_indicators = {}
    for crypto in crypto_ids:
        data = get_crypto_historical_data(crypto, 30)
        historical_data[crypto] = data
        if crypto == "bitcoin":
            prices = [point["price"] for point in data]
            rsi_values = compute_rsi(prices, period=14)
            technical_indicators[crypto] = {"rsi": rsi_values}
    return render_template("analysis.html",
                           historical_data=historical_data,
                           technical_indicators=technical_indicators)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/news')
def news():
    market_news = get_market_news()
    return render_template("news.html", market_news=market_news)
=======
import datetime
from flask import render_template, jsonify, request, session, redirect, url_for, flash, Blueprint
import yfinance as yf
from app import app
from app.utils import (get_exchange_rates, get_bitcoin_price, get_bitcoin_details,
                       get_multi_crypto_data, get_asset_prices, get_market_news,
                       get_crypto_historical_data, compute_rsi)

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')

@app.template_filter('timestamp_to_date')
def timestamp_to_date_filter(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    return date.strftime("%d/%m/%Y %H:%M")

@app.context_processor
def inject_live_rates(): # Her sayfa yüklendiğinde bazı canlı verileri şablonlara otomatik gönderir
    exchange_rates = get_exchange_rates()
    asset_prices = get_asset_prices()
    crypto_usd = get_multi_crypto_data()['bitcoin'] if get_multi_crypto_data() else {}
    live_rates = {
        "USD": exchange_rates.get("USD", "N/A"),
        "EUR": exchange_rates.get("EUR", "N/A"),
        "GBP": exchange_rates.get("GBP", "N/A"),
        "GramAltin": asset_prices.get("gram_altin", "N/A"),
        "OnsAltin": asset_prices.get("ons_altin", "N/A"),
        "Gumus": asset_prices.get("gumus", "N/A"),
        "BIST100": asset_prices.get("bist100", "N/A"),
        "BTCUSD": get_multi_crypto_data().get("bitcoin", "N/A"),
        "ETHUSD": get_multi_crypto_data().get("ethereum", "N/A"),
        "XRPUSD": get_multi_crypto_data().get("ripple", "N/A")
    }
    return dict(live_rates=live_rates)

@assets_bp.route('/<asset_name>')
def asset_detail(asset_name): # Belirli bir varlığın detaylarını gösterir
    asset_mapping = {
        "USD": "USDTRY=X",
        "EUR": "EURTRY=X",
        "GBP": "GBPTRY=X",
        "GramAltin": "GC=F",
        "OnsAltin": "GC=F",
        "Gumus": "SI=F",
        "BIST100": "^XU100",
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "XRPUSD": "XRP-USD"
    }
    if asset_name not in asset_mapping:
        flash("Geçersiz varlık.", "danger")
        return redirect(url_for("home"))
    ticker_symbol = asset_mapping[asset_name]
    ticker = yf.Ticker(ticker_symbol)
    try:
        info = ticker.info
    except Exception as e:
        flash("Varlık bilgileri alınırken hata oluştu.", "danger")
        return redirect(url_for("home"))
    details = {
        "Mevcut Fiyat": info.get("regularMarketPrice"),
        "Alış": info.get("bid"),
        "Satış": info.get("ask"),
        "Günün En Düşük Değeri": info.get("dayLow"),
        "Günün En Yüksek Değeri": info.get("dayHigh")
    }
    if details["Alış"] is not None and details["Satış"] is not None and details["Alış"] != 0:
        diff_percent = ((details["Satış"] - details["Alış"]) / details["Alış"]) * 100
        details["Fark (%)"] = round(diff_percent, 2)
    else:
        details["Fark (%)"] = None
    return render_template("asset_detail.html", asset_name=asset_name, details=details)

@app.route('/asset/<asset_name>/chart/<timeframe>')
def asset_chart(asset_name, timeframe):
    asset_mapping = {
        "USD": "USDTRY=X",
        "EUR": "EURTRY=X",
        "GBP": "GBPTRY=X",
        "GramAltin": "GC=F",
        "OnsAltin": "GC=F",
        "Gumus": "SI=F",
        "BIST100": "^XU100",
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "XRPUSD": "XRP-USD"
    }

    if asset_name not in asset_mapping:
        return jsonify({"error": "Geçersiz varlık."}), 400

    ticker_symbol = asset_mapping[asset_name]
    ticker = yf.Ticker(ticker_symbol)
    valid_timeframes = {"1d", "5d", "1mo", "1y", "5y", "max"}
    if timeframe not in valid_timeframes:
        return jsonify({"error": "Geçersiz zaman dilimi."}), 400

    try:
        df = ticker.history(period=timeframe)
        if df.empty:
            return jsonify({"error": "Veri bulunamadı."}), 404
    except Exception as e:
        return jsonify({"error": "Veriler alınırken hata oluştu."}), 500

    labels = df.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
    prices = df["Close"].tolist()

    return jsonify({"labels": labels, "prices": prices})

@app.route('/')
def home():
    exchange_rates = get_exchange_rates()
    bitcoin_price = get_bitcoin_price()
    bitcoin_details = get_bitcoin_details()
    multi_crypto = get_multi_crypto_data()
    asset_prices = get_asset_prices()
    market_news = get_market_news()
    alarm = session.get("alarm", None)
    from app.models import Comment
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    return render_template("index.html",
                           exchange_rates=exchange_rates,
                           bitcoin_price=bitcoin_price,
                           bitcoin_details=bitcoin_details,
                           other_crypto=multi_crypto,
                           asset_prices=asset_prices,
                           market_news=market_news,
                           alarm=alarm,
                           comments=comments)

@app.route('/api/data')
def api_data():
    exchange_rates = get_exchange_rates()
    bitcoin_price = get_bitcoin_price()
    bitcoin_details = get_bitcoin_details()
    multi_crypto = get_multi_crypto_data()
    asset_prices = get_asset_prices()
    market_news = get_market_news()
    alarm = session.get("alarm", None)
    alarm_triggered = False
    if alarm and bitcoin_details.get("price_try") is not None:
        threshold = alarm.get("threshold")
        alarm_type = alarm.get("type")
        current_price = bitcoin_details.get("price_try")
        if alarm_type == "above" and current_price >= threshold:
            alarm_triggered = True
        elif alarm_type == "below" and current_price <= threshold:
            alarm_triggered = True
    return jsonify({
        "exchange_rates": exchange_rates,
        "bitcoin_price": bitcoin_price,
        "bitcoin_details": bitcoin_details,
        "other_crypto": multi_crypto,
        "asset_prices": asset_prices,
        "market_news": market_news,
        "alarm_triggered": alarm_triggered
    })

@app.route('/api/historical')
def api_historical():
    crypto = request.args.get("crypto", "bitcoin")
    days = request.args.get("days", 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    historical_data = get_crypto_historical_data(crypto, days)
    return jsonify(historical_data)

@app.route('/set_alarm', methods=["POST"])
def set_alarm():
    try:
        threshold = float(request.form.get("threshold"))
        alarm_type = request.form.get("alarm_type")
        session["alarm"] = {"threshold": threshold, "type": alarm_type}
    except Exception as e:
        print("Alarm ayarlanırken hata:", e)
    return redirect(url_for("home"))

@app.route('/clear_alarm', methods=["POST"])
def clear_alarm():
    session.pop("alarm", None)
    return redirect(url_for("home"))

@app.route('/converter', methods=["GET", "POST"])
def converter(): # para birimi dönüştürüü
    result = None
    exchange_rates = get_exchange_rates()
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount"))
            from_currency = request.form.get("from_currency")
            to_currency = request.form.get("to_currency")
            rate_from = exchange_rates.get(from_currency)
            rate_to = exchange_rates.get(to_currency)
            if rate_from and rate_to:
                amount_in_usd = amount / rate_from
                result = round(amount_in_usd * rate_to, 4)
        except Exception as e:
            print("Dönüştürücü işleminde hata:", e)
    return render_template("converter.html", result=result, exchange_rates=exchange_rates)

@app.route('/analysis')
def analysis():
    crypto_ids = ["bitcoin", "ethereum", "ripple", "litecoin"]
    historical_data = {}
    technical_indicators = {}
    for crypto in crypto_ids:
        data = get_crypto_historical_data(crypto, 30)
        historical_data[crypto] = data
        if crypto == "bitcoin":
            prices = [point["price"] for point in data]
            rsi_values = compute_rsi(prices, period=14)
            technical_indicators[crypto] = {"rsi": rsi_values}
    return render_template("analysis.html",
                           historical_data=historical_data,
                           technical_indicators=technical_indicators)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/news')
def news():
    market_news = get_market_news()
    return render_template("news.html", market_news=market_news)
>>>>>>> 1d546081434adb9efc9533d04b916628b6944a42
