"""Helper functions for database management
"""
from contextlib import contextmanager
from typing import List, Optional

from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker

from rest.models import Admin, Person, LoanRecord
from db.models import AdminUser, LoanRequest

engine = create_engine("sqlite:///db/loan_challenge_db.db")
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Context manager for sqlalchemy session"""
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


def add_loan_record(user: Person, loan_status: str) -> None:
    """Add new loan record to the database

    Args:
    user: person who requested the loan.
    loan_status: if loan has been approved or rejected."""
    with session_scope() as session:
        session.add(
            LoanRequest(
                dni=user.dni,
                full_name=user.full_name,
                genre=user.genre,
                email=user.email,
                loan_amount=user.loan_amount,
                status=loan_status,
            )
        )
        session.commit()


def get_loan_records() -> Optional[List[dict]]:
    """Gets all loan record in the database and returns them in a list.
    If there are no records, it returns None."""
    with session_scope() as session:
        response = session.query(LoanRequest).all()
    if response:
        records = []
        for record in response:
            records.append(
                {
                    "id": record.id,
                    "dni": record.dni,
                    "full_name": record.full_name,
                    "genre": record.genre,
                    "email": record.email,
                    "loan_amount": record.loan_amount,
                    "status": record.status,
                }
            )
        return records
    return None


def update_loan_record(id_: int, loan_record: LoanRecord) -> bool:
    """Update a loan record from the database

    Args:
    id_: loan record id which wants to be modified.
    loan_record: new information for updating."""
    updated_data = {key: value for key, value in loan_record.items() if value is not None}  # type: ignore
    with session_scope() as session:
        result = session.query(LoanRequest).filter(LoanRequest.id == id_).update(updated_data)
        session.commit()
    return bool(result)


def delete_loan_record(id_: int) -> bool:
    """Delete a loan record to the database

    Args:
    id_: loan record id which wants to be deleted."""
    with session_scope() as session:
        result = session.query(LoanRequest).filter(LoanRequest.id == id_).delete()
        session.commit()
    return bool(result)


def add_new_admin(user_to_register: Admin) -> bool:
    """Add new user into the admin database"""
    with session_scope() as session:
        registered_user = (
            session.query(AdminUser).filter(AdminUser.username == user_to_register.username).first()
        )
        if registered_user:
            return False
        session.add(
            AdminUser(
                username=user_to_register.username,
                password=user_to_register.password,
            )
        )
        session.commit()
    return True
