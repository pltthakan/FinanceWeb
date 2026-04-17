Tabii. Bu dokümanda hâlâ eski yapı yazıyor; özellikle **Jinja2 tabanlı view katmanı**, **tam sayfa yenileme mantığı** ve eski klasör yapısı güncellenmeli. Mevcut metinde frontend’in HTML/CSS/JS + Jinja2 olduğu ve sayfaların template üzerinden render edildiği yazıyor.  

Aşağıya direkt yapıştırabileceğin güncel sürümü bırakıyorum:

````md
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

The **Finance Tracking Application** is a modern web application that allows users to track real-time financial data, analyze historical trends through charts, and interact with finance-related content through social features.

The project has been restructured from a traditional Flask + Jinja multi-page application into a **React-based Single Page Application (SPA)** architecture. This change improves perceived performance, enables faster page transitions, and creates a more modern and responsive user experience.

The backend remains Flask-based and is now primarily responsible for serving **REST-style API endpoints**, authentication logic, and data access.

<img width="1470" height="956" alt="Ekran Resmi 2026-04-17 23 25 10" src="https://github.com/user-attachments/assets/59949f84-31ff-435f-ba34-aac4a28fe054" />


---

## Project Purpose & Scope

### Purpose

* **Real-time data:** Provide up-to-date exchange rates and asset prices
* **Fast navigation:** Eliminate full page reloads with SPA architecture
* **Trend tracking:** Visual indicators for price increases/decreases
* **Charts:** Daily, weekly, monthly, and yearly analysis
* **Shared live state:** Reuse fetched live data across multiple pages without unnecessary repeated requests
* **User experience:** Cleaner, smoother, and more responsive interface
* **Social features:** Support user interaction, comments, and profile-based features

### Scope

* **Frontend:** React + Vite + React Router
* **Backend:** Python + Flask API service
* **Database:** SQLite (can be extended later)
* **Data Source:** External financial APIs
* **UI Goal:** Lightweight, responsive, and navigation-friendly financial dashboard

---

## Architecture & System Design

### General Architecture

The project now follows a **frontend-backend separated architecture**:

* **Frontend (React SPA):** Responsible for rendering pages, routing, top bar, and client-side interactions
* **Backend (Flask API):** Provides financial data, historical data, authentication-related operations, and business logic
* **Shared State Layer:** Centralized client-side live data management using a context-based structure

This architecture removes the traditional server-rendered page flow and replaces it with a client-rendered interface that communicates with the backend through API calls.

### Components

* **React SPA Frontend**
  * Handles page transitions without full reload
  * Uses React Router for navigation
  * Improves responsiveness and user experience

* **LiveDataContext**
  * Centralized state manager for live financial data
  * Polls backend data periodically (for example every 60 seconds)
  * Prevents duplicate requests when moving between pages
  * Ensures top bar and homepage use the same live dataset

* **Flask API Backend**
  * Serves `/api/*` endpoints
  * Handles business logic and data processing
  * Can continue using existing backend logic with minimal disruption

* **Historical Chart Services**
  * Provides chart data for selected assets and time ranges
  * Used by analysis and asset detail pages

---

## Technologies Used

### Frontend

* React
* Vite
* React Router
* JavaScript
* CSS3

### Backend

* Python 3.x
* Flask

### State Management

* React Context API

### Database

* SQLite

### API

* Financial data APIs
* Historical asset data APIs

### Testing

* pytest
* Frontend component/page testing can be extended later

### Tools

* Git
* Docker
* npm

---

## Setup & Run

### Requirements

* Python 3.10+
* Node.js 18+
* npm
* Git

### Installation Steps

#### 1. Clone the repository

```bash
git clone https://github.com/pltthakan/FinanceWeb.git
cd FinanceWeb
````

#### 2. Backend setup

```bash
python -m venv env
source env/bin/activate   # macOS/Linux
pip install -r requirements.txt
python run.py
```

Backend runs by default on:

```text
http://localhost:5000
```

#### 3. Frontend setup

```bash
cd finance-react
npm install
npm run dev
```

Frontend runs by default on:

```text
http://localhost:5173
```

### Frontend Proxy

To simplify development, Vite can proxy API requests to Flask:

```js
server: {
  proxy: {
    '/api': 'http://localhost:5000',
    '/asset': 'http://localhost:5000'
  }
}
```

This allows the React frontend to call backend endpoints without manual CORS handling during development.

---

## File Structure & Modules

### Main Structure

```text
FinanceWeb/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── utils.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── profile.py
│   │   └── comments.py
│   └── static/
├── finance-react/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       ├── index.css
│       ├── context/
│       │   └── LiveDataContext.jsx
│       ├── components/
│       │   ├── Layout.jsx
│       │   ├── LiveRateBar.jsx
│       │   ├── Navbar.jsx
│       │   └── ParticlesBackground.jsx
│       └── pages/
│           ├── Home.jsx
│           ├── Converter.jsx
│           ├── Analysis.jsx
│           ├── News.jsx
│           ├── About.jsx
│           ├── Comments.jsx
│           ├── Profile.jsx
│           ├── Login.jsx
│           ├── Register.jsx
│           ├── AssetDetail.jsx
│           └── NotFound.jsx
├── run.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### Module Descriptions

