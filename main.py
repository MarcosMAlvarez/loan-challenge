"""
Loan Challenge
"""

from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import requests

from settings import MONI_CREDENTIALS, ACCESS_TOKEN_EXPIRE_MINUTES
from rest.models import Admin, Person, Token, LoanRecord
import rest.helpers as helpers
import db.helpers

app = FastAPI(
    title="Loan Challenge",
    version="0.0.1",
    description="API to validate access to a personal loan.",
)

# Throttling exception for rate limit
@app.exception_handler(helpers.RateLimitException)
async def rate_limit_exception_handler(*args, **kwargs):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error msg": f"Rate-limit reached. The API call frequency is {helpers.MAX_LEN} per {helpers.SECONDS} seconds."
        },
    )

@app.post("/sign-up/", status_code=status.HTTP_201_CREATED)
async def sign_up(user_to_register: Admin):
    """Endpoint to register a new user. Both username and email address must be unique"""
    result = db.helpers.add_new_admin(user_to_register)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username {user_to_register.username} already exist in database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"msg": "User has been successfully registered"}


@app.post("/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """An authorized user can log in to get a token"""
    user = helpers.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = helpers.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/admin/")
async def get_stock_information(token: str = Depends(helpers.oauth2_scheme)):
    """Returns all loan records in the database"""
    await helpers.check_credentials(token)
    return db.helpers.get_loan_records()


@app.patch("/admin/")
async def update_loan_record(
    id_: int, updated_loan_data: LoanRecord, token: str = Depends(helpers.oauth2_scheme)
):
    """Update loan record.

    Updates the loan record with id equals to id_ with the information passed as body request."""
    await helpers.check_credentials(token)
    result = db.helpers.update_loan_record(id_, jsonable_encoder(updated_loan_data))
    if result:
        return {"msg": f"Loan record with id={id_} as been updated"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"There is no record with id={id_}.",
        )


@app.delete("/admin/")
async def delete_loan_record(id_: int, token: str = Depends(helpers.oauth2_scheme)):
    """Delete the loan record with id equals to id_"""
    await helpers.check_credentials(token)
    result = db.helpers.delete_loan_record(id_)
    if result:
        return {"msg": f"Loan record with id={id_} as been deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"There is no record with id={id_}.",
        )


@app.post("/check-loan/")
@helpers.rate_limit(maxlen=helpers.MAX_LEN, seconds=helpers.SECONDS)
async def check_loan_access(person_data: Person):
    """Verify loan access.

    Given a person's data information, the endpoint calls moni API to verify the loan access."""
    header = {"credential": MONI_CREDENTIALS}
    url = f"https://api.moni.com.ar/api/v4/scoring/pre-score/{person_data.dni}"
    response = requests.get(url, headers=header).json()
    if response["has_error"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify the data entered.",
        )
    db.helpers.add_loan_record(person_data, response["status"])
    return {"loan_status": response["status"]}
