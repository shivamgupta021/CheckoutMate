# API Documentation

## Table of Contents

1. **[Introduction](#introduction)**

2. **[Setup and Installation](#setup-and-installation)**

3. **[Authentication](#authentication)**
    - 3.1 [Obtaining Credentials](#obtaining-credentials)
    - 3.2 [Example Authenticated Request](#example-authenticated-request)

4. **[Endpoints](#endpoints)**
    - 4.1 [Users](#users)
        - 4.1.1 [List Users](#list-users)
        - 4.1.2 [Get User](#get-user)
        - 4.1.3 [Create User](#create-user)
        - 4.1.4 [Update User](#update-user)
        - 4.1.5 [Delete User](#delete-user)
    - 4.2 [Posts](#posts)
        - **4.2.1 [List Posts](#list-posts)
        - 4.2.2 [Get Post](#get-post)
        - 4.2.3 [Create Post](#create-post)
        - 4.2.4 [Update Post](#update-post)
        - 4.2.5 [Delete Post](#delete-post)


5. **[Testing](#testing)**
    - **5.1** [Running Tests](#running-tests)
    - **5.2** [Test Coverage](#test-coverage)

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

To obtain a JWT token, users (customers or employees) must authenticate by sending their credentials to
the `/auth/login/` endpoint. Upon successful authentication, a JWT token will be returned, which must be included in
the `Authorization header of future requests.

### Obtaining Credentials

- Login Request:

    ```bash
    POST /api/user/login/
    Content-Type: application/json
    
    {
      "email": "customer@checkoutmate.com",
      "password": "supersecretpassword",
      "password2": "supersecretpassword"
    }
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
  curl -X POST api/products/ \
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
