from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer,\
                       String, Boolean,\
                       Sequence, Text,\
                       ForeignKey, Float,\
                       DateTime, Table

from datetime import datetime


Base = declarative_base()


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
        self.code, self.name, self.cost, self.cat_id = code, name, cost, category
        for k in kwargs:
            if k in ('description', 'image',
                     'markup', 'stock_count',
                     'stock_low_mark', 'wishlist' ,'enabled'):
                setattr(self, k, kwargs[k])

    def __repr__(self):
        return "<Item(%s, code=%s, stock=%d)>" % (self.name, self.code, self.stock_count)


class ItemCategory(Base):
    __tablename__ = 'itemcategory'

    id = Column(Integer, Sequence('itemcat_id_seq'), primary_key=True)
    name = Column(String, unique=True, nullable=False)

    items = relationship("Item", order_by="Item.id", backref="category")
    attributegroups = relationship("AttributeGroup", backref="category")

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


class AttributeGroup(Base):
    __tablename__ = 'attributegroup'

    id = Column(Integer, Sequence('attributegroup_id_seq'), primary_key=True)
    code = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    cat_id = Column(Integer, ForeignKey('itemcategory.id'), nullable=False)
    attrtype = Column(String, nullable=False)
    required = Column(Boolean, nullable=False, default=False)

    attributes = relationship('Attribute', backref='group')

    def __init__(self, code, description, cat_id, attrtype, required=False):
        self.code = code
        self.description = description
        self.cat_id = cat_id
        self.attrtype = attrtype
        self.required = required


class Attribute(Base):
    __tablename__ = 'attribute'

    id = Column(Integer, Sequence('attribute_id_seq'), primary_key=True)
    code = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('attributegroup.id'), nullable=False)

    def __init__(self, code, description, group_id):
        self.code = code
        self.description = description
        self.group_id = group_id


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    isadmin = Column(Boolean, nullable=False, default=False)
    enabled = Column(Boolean, nullable=False, default=True)

    image = relationship("UserImage", backref="user", uselist=False)
    account = relationship("Account", backref="user", uselist=False)
    discount = relationship("UserDiscount", backref="user", uselist=False)
    ledgers = relationship("Ledger", backref="user", primaryjoin="User.id == Ledger.user_id")
    votes = relationship("Vote", backref="user")

    def __init__(self, email, password, **kwargs):
        self.email = email
        self.password = password
        for k in kwargs:
            if k in ('isadmin', 'enabled'):
                setattr(self, k, kwargs[k])

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


class Vote(Base):
    __tablename__ = 'vote'

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    vote = Column(Boolean, nullable=False)

    def __init__(self, user_id, item_id, vote):
        self.user_id, self.item_id, self.vote = user_id, item_id, vote


TransactionTypes = ["transfer", "purchase", "topup", "restock"]


ledgerattributes= Table('ledgerattributes', Base.metadata,
    Column('ledger_id', Integer, ForeignKey('ledger.id'), nullable=False),
    Column('attribute_id', Integer, ForeignKey('attribute.id'), nullable=False)
)


class Ledger(Base):
    __tablename__ = 'ledger'

    id = Column(Integer, Sequence('ledger_id_seq'), primary_key=True)
    transtype = Column(Integer, default=TransactionTypes.index("purchase"))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('item.id'))
    to_user_id = Column(Integer, ForeignKey('user.id'))
    quantity = Column(Float, default=0.0, nullable=False)
    verified = Column(Boolean, default=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now())

    attributes = relationship("Attribute", secondary=ledgerattributes, backref="ledgers")

    def __init__(self, user_id, quantity, transtype=TransactionTypes.index("purchase"), verified=True, **kwargs):
        self.user_id = user_id
        self.quantity = quantity
        self.transtype = transtype
        self.verified = verified
        self.timestamp = datetime.now()

        for k in kwargs:
            if k in ('product_id', 'to_user_id'):
                setattr(self, k, kwargs[k])

        if not (hasattr(self, 'product_id') or hasattr(self, 'to_user_id')):
            raise Exception("Ledger must have either product_id or to_user_id!")

    def __repr__(self):
        return "<Ledger(%s: %s %s %d)>" % (self.timestamp.isoformat(' '), user.username, TransactionTypes[self.transtype], self.quantity)


def init(dbpath, debug=False):
    global Base
    engine = create_engine(dbpath, echo=debug)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    return Base, Session
