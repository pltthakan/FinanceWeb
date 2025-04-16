class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60

    # API URL’leri ve Anahtarlar
    API_KEY = "458305536015ef1bc0a78cd5fb821e70b8b1cd87"
    API_URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={API_KEY}&public=true"