* **app/** → Flask backend application
* **routes/** → API and backend route logic
* **finance-react/** → React frontend
* **LiveDataContext.jsx** → shared live market data state
* **components/** → reusable UI blocks
* **pages/** → route-level page components

---

## Use Cases & Features

### 1. Homepage

* Displays live financial data
* Uses shared live state from the client context
* Avoids refetching when navigating back from another page

### 2. Live Top Bar

* Shows financial items in a cleaner horizontal structure
* Designed to avoid broken wrapping issues
* Can behave like a ticker or horizontally scrollable chip row on small screens

### 3. Fast Navigation

* React Router enables route transitions without full page reload
* Improves perceived speed significantly

### 4. Data Visualization

* Asset detail and analysis pages display historical charts
* Supports multiple ranges such as daily, weekly, monthly, yearly

### 5. User Features

* Authentication pages
* Profile page
* Comment and interaction pages
* Expandable social-style features

---

## API Integration Details

### Backend Role

The Flask backend now primarily acts as an API provider rather than a template-rendering engine.

### Example Responsibilities

* Serve live financial data
* Provide historical chart data
* Handle authentication-related operations
* Deliver profile and comment-related backend logic

### Data Flow

1. React frontend requests data from `/api/*`
2. Flask processes and returns JSON responses
3. React components consume and render the data
4. Shared context distributes live data across pages and UI elements

---

## UI & Workflows

### Previous Limitation

In the older architecture, page transitions triggered full browser reloads because rendering was handled through Flask + Jinja templates. This negatively affected perceived speed and continuity.  

### Updated UI Flow

* React handles route changes on the client side
* Layout remains mounted while page content changes
* Top bar and homepage can consume the same live data source
* Navigation feels more fluid and modern

### Top Bar Improvement

The redesigned top bar is intended to:

* keep financial items aligned in a cleaner structure
* avoid asymmetric wrapping problems
* support smoother horizontal overflow on smaller screens
* improve readability and consistency

---

## Testing

### Backend Testing

* API endpoint validation
* Business logic checks
* Historical data and live data response testing

### Frontend Testing

* Route rendering tests
* Component behavior tests
* Shared state consistency tests
* UI responsiveness checks

### Manual Validation Goals

* No unnecessary reload on navigation
* Top bar remains stable across screen sizes
* Home page reuses cached/shared live data correctly
* Asset detail pages fetch the correct chart data

---

## Deployment

### Development Mode

Backend:

```bash
python run.py
```

Frontend:

```bash
cd finance-react
npm run dev
```

### Production Approach

Recommended production model:

* Build React frontend using Vite
* Serve compiled frontend separately or behind Flask/reverse proxy
* Keep Flask backend as API service
* Use Docker for containerized deployment

### Docker

Docker setup can be extended to support:

* Flask backend container
* React frontend build/container
* Reverse proxy if needed

---

## Troubleshooting & Support

### Common Issues

* **Frontend cannot reach backend:** Check Vite proxy or backend port
* **Slow data refresh:** Verify polling interval and API response times
* **Broken top bar layout:** Check responsive CSS and overflow handling
* **Missing chart data:** Verify backend asset/history endpoints
* **Dependency errors:** Reinstall both Python and npm dependencies

### Support

* GitHub Issues
* Email: [hakankocaeli15@gmail.com](mailto:hakankocaeli15@gmail.com)

---

## Contributors

* **Hakan Polat**

---

## Roadmap & Future Improvements

### Short-Term

* Finalize React SPA migration
* Improve top bar ticker responsiveness
* Expand API coverage for all pages
* Improve component-level error handling
* Add loading and skeleton states

### Mid-Term

* Better caching strategy for frequently requested data
* Authentication/session improvements
* More advanced chart filtering and comparisons
* Better mobile optimization

### Long-Term

* WebSocket-based real-time updates instead of polling
* Role-based access and stronger security
* Notification/alert system
* Multi-language support
* Premium analytics features

---

## Additional Resources

* Flask Documentation
* React Documentation
* Vite Documentation
* React Router Documentation
* Financial API provider documentation

```

