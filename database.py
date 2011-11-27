from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer,\
                       String, Boolean,\
                       Sequence, Text,\
                       ForeignKey, Float,\
                       DateTime

from datetime import datetime

Base = declarative_base()

engine = create_engine('sqlite:///home/hugh/src/fridge_2.0/db.sqlite', echo=True)

Session = sessionmaker(bind=engine)

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, Sequence('item_id_seq'), primary_key=True)
    code = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    cost = Column(Float, default=0.0, nullable=False)
    markup = Column(Float, default=5.0, nullable=False)
    cat_id = Column(Integer, ForeignKey('itemcategory.id'))
    stock_count = Column(Integer, default=0, nullable=False)
    stock_low_mark = Column(Integer, default=10, nullable=False)
    wishlist = Column(Boolean, default=False, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)

    image = relationship("ItemImage", backref="item", uselist=False)
    votes = relationship("Vote", backref="item")

    def __init__(self, code, name, cost, category, **kwargs):
        self.code, self.name, self.cost, self.category = code, name, cost, category
        for k,v in kwargs:
            if k in ('description', 'image',
                     'markup', 'stock_count',
                     'stock_low_mark', 'wishlist' ,'enabled'):
                setattr(self, k, v)

    def __repr__(self):
        return "<Item(%s, code=%s, stock=%d)>" % (self.name, self.code, self.stock_count)


class ItemCategory(Base):
    __tablename__ = 'itemcategory'

    id = Column(Integer, Sequence('itemcat_id_seq'), primary_key=True)
    name = Column(String, unique=True, nullable=False)

    items = relationship("Item", order_by="Item.id", backref="category")

    def __init__(self, name):
        self.name = name


class ItemImage(Base):
    __tablename__ = 'itemimage'

    id = Column(Integer, Sequence('itemimage_id_seq'), primary_key=True)
    item_id = Column(Integer, ForeignKey("item.id"))
    path = Column(String, nullable=False, default="")

    def __init__(self, item_id, path):
        self.item_id = item_id
        self.path = path

class Vote(Base):
    __tablename__ = 'vote'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    vote = Column(Boolean, nullable=False)

    def __init__(self, user_id, item_id, vote):
        self.user_id, self.item_id, self.vote = user_id, item_id, vote


TransactionTypes = ["transfer", "purchase", "topup", "restock"]


class Ledger(Base):
    __tablename__ = 'ledger'

    id = Column(Integer, Sequence('ledger_id_seq'), primary_key=True)
    transtype = Column(Integer, default=TransactionTypes.index("purchase"), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    reference = Column(String, nullable=False, default="")
    quantity = Column(Float, default=0.0, nullable=False)
    verified = Column(Boolean, default=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now())

    def __init__(self, user_id, reference, quantity, transtype=TransactionTypes.index("purchase"), verified=True):
        self.user_id = user_id
        self.reference = reference
        self.quantity = quantity
        self.transtype = transtype
        self.verified = verified
        self.timestamp = datetime.now()

    def __repr__(self):
        return "<Ledger(%s: %s %s %d %s)>" % (self.timestamp.isoformat(' '), user.username, TransactionTypes[self.transtype], self.quantity, self.reference)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String, nullable=False, unique=True, index=True)
    fname = Column(String, nullable=False)
    lname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    isadmin = Column(Boolean, nullable=False, default=False)
    enabled = Column(Boolean, nullable=False, default=True)

    image = relationship("UserImage", backref="user", uselist=False)
    account = relationship("Account", backref="user", uselist=False)
    discount = relationship("UserDiscount", backref="user", uselist=False)
    ledgers = relationship("Ledger", backref="user")
    votes = relationship("Vote", backref="user")

    def __init__(self, username, password, email, fname, lname, **kwargs):
        self.username = username
        self.password = password
        self.email = email
        self.fname, self.lname = fname, lname
        for k,v in kwargs:
            if k in ('isadmin', 'enabled', 'image'):
                setattr(self, k, v)

    def __repr__(self):
        return "<User('%s')>" % self.username


class UserImage(Base):
    __tablename__ = 'userimage'

    id = Column(Integer, Sequence('userimage_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    path = Column(String, nullable=False, default="")

    def __init__(self, user_id, path):
        self.user_id = user_id
        self.path = path


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, Sequence('account_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    balance = Column(Float, nullable=False, default=0.0)

    def __init__(self, user_id, balance):
        self.user_id = user_id
        self.balance = balance


class UserDiscount(Base):
    __tablename__ = 'userdiscount'

    id = Column(Integer, Sequence('userdiscount_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    discount = Column(Float, default=0.0, nullable=False)

    def __init__(self, user_id, discount):
        self.user_id = user_id
        self.discount = discount
