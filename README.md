# Market

## Introduction

The Market project is a web application built using Flask, a lightweight WSGI web framework in Python. This application is designed to manage and interact with marketplace functionalities. Whether you're managing a small business or a larger marketplace, this application can be customized to suit your needs.

## Features

- **Flask-based Web Application**: Lightweight and highly customizable.
- **User Authentication**: Secure login and registration system.
- **Product Management**: Add, edit, and delete products in the market.
- **Real-time Notifications**: Using Blinker for real-time updates.
- **Responsive Design**: Mobile-first design using Jinja2 templating.

## Installation

### Prerequisites

Make sure you have the following installed:

- Python 3.x
- pip (Python package installer)

### Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/shishpal0666/Market.git
    cd Market
    ```

2. Create a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask application:

    ```bash
    flask market
    ```

## Usage

Once the server is running, you can access the application in your web browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

### Admin Features

- Manage products and categories.
- Monitor user activity and sales.
- Generate reports for market analysis.

### User Features

- Browse products by categories.
- Add products to the cart and proceed to checkout.
- Track orders and receive notifications on order status.

## Documentation

For more detailed documentation on how to use and customize this application, please refer to the official [Flask documentation](https://flask.palletsprojects.com/).

## Contact Information

For questions or collaboration requests, please reach out via [email](mailto:shishpalpolampally@gmail.com).

