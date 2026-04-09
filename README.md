# Finance Tracking Application

## Table of Contents

1. Introduction
2. Project Purpose & Scope
3. Architecture & System Design
4. Technologies Used
5. Setup & Run
6. File Structure & Modules
7. Use Cases & Features
8. API Integration Details
9. UI & Workflows
10. Testing
11. Deployment
12. Troubleshooting & Support
13. Contributors & Contact
14. Roadmap & Future Improvements
15. License
16. Additional Resources

---

## Introduction

The **Finance Tracking Application** is a web application that allows users to track real-time financial data, analyze historical trends through charts, and interact with a social-network-like system.

This documentation explains the internal workings of the project, installation steps, usage, and potential improvements. 

---

## Project Purpose & Scope

### Purpose

* **Real-time data:** Provide up-to-date exchange rates
* **Trend tracking:** Visual indicators for price increases/decreases
* **Charts:** Daily, weekly, monthly, yearly analysis
* **User experience:** Simple and user-friendly interface
* **Social features:** Follow users, comment, and interact with financial data

### Scope

* **Data Source:** External API (Yahoo Finance)
* **UI:** Simple yet effective web interface
* **Backend:** Python/Flask-based system
* **Database:** SQLite (or alternatives)
* **Notifications:** Visual indicators (color, symbols, alerts) for price changes

---

## Architecture & System Design

### General Architecture

The project follows a layered structure similar to MVC (Model-View-Controller):

* **Model:** Manages and stores data (user preferences, historical data)
* **View:** UI built with HTML, CSS, JavaScript, and Jinja2
* **Controller:** Flask logic, routing, API handling, data processing

### Components

* **API Integration:** Fetches real-time financial data
* **Data Processing:** Cleans and formats API data
* **Testing:** Unit and integration tests ensure reliability

---

## Technologies Used

### Frontend

* HTML5, CSS3, JavaScript
* Bootstrap or TailwindCSS

### Backend

* Python 3.x
* Flask

### Templating

* Jinja2

### Database

* SQLite
* (Optional) PostgreSQL / MySQL

### API

* ExchangeRate API
* Yahoo Finance

### Testing

* pytest

### Tools

* Git
* Docker (optional)

---

## Setup & Run

### Requirements

* Python 3.1+
* Git
* Pipenv or virtualenv (optional)

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/Skarled5/FinanceWeb.git
cd doviz_takip
```

2. **Create a virtual environment**

Using virtualenv:

```bash
python -m venv env
source env/bin/activate   # macOS/Linux
env\Scripts\activate      # Windows
```

Or using Pipenv:

```bash
pipenv shell
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Environment variables**

Create a `.env` file:

```env
FLASK_APP=app/routes.py
FLASK_ENV=development
API_KEY=your_exchange_rate_api_key
SECRET_KEY=your_secret_key
```

5. **Run the application**

For production:

```bash
waitress-serve --listen=0.0.0.0:8000 app:app
```

Application runs at:

```
http://localhost:8000
```

> Note: Gunicorn is not supported on Windows. Use **Waitress** instead.

---

## File Structure & Modules

### Main Structure

```
doviz_takip/
├── app/
│   ├── __init__.py      
│   ├── admin.py        
│   ├── config.py          
│   ├── models.py        
│   ├── utils.py         
│   ├── static/          
│   └── templates/       
├── routes/
│   ├── auth.py
│   ├── main.py
│   ├── profile.py
│   └── comments.py
├── run.py
├── test.py
├── Dockerfile
├── README.md
└── LICENSE
```

### Module Descriptions

* **app/**init**.py:** Initializes Flask app and database
* **admin.py:** Admin panel setup
* **config.py:** Configuration settings
* **models.py:** Database models and social features
* **utils.py:** Helper functions for financial data
* **routes/**:

  * `auth.py` → authentication
  * `main.py` → main pages
  * `profile.py` → user profile
  * `comments.py` → comments system

---

## Use Cases & Features

### 1. Homepage

* Displays real-time financial data
* Auto-refreshes via API

### 2. Live Change Indicator

* Green arrow → increase
* Red arrow → decrease

### 3. Data Visualization

* Line and bar charts
* Date range selection
* Interactive graphs

---

## API Integration Details

### External Data Source

* Uses Yahoo Finance API
* Data retrieved periodically

### Data Processing

* JSON parsing
* Data transformation into models
* Error handling (timeouts, invalid data, retries)

---

## UI & Workflows

### Homepage

* Uses `templates/index.html`
* Dynamic rendering with Jinja2

### User Interactions

* Forms for currency conversion and alerts
* AJAX-based dynamic updates

---

## Testing

* Selenium-based automated tests
* Validates:

  * Page loads
  * Authentication
  * Currency conversion
  * Comments and profile features

---

## Deployment

### Running

* Run via `run.py`
* Access via `http://localhost:8000`

### Production

* Use Gunicorn / uWSGI

### Docker (Optional)

Example Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app/routes.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
```

---

## Troubleshooting & Support

### Common Issues

* **API errors:** Check API key and connection
* **Database issues:** Verify configuration
* **Environment variables:** Ensure `.env` is correct
* **Server errors:** Check Flask logs

### Support

* GitHub Issues
* Email: [hakankocaeli15@gmail.com](mailto:hakankocaeli15@gmail.com)

---

## Contributors

* **Hakan Polat**

---

## Roadmap & Future Improvements

### Short-Term

* Add authentication system
* Improve charts (Chart.js / D3.js)
* Enhance mobile responsiveness

### Long-Term

* WebSocket for real-time updates
* Multi-language support (i18n)
* Payment integration / premium features
* Advanced security (rate limiting, CSRF protection)

---

## Additional Resources

* Flask Documentation
* Requests Library
* Jinja2
* Yahoo Finance API
* Crypto Panic API
