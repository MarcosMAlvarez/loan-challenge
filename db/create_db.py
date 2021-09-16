"""Create db

Module for database creation.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import AdminUser, Base
from helpers import session_scope

engine = create_engine("sqlite:///db/loan_challenge_db.db")
Session = sessionmaker(bind=engine)

# Generate database schema
Base.metadata.create_all(engine)

# Create some Admin instances
admins = (("marcos", "pass1"), ("matias", "pass2"))

with session_scope() as session:
    for user in admins:
        session.add(AdminUser(*user))
    session.commit()
