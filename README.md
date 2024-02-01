# Library Service API
##### ** Welcome to the library service, where you can borrow books **


The system optimizes the work of library administrators and makes the service much more user-friendly.

## Key Features

### Books Service
- **CRUD**: Implemented CRUD functionality for Books Service.
- **Permission**: Only admin users can create, update or delete books. But all users, even anon users, can list books.
### Users Service
- **CRUD**: Implemented CRUD for Users Service.
- **Email**: User model with email field instead of username.
### Borrowing Service
- **Create Borrowing**: Implemented the creation of borrowings.
- **Filtering**: Added filtering for the Borrowings List endpoint
- **Security**: Non-admin users can see only their borrowings.
- **Return Borrowing Functionality:** Implemented the return of the borrowed book with the change of the book inventory, the return cannot be made twice.
- **Telegram Notifications:** Integrated sending notifications on new borrowing creation with Telegram API.
#### JWT Token Authentication
- Integrated JWT token authentication for secure authentication.
- **ModHeader**: Change the default `Authorization` header for JWT authentication to a custom `Authorize` header.

## Test Coverage Report

```plaintext
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
book\__init__.py                            0      0   100%
book\admin.py                               3      0   100%
book\apps.py                                4      0   100%
book\migrations\0001_initial.py             5      0   100%
book\migrations\__init__.py                 0      0   100%
book\models.py                             20      1    95%
book\permissions.py                         4      0   100%
book\serializers.py                         6      0   100%
book\tests\__init__.py                      0      0   100%
book\tests\test_book_api.py                72      0   100%
book\urls.py                                7      0   100%
book\views.py                               8      0   100%
borrowing\__init__.py                       0      0   100%
borrowing\admin.py                          3      0   100%
borrowing\apps.py                           4      0   100%
borrowing\migrations\0001_initial.py        7      0   100%
borrowing\migrations\__init__.py            0      0   100%
borrowing\models.py                        28      2    93%
borrowing\serializers.py                   48      0   100%
borrowing\tests\__init__.py                 0      0   100%
borrowing\tests\test_borrowing_api.py     130      0   100%
borrowing\urls.py                           7      0   100%
borrowing\views.py                         43      1    98%
library_api_service\__init__.py             0      0   100%
library_api_service\asgi.py                 4      4     0%
library_api_service\settings.py            29      0   100%
library_api_service\urls.py                 4      0   100%
library_api_service\wsgi.py                 4      4     0%
manage.py                                  12      2    83%
telegram_helper\__init__.py                 0      0   100%
telegram_helper\bot.py                      6      0   100%
user\__init__.py                            0      0   100%
user\admin.py                              11      0   100%
user\apps.py                                4      0   100%
user\migrations\0001_initial.py             7      0   100%
user\migrations\__init__.py                 0      0   100%
user\models.py                             31      8    74%
user\serializers.py                        17      7    59%
user\tests.py                               1      0   100%
user\urls.py                                5      0   100%
user\views.py                              13      1    92%
-----------------------------------------------------------
TOTAL                                     547     30    95%

```

## Installing Using GitHub

Ensure you have `Python 3` installed.
Install `PostgreSQL` and create db.

#### Clone the repo:
```bash
git clone https://github.com/KolBohdan/library-api-service
cd library_api_service
```

For Windows users:
```bash
python -m venv venv
source venv/Scripts/activate
```
For macOS/Linux users:
```bash
python3 -m venv venv
source venv/bin/activate
```
Install requirements:
```bash
pip install -r requirements.txt
```

### Set your variables
You should set up  .env file with these variables:
```
POSTGRES_HOST=POSTGRES_HOST
POSTGRES_DB=POSTGRES_DB
POSTGRES_USER=POSTGRES_USER
POSTGRES_PASSWORD=POSTGRES_PASSWORD
TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=TELEGRAM_CHAT_ID
DJANGO_SECRET_KEY=DJANGO_SECRET_KEY
```

### Migrate db and create user

```bash
python manage.py migrate
```
You can create admin user:
```bash
python manage.py createsuperuser
```
###### or use default user as described in the ''Getting access'' section.
### Run server:
- For Windows users:
```bash
python manage.py runserver
```
- For macOS/Linux users:
```bash
python3 manage.py runserver
```

## Run with docker

`Docker` should be installed.

```
docker-compose build
docker-compose up
```

## Getting access
- create a user via **/api/users/register/**
- get access token via **/api/users/token/**

## Library Service endpoints
You can use next endpoints:
```
Books:

/api/books/ - GET list of books and POST method there;
/api/books/{id}/ - GET detail book page and there PUT, PATCH and DELETE methods for admin;

Borrowings:

/api/borrowings/ - GET list of borrowings and POST method there;
/api/borrowings/{id}/ - GET detail borrowing;
/api/borrowings/{id}/return/ - POST method which return the borrowing

Users:

/api/users/me/ - GET user page and there PUT and PATCH methods available;
/api/users/register/ - registration page;
/api/users/token/ - get token page;

More details in Swagger doc 
```

## Swagger documentation
![documentation.png](project_preview%2Fdocumentation.png)