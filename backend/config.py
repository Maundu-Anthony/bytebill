import os
from datetime import timedelta

class Config:
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bytebill-secret-key-change-in-production'
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Database Settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or 3306
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'bytebill_user'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'bytebill_password'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'bytebill_db'
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # M-PESA Settings
    MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY')
    MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET')
    MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY')
    MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE')
    MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL') or 'http://hotspot.local/api/mpesa/callback'
    
    # Network Settings
    LAN_INTERFACE = 'eth0'
    WAN1_INTERFACE = 'enx1'
    WAN2_INTERFACE = 'enx2'
    LAN_SUBNET = '192.168.88.0/24'
    GATEWAY_IP = '192.168.88.1'
    
    # Hotspot Settings
    CAPTIVE_PORTAL_URL = 'http://hotspot.local'
    DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour in seconds
    DEFAULT_DATA_LIMIT = 1048576000  # 1GB in bytes
    
    # ISP Settings
    ISP1_NAME = 'ISP 1 (Unlimited)'
    ISP2_NAME = 'ISP 2 (FUP)'
    SPEED_TEST_INTERVAL = 300  # 5 minutes
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
