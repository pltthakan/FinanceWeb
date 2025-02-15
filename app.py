import datetime
import json
import time
import feedparser
import numpy as np
import requests
import yfinance as yf  # yfinance kütüphanesi

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Gerçek uygulamada daha güvenli bir anahtar kullanın!

# SQLAlchemy yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Cache yapılandırması
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 10
cache = Cache(app)
cache.clear()

# API URL’leri ve Anahtarlar
# Döviz kurları için artık yfinance kullanılacak.
# Piyasa haberleri için CryptoPanic API'si orijinal kod gibi kullanılmaya devam ediliyor.
API_KEY = "458305536015ef1bc0a78cd5fb821e70b8b1cd87"
API_URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={API_KEY}&public=true"

#########################################
# VERİTABANI MODELLERİ: User, Comment, CommentLike
#########################################

# Takip (followers) ilişkisi için yardımcı tablo (Many-to-Many)
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(200), nullable=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment',
                              backref=db.backref('parent', remote_side=[id]),
                              cascade="all, delete-orphan",
                              lazy='dynamic')

    @property
    def like_count(self):
        return CommentLike.query.filter_by(comment_id=self.id, is_like=True).count()

    @property
    def dislike_count(self):
        return CommentLike.query.filter_by(comment_id=self.id, is_like=False).count()

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    is_like = db.Column(db.Boolean, nullable=False)  # True: Like, False: Dislike
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='_user_comment_uc'),)

app.jinja_env.globals['Comment'] = Comment

#########################################
# YARDIMCI FONKSİYONLAR (yfinance ile verilerin çekilmesi)
#########################################

@cache.memoize(timeout=10)
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
        "litecoin": "LTC-USD"
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
                    "market_cap_try": round(market_cap * usd_to_try, 2) if market_cap else None,
                    "volume_24h_try": round(volume * usd_to_try, 2) if volume else None,
                    "price_change_percentage_24h": change_percent
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

    try:
        gold_data = yf.Ticker("GC=F").history(period="1d")
        if not gold_data.empty:
            gold_price_usd = gold_data["Close"].iloc[-1]
        else:
            gold_price_usd = None
    except Exception as e:
        print("Gold yfinance error:", e)
        gold_price_usd = None

    try:
        silver_data = yf.Ticker("SI=F").history(period="1d")
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

    try:
        ticker = "^XU100"
        bist100_data = yf.download(ticker, period="1d", interval="1m")
        if not bist100_data.empty:
            bist100 = round(bist100_data["Close"].iloc[-1], 2)
        else:
            bist100 = "N/A"
    except Exception as e:
        print("BIST 100 yfinance error:", e)
        bist100 = "N/A"

    return {
        "gram_altin": round(gold_price_try_per_gram, 2) if gold_price_try_per_gram is not None else "N/A",
        "ons_altin": round(gold_price_try_per_ounce, 2) if gold_price_try_per_ounce is not None else "N/A",
        "gumus": round(silver_price_try_per_gram, 2) if silver_price_try_per_gram is not None else "N/A",
        "bist100": bist100
    }

#########################################
# ORİJİNAL PİYASA HABERLERİ (MARKET NEWS) KODU
#########################################

@cache.cached(timeout=10, key_prefix='market_news')
def get_market_news():
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

#########################################
# TEMPLATE FILTER VE CONTEXT PROCESSOR
#########################################

