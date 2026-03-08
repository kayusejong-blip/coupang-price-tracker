from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

DB_URL = "sqlite:///./data/database.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    name = Column(String)
    thumbnail = Column(String)
    current_price = Column(Float, default=0.0)
    target_price = Column(Float, nullable=True)
    is_active = Column(Integer, default=1) # 1 for active, 0 for inactive
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    product = relationship("Product", back_populates="history")

def init_db():
    Base.metadata.create_all(bind=engine)
