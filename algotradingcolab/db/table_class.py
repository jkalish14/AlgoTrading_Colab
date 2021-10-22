from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy import Index


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "PLACE_HOLDER" #URL pointed at db
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) #creating object class of SQLAlchemy

class Stocks(db.Model):
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    symbol = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(125),index=True, nullable=False)
    exchange = db.Column(db.String(10), nullable=False)
    stock_class = db.Column(db.String(10), nullable=False)
    shortable = db.Column(db.Boolean, nullable=False, default=False)
    fractionable = db.Column(db.Boolean, nullable=False, default=False)
    price_minute_id = db.relationship('Price_minutes', backref='stocks')
    quotes_minute_id = db.relationship('Quotes_minutes', backref='stocks')

    def __init__(self, id, symbol, name, exchange, stock_class, shortable, fractionable):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.exchange = exchange
        self.stock_class = stock_class
        self.shortable = shortable
        self.fractionable = fractionable

class Price_minute(db.Model):
    __tablename__ = "price_minute"
    minute_id = db.Column(db.Integer, primary_key =True, unique=True, nullable=False)
    date_time = db.Column(db.DateTime, primary_key =True,nullable=False)
    minute_open = db.Column(db.Integer, nullable=False)
    minute_high = db.Column(db.Integer, nullable=False)
    minute_low = db.Column(db.Integer, nullable=False)
    minute_close = db.Column(db.Integer, nullable=False)
    minute_volume = db.Column(db.Integer, nullable=False)
    stock_id = db.relationship(db.Integer, db.ForeignKey('stocks.id'))

    def __init__(self, minute_id, date_time, minute_open, minute_high, minute_low, minute_close, minute_volume):
        self.minute_id
        self.date_time
        self.minute_open
        self.minute_high
        self.minute_low
        self.minute_close
        self.minute_volume

class Quotes_minute(db.Model):
    __tablename__ = "quote_minutes"
    quotes_id = db.Column(db.Integer, primary_key =True, unique=True, nullable=False)
    date_time = db.Column(db.DateTime, primary_key =True,nullable=False)
    ask_exchange = db.Column(db.String, nullable=False)
    ask_price = db.Column(db.Integer, nullable=False)
    ask_size = db.Column(db.Integer, nullable=False)
    bid_exchange = db.Column(db.String, nullable=False)
    bid_price = db.Column(db.Integer, nullable=False)
    conditions = db.Column(db.String, nullable=False)
    tape = db.Column(db.String, nullable=False)
    stock_id = db.relationship(db.Integer, db.ForeignKey('stocks.id'))

    def __init__(self, quotes_id, date_time, ask_exchange, ask_price, ask_size, bid_exchange, bid_price, conditions, tape):
        self.quotes_id
        self.date_time
        self.ask_exchange
        self.ask_price
        self.ask_size
        self.bid_exchange
        self.bid_price
        self.conditions
        self.tape

class Trading_days(db.Model):
    __tablename__ = "trading_days"
    date = db.Column(db.DateTime, primary_key=True)
    market_open = db.Column(db.Boolean, nullable=False, default=False)
    close_time = db.Column(db.Time)
    open_time = db.Column(db.Time)
    session_close = db.Column(db.Time)
    session_open = db.Column(db.Time)

    def __init__(self, date, market_open, market_close, close_time, open_time, session_close, session_open):
        self.date
        self.market_open
        self.market_close
        self.close_time
        self.open_time
        self.session_close
        self.session_open

db.create_all()
db.session.commit()

@app.route("/")
def index():

    return "CHECKING V2"

if __name__ == "__main__":
    app.run(debug=True)