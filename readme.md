# API Documentation

## Table of Contents

- [Introduction](#introduction)
- [Setup and Installation](#setup-and-installation)
- [Authentication](#authentication)
    - [Obtaining Credentials](#obtaining-credentials)
    - [Example Authenticated Request](#example-authenticated-request)
- [Endpoints](#endpoints)
    - [Accounts](#accounts)
    - [Products](#products)
- [Testing](#testing)
    - [Running Tests](#running-tests)
    - [Test Coverage](#test-coverage)

## Introduction

This a web API, built with Django and Django Rest Framework, is designed to handle e-commerce operations using
PostgreSQL.
It offers functionalities for both customers and employees. Customers can browse and manage products in their cart, as
well as generate and receive bills via email. Employees are responsible for managing inventory, with the ability to
create, retrieve, update, and delete inventory items. They also receive daily inventory updates via email, and if
product stock falls below a critical level, they are notified every 20 minutes to restock.

## Setup and Installation

[Python](https://www.python.org/downloads/release/python-3124/) version used - 3.12.4

- #### Clone the GitHub repository

  Make sure git is [setup](https://www.theodinproject.com/lessons/foundations-setting-up-git) properly on your system.

   ```bash
   git clone https://github.com/shivamgupta021/CheckoutMate.git && cd CheckoutMate
   ```

- #### Create and activate a virtual environment
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   ```

- #### Install dependencies
   ```bash
   pip install poetry && poetry install
   ```

- #### Apply changes to the database schema
   ```bash
   python manage.py migrate
   ```

- #### Create a superuser account
   ```bash
   python manage.py createsuperuser
   ```

- #### Run the server
   ```bash
   python manage.py runserver
   ```
- #### Run celery worker
  In a separate terminal navigate to the project root and -
   ```bash
   celery -A backend worker -l info
   ```
- #### Run celery beat
  In a separate terminal navigate to the project root and -
   ```bash
   celery -A backend beat -l info
   ```

## Authentication

The API uses **JSON Web Tokens (JWT)** for authentication. JWT is a secure way to handle authentication by including the
token in the `Authorization` header for each request.

- **Token Type**: Bearer Token (JWT)
- **Roles**:
    - **Customers**: Have access to endpoints related to browsing products, managing their cart, and generating bills.
    - **Employees**: Have access to manage the inventory, including creating, updating, and deleting products.

### Obtaining Credentials

- Login Request:

    ```bash
    curl -X POST 127.0.0.1:8000/api/user/login/ \
    -H "Content-Type: application/json" \
    -d '{
      "email": "customer@checkoutmate.com",
      "password": "supersecretpassword",
      "password2": "supersecretpassword"
    }'
    ```
- Successful Response:

    ```bash
    {
      "token": {
        "refresh": <refresh_token>,
        "access": <access_token>
      },
      "message": "Login Successful!"
    }
    ```

### Example Authenticated Request

```bash
# Requires Employee Authentication
curl -X POST 127.0.0.1:8000/api/products/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
"name": "Pants",
"description": "Either hard professor financial store dark security agency. Audience important determine a.",
"price": 88.55,
"quantity": 992
}'
```

## Endpoints

### Accounts

- Register an Employee or Customer
    ```bash
    curl -X POST 127.0.0.1:8000/api/user/register/ \
    -H "Content-Type: application/json" \
    -d '{
      "role": "EMPLOYEE",
      "name": "Maurice Randolph",
      "age": 38,
      "email": "employee@checkoutmate.com",
      "password": "supersecretpassword",
      "password2": "supersecretpassword"
      }'
      # OR
    -d '{  "role": "CUSTOMER",
      "name": "Donald Anderson",
      "age": 42,
      "email": "customer@checkoutmate.com",
      "password": "supersecretpassword",
      "password2": "supersecretpassword"
    }'
    ```
- Login an Employee or Customer
    ```bash
    curl -X POST 127.0.0.1:8000/api/user/register/ \
    -H "Content-Type: application/json" \
    -d '{
      "email": "employee.email@checkoutmate.com",
      "password": "supersecretpassword",
      "password2": "supersecretpassword"
    }'
    # OR
    -d '{
      "email": "customer.email@checkoutmate.com",
      "password": "supersecretpassword",
      "password2": "supersecretpassword"
    }'
    ```
- Change Password : Requires authentication
    ```bash
    curl -X POST 127.0.0.1:8000/api/user/change-password/ \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d '{
      "password": "notsosecretpassword",
      "password2": "notsosecretpassword"
    }'
    ```

### Products

- List all Products
  ```bash
  curl -X GET 127.0.0.1:8000/api/products/ \
  -H "Content-Type: application/json"
  ```
- Retrieve a single Product
   ```bash
  curl -X GET 127.0.0.1:8000/api/products/{id}/ \
  -H "Content-Type: application/json"
  ```
- Create a new Product : Requires Employee Authentication
  ```bash
  curl -X POST 127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pants",
    "description": "Significant natural actually brother bring. Admit four what dream anything usually research science.",
    "price": 87.91,
    "quantity": 587
  }'
  ```
- Update an existing Product: Requires Employee Authentication
    - PUT:
      ```bash
      curl -X PUT 127.0.0.1:8000/api/products/{id}/ \
      -H "Authorization: Bearer <access_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "New Product",
        "description": "Significant natural actually brother bring. Admit four what dream anything usually research science.",
        "price": 87.91,
        "quantity": 587
      }'
      ```
    - PATCH:
      ```bash
      curl -X PATCH 127.0.0.1:8000/api/products/{id}/ \
      -H "Authorization: Bearer <access_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "quantity": 587
      }'
      ```
- Delete a Product: Requires Employee Authentication
  ```bash
  curl -X DELETE 127.0.0.1:8000/api/products/{id}/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" 
  ```

## Query Optimisations -

**OVERALL TIME IS HIGH DUE TO SERVERS** \
[Commit](https://github.com/shivamgupta021/CheckoutMate/commit/2093ab482bad09a0e6156cc2a2eacc1e082d482e)

#### Before :

![img.png](https://github.com/user-attachments/assets/c77b893c-6adb-4c15-bc29-ab86d4d59b23)

#### After :

- Optimised the number of queries using select_related, prefetch_related, bulk_update and bulk_add functions, improving
  the response time and removing redundancy.
  ![img_1.png](https://github.com/user-attachments/assets/52f1627c-bb7a-4fb6-89e4-ba2a6eae6a38)