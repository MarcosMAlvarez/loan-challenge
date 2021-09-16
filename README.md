# Loan Challenge

API where loan requests are registered and validated. The loan requests can be queried, modified and deleted by an user with administrator privileges

## Postman collection

In the link below you can test the API endpoint.

`https://www.getpostman.com/collections/bf261de2e242514deb8a`

## Deployment

The project uses pipenv for the virtual environment. To install and run it:

```bash
pip install pipenv

#inside loan-challenge directory
pipenv sync
pipenv shell
```

Then, to run the application, execute the next command:

```bash
uvicorn main:app
```

The app will be running in localhost:8000

## Endpoints

### /sign-up - POST

The endpoint needs a request body with user information to sign up as administrator. Username must be unique. The required json has the following structure:

```
{
  "username": "string",
  "password": "string"
}
```

### /token - POST

The endpoint receives username and password as form data and retrieves a token required to consume the endpoints that require authentication.

### /admin - GET

This endpoint returns all the load requests that has been made

### /admin - PATCH

This endpoint update a load record. Needs a "id_" query parameter and a body request with the new information to update the record with. The body request has the following structure, not all the field are required:

```
{
  "dni": 0,
  "full_name": "string",
  "genre": "masculino",
  "email": "user@example.com",
  "loan_amount": 0
}
```

### /admin - DELETE

This endpoint delete a load record. Needs a "id_" query parameter to know which record delete.

### /check-loan - POST

This endpoint receives a person's information with the loan amount, as body request and calls the moni's endpoint to validate the loan. The endpoint return if the loan has been approved or not. The body request has the following structure:

```
{
  "dni": 0,
  "full_name": "string",
  "genre": "masculino",
  "email": "user@example.com",
  "loan_amount": 0
}
```
