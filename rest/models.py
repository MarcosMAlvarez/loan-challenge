"""Loan api models"""
from enum import Enum
import re
from typing import Optional

from pydantic import BaseModel
from pydantic.networks import EmailStr


class SexEnum(str, Enum):
    """Sex must be masculino or femenino"""

    male = "masculino"
    female = "femenino"


class FullName(str):
    """Validate that full name is a string with only alphabetic characters and whitespaces"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError("String required")
        if re.search(r"[^a-zA-Z\s]", value):
            raise ValueError("Full name only can have alphabetic characters")
        return cls(value)


class DNI(int):
    """Validate that dni is an integer between a million and a hundred million"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, int):
            raise TypeError("Integer required")
        if not 10 ** 6 < value < 10 ** 8:
            raise ValueError("Verify DNI number")
        return cls(value)


class Person(BaseModel):
    dni: DNI
    full_name: FullName
    genre: SexEnum
    email: EmailStr
    loan_amount: float


class LoanRecord(BaseModel):
    dni: Optional[DNI] = None
    full_name: Optional[FullName] = None
    genre: Optional[SexEnum] = None
    email: Optional[EmailStr] = None
    loan_amount: Optional[float] = None
    status: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Admin(BaseModel):
    username: str
    password: str