@app.template_filter('timestamp_to_date')
def timestamp_to_date_filter(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    return date.strftime("%d/%m/%Y %H:%M")

@app.context_processor
def inject_live_rates():
    exchange_rates = get_exchange_rates()
    asset_prices = get_asset_prices()
    crypto_usd = get_multi_crypto_data_usd()
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

#########################################
# ROUTELER
#########################################

@app.route('/')
def home():
    exchange_rates = get_exchange_rates()
    bitcoin_price = get_bitcoin_price()
    bitcoin_details = get_bitcoin_details()
    multi_crypto = get_multi_crypto_data()
    asset_prices = get_asset_prices()
    market_news = get_market_news()
    alarm = session.get("alarm", None)
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

@app.route('/predict', methods=['GET'])
def predict():
    crypto = request.args.get("crypto", "bitcoin")
    try:
        forecast_days = int(request.args.get("days", 7))
    except ValueError:
        forecast_days = 7
    predictions = get_crypto_predictions(crypto, days=30, forecast_days=forecast_days)
    historical_data = get_crypto_historical_data(crypto, days=30)
    return render_template("predict.html",
                           crypto=crypto,
                           predictions=predictions,
                           historical_data=historical_data,
                           forecast_days=forecast_days)

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
def converter():
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

#########################################
# KULLANICI KAYIT / GİRİŞ / ÇIKIŞ
#########################################

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password != confirm:
            flash("Şifreler eşleşmiyor!", "danger")
            return redirect(url_for('register'))
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Kullanıcı adı veya e-posta zaten kayıtlı.", "warning")
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Kayıt başarılı! Lütfen giriş yapın.", "success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Geçersiz kullanıcı adı veya şifre.", "danger")
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['username'] = user.username
        flash("Giriş başarılı.", "success")
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Çıkış yapıldı.", "info")
    return redirect(url_for('home'))

#########################################
# YORUM İŞLEMLERİ
#########################################

@app.route('/comments')
def comments_page():
    comments = Comment.query.filter_by(parent_id=None).order_by(Comment.timestamp.desc()).all()
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return render_template("comments.html", comments=comments, current_user=current_user)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user_id' not in session:
        flash("Yorum yapabilmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    comment_text = request.form.get('comment')
    parent_id = request.form.get('parent_id')
    if parent_id:
        try:
            parent_id = int(parent_id)
        except ValueError:
            parent_id = None
    else:
        parent_id = None

    if comment_text:
        new_comment = Comment(content=comment_text,
                              user_id=session['user_id'],
                              parent_id=parent_id)
        db.session.add(new_comment)
        db.session.commit()
        flash("Yorum eklendi.", "success")
    else:
        flash("Yorum boş olamaz.", "warning")
    return redirect(url_for('comments_page'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        flash("Yorum silebilmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != session['user_id']:
        flash("Bu yorumu silemezsiniz.", "danger")
        return redirect(url_for('comments_page'))
    db.session.delete(comment)
    db.session.commit()
    flash("Yorum silindi.", "success")
    return redirect(url_for('comments_page'))

@app.route('/like_comment/<int:comment_id>', methods=['POST'])
def like_comment(comment_id):
    if 'user_id' not in session:
        flash("Yorum beğenmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_id = session['user_id']
    existing = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if existing:
        if existing.is_like:
            db.session.delete(existing)
        else:
            existing.is_like = True
    else:
        like = CommentLike(user_id=user_id, comment_id=comment_id, is_like=True)
        db.session.add(like)
    db.session.commit()
    return redirect(url_for('comments_page'))

@app.route('/dislike_comment/<int:comment_id>', methods=['POST'])
def dislike_comment(comment_id):
    if 'user_id' not in session:
        flash("Yorum beğenmemek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_id = session['user_id']
    existing = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if existing:
        if not existing.is_like:
            db.session.delete(existing)
        else:
            existing.is_like = False
    else:
        dislike = CommentLike(user_id=user_id, comment_id=comment_id, is_like=False)
        db.session.add(dislike)
    db.session.commit()
    return redirect(url_for('comments_page'))

#########################################
# PROFIL VE TAKİP İŞLEMLERİ
#########################################

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    comments = Comment.query.filter_by(user_id=user.id).order_by(Comment.timestamp.desc()).all()
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user, comments=comments, current_user=current_user)

@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    if 'user_id' not in session:
        flash("Takip işlemi yapmak için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_to_follow = User.query.filter_by(username=username).first_or_404()
    current_user = User.query.get(session['user_id'])
    if current_user.id == user_to_follow.id:
        flash("Kendinizi takip edemezsiniz.", "warning")
        return redirect(url_for('profile', username=username))
    current_user.follow(user_to_follow)
    db.session.commit()
    flash(f"{username} kullanıcısını takip ettiniz.", "success")
    return redirect(url_for('profile', username=username))

@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    if 'user_id' not in session:
        flash("Takipten çıkma işlemi yapmak için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_to_unfollow = User.query.filter_by(username=username).first_or_404()
    current_user = User.query.get(session['user_id'])
    if current_user.id == user_to_unfollow.id:
        flash("Kendinizi takipten çıkaramazsınız.", "warning")
        return redirect(url_for('profile', username=username))
    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    flash(f"{username} kullanıcısını takipten çıktınız.", "success")
    return redirect(url_for('profile', username=username))

#########################################
# UYGULAMA BAŞLANGICI
#########################################

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)