"""Loan challenge database model.

The database contains to tables:
    - admin_users: users with admin privileges
    - loan_requests: save all requested loan
"""
from passlib.context import CryptContext
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        self.password = pwd_context.hash(password)


class LoanRequest(Base):
    __tablename__ = "loan_requests"

    id = Column(Integer, primary_key=True)
    dni = Column(Integer)
    full_name = Column(String)
    genre = Column(String)
    email = Column(String)
    loan_amount = Column(Float)
    status = Column(String)

    def __init__(self, dni, full_name, genre, email, loan_amount, status):
        self.dni = dni
        self.full_name = full_name
        self.genre = genre
        self.email = email
        self.loan_amount = loan_amount
        self.status = status
