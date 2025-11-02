# Stock Analysis System

An intelligent stock analysis and alert system powered by AI agents, featuring multi-dimensional analysis, real-time monitoring, and role-based access control.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [User Roles](#user-roles)
- [Key Features](#key-features)
- [Development Status](#development-status)

## ✨ Features

### Core Functionality
- **Real-time Stock Monitoring**: Track stock prices and market data with automatic updates
- **Multi-dimensional Analysis**: Technical, fundamental, sentiment, and risk analysis
- **Intelligent Alert System**: Customizable price alerts with cumulative trigger logic
- **Portfolio Management**: Track investments, calculate P&L, and monitor performance
- **AI-Powered Analysis**: LangChain-based agents for comprehensive stock analysis
- **Automated Report Generation**: Generate detailed analysis reports automatically

### Role-Based Features

#### Investor Features
- Personal dashboard with portfolio overview
- Stock search and tracking
- Custom alert configuration
- Portfolio management
- AI assistant for investment queries
- Report viewing and generation

#### Advisor Features
- Client portfolio management
- Multi-client dashboard
- Client analytics and insights
- Report generation and sharing
- Client alert monitoring
- AI-powered investment recommendations

#### Admin Features
- System dashboard with key metrics
- User management (create, update, delete, activate/deactivate)
- Role management and permissions
- System performance monitoring
- Background task management
- System logs viewer
- System settings configuration

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: MySQL (with SQLAlchemy ORM 2.0.36)
- **Authentication**: JWT (python-jose, passlib)
- **AI/ML**: LangChain, LangGraph, OpenAI
- **Task Queue**: APScheduler for scheduled tasks
- **API Client**: yfinance for stock data, httpx for HTTP requests

### Frontend
- **Framework**: React 18.2 with TypeScript
- **UI Library**: Ant Design 5.12.0
- **Routing**: React Router DOM 6.20.0
- **State Management**: Zustand 4.4.7
- **Charts**: Recharts 2.10.3, @ant-design/charts
- **Build Tool**: Vite 5.0.8
- **HTTP Client**: Axios 1.6.2

### Infrastructure
- **Language**: Python 3.x
- **Server**: Uvicorn (ASGI server)
- **Logging**: Structured JSON logging
- **Monitoring**: System metrics collection (CPU, Memory, Disk)

## 🏗 System Architecture

```
┌─────────────────┐
│   Frontend      │  React + TypeScript + Ant Design
│   (Port 5173)   │
└────────┬────────┘
         │ REST API
┌────────▼────────┐
│   Backend API   │  FastAPI
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬─────────────┐
    │         │              │             │
┌───▼───┐ ┌──▼───┐ ┌────────▼──┐ ┌───────▼────┐
│ MySQL │ │Redis │ │  LangChain │ │  External  │
│       │ │(Tasks)│ │  Agents    │ │   APIs     │
└───────┘ └──────┘ └────────────┘ └────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis (optional, for Celery)

### Backend Setup

1. **Clone the repository**
```bash
cd stock-analysis-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the `stock-analysis-system` directory:
```env
# Database
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/stock_analysis

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI (for AI features)
OPENAI_API_KEY=your-openai-api-key

# External APIs (optional)
NEWS_API_KEY=your-news-api-key
```

5. **Initialize database**
```bash
# Option 1: Use existing init script
python init_db.py

# Option 2: MySQL setup script
python setup_mysql.py
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../stock-analysis-frontend
```

2. **Install dependencies**
```bash
npm install
```

## ⚙️ Configuration

### Database Configuration
The system uses MySQL as the primary database. Ensure MySQL is running and accessible.

### API Keys
- **OpenAI API Key**: Required for AI-powered analysis features
- **News API Key**: Optional, for news aggregation

### Port Configuration
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## 🚀 Running the Application

### Start Backend

1. **Activate virtual environment**
```bash
source venv/bin/activate
```

2. **Run the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Start background scheduler** (in a separate terminal)
```bash
python start_celery.py
```

### Start Frontend

1. **Navigate to frontend directory**
```bash
cd stock-analysis-frontend
```

2. **Start development server**
```bash
npm run dev
```

3. **Access the application**
Open your browser and navigate to `http://localhost:5173`

### API Documentation
Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
stock-analysis-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and session
│   ├── scheduler.py            # Background task scheduler
│   │
│   ├── models/                 # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── stock.py
│   │   ├── portfolio.py
│   │   ├── alert.py
│   │   ├── report.py
│   │   └── ...
│   │
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── stock.py
│   │   └── ...
│   │
│   ├── api/                     # API route handlers
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── stocks.py           # Stock data endpoints
│   │   ├── portfolio.py        # Portfolio management
│   │   ├── alerts.py           # Alert management
│   │   ├── reports.py          # Report generation
│   │   ├── admin.py            # Admin panel endpoints
│   │   ├── advisor.py          # Advisor-specific endpoints
│   │   ├── chat.py             # AI chat endpoints
│   │   ├── monitoring.py       # System monitoring
│   │   └── tasks.py            # Background tasks
│   │
│   ├── agents/                  # AI agent implementations
│   │   ├── agent_manager.py    # Agent orchestration
│   │   ├── analysis_agent.py  # Stock analysis agent
│   │   ├── data_collection_agent.py
│   │   ├── risk_analysis_agent.py
│   │   └── ...
│   │
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── stock_service.py    # Stock operations
│   │   ├── portfolio_service.py
│   │   ├── alert_service.py
│   │   ├── report_service.py
│   │   ├── ai/
│   │   │   └── langchain_service.py  # LangChain integration
│   │   └── ...
│   │
│   ├── repositories/           # Data access layer
│   │   ├── user_repository.py
│   │   ├── stock_repository.py
│   │   └── ...
│   │
│   ├── tasks/                   # Background tasks (Celery)
│   │   ├── data_update_tasks.py
│   │   ├── alert_tasks.py
│   │   ├── report_tasks.py
│   │   └── monitoring_tasks.py
│   │
│   ├── external/                # External API clients
│   │   ├── stock_api_client.py
│   │   └── news_api_client.py
│   │
│   ├── core/                    # Core functionality
│   │   ├── logging.py          # Structured logging
│   │   ├── security.py         # Security utilities
│   │   ├── error_handlers.py   # Error handling
│   │   └── database_operations.py
│   │
│   └── utils/                   # Utility functions
│       └── validators.py
│
├── stock-analysis-frontend/
│   ├── src/
│   │   ├── pages/              # React page components
│   │   │   ├── admin/          # Admin panel pages
│   │   │   ├── advisor/        # Advisor dashboard
│   │   │   ├── investor/       # Investor dashboard
│   │   │   └── auth/           # Authentication pages
│   │   │
│   │   ├── services/           # API service layer
│   │   │   ├── api.ts
│   │   │   ├── authService.ts
│   │   │   ├── stockService.ts
│   │   │   └── ...
│   │   │
│   │   ├── stores/             # State management
│   │   │   └── authStore.ts
│   │   │
│   │   ├── types/              # TypeScript type definitions
│   │   │   └── index.ts
│   │   │
│   │   └── utils/              # Utility functions
│   │       └── tokenRefresh.ts
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── requirements.txt            # Python dependencies
├── init_db.py                  # Database initialization script
├── setup_mysql.py              # MySQL setup script
└── README.md                   # This file
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### Stock Endpoints
- `GET /api/v1/stocks` - List all stocks
- `GET /api/v1/stocks/{id}` - Get stock details
- `GET /api/v1/stocks/search` - Search stocks
- `GET /api/v1/stocks/{id}/data` - Get historical data

### Portfolio Endpoints
- `GET /api/v1/portfolio` - Get user portfolio
- `POST /api/v1/portfolio` - Add stock to portfolio
- `PUT /api/v1/portfolio/{id}` - Update portfolio entry
- `DELETE /api/v1/portfolio/{id}` - Remove from portfolio

### Alert Endpoints
- `GET /api/v1/alerts` - Get user alerts
- `POST /api/v1/alerts` - Create new alert
- `PUT /api/v1/alerts/{id}` - Update alert
- `DELETE /api/v1/alerts/{id}` - Delete alert

### Report Endpoints
- `GET /api/v1/reports` - Get user reports
- `POST /api/v1/reports/generate` - Generate new report
- `GET /api/v1/reports/{id}` - Get report details

### Admin Endpoints
- `GET /api/v1/admin/dashboard` - Admin dashboard stats
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users` - Create user
- `PUT /api/v1/admin/users/{id}` - Update user
- `GET /api/v1/admin/logs` - System logs
- `GET /api/v1/admin/tasks/list` - Background tasks

### Advisor Endpoints
- `GET /api/v1/advisor/dashboard` - Advisor dashboard
- `GET /api/v1/advisor/clients` - List clients
- `GET /api/v1/advisor/portfolios` - Client portfolios
- `GET /api/v1/advisor/reports` - Client reports

### AI Chat Endpoints
- `POST /api/v1/chat` - Chat with AI assistant
- `GET /api/v1/chat/history` - Get chat history

## 👥 User Roles

### 1. Individual Investor (INVESTOR)
**Capabilities:**
- Track personal portfolio
- Search and monitor stocks
- Set up price alerts
- Generate stock analysis reports
- Chat with AI assistant
- View investment recommendations

**Access:**
- Personal dashboard
- Portfolio management
- Stock search and tracking
- Alert configuration
- Report viewing

### 2. Financial Advisor (ADVISOR)
**Capabilities:**
- Manage multiple client portfolios
- View client analytics and insights
- Generate comprehensive reports
- Monitor client alerts
- Access AI-powered recommendations
- View client performance metrics

**Access:**
- Multi-client dashboard
- Client portfolio management
- Report generation
- Client analytics
- Alert monitoring

### 3. System Administrator (ADMIN)
**Capabilities:**
- User management (create, update, delete, activate/deactivate)
- Role management and assignment
- System performance monitoring
- Background task management
- System logs viewing
- System configuration

**Access:**
- Admin dashboard
- User management
- Role management
- System monitoring (Performance, Tasks, Logs)
- System settings

## 🔑 Key Features

### 1. Intelligent Alert System
- **Cumulative Trigger Logic**: Alerts trigger after multiple consecutive condition matches
- **Custom Thresholds**: Set custom alert thresholds per stock
- **Multiple Alert Types**: Price drop, price spike, volatility, volume anomaly
- **Real-time Monitoring**: Background scheduler checks alerts every minute

### 2. AI-Powered Analysis
- **Multi-agent Architecture**: Specialized agents for different analysis types
- **LangChain Integration**: Leverages LangChain and LangGraph for agent orchestration
- **Comprehensive Reports**: Technical, fundamental, sentiment, and risk analysis
- **AI Chat Assistant**: Interactive chat for investment queries

### 3. Portfolio Management
- **Real-time P&L Calculation**: Automatic profit/loss calculation
- **Performance Tracking**: Track portfolio performance over time
- **Multi-stock Portfolio**: Support for multiple stocks per user
- **Historical Data**: View portfolio history

### 4. System Monitoring (Admin)
- **Performance Metrics**: CPU, Memory, Disk usage monitoring
- **Background Tasks**: View and manage Celery tasks
- **System Logs**: Structured logging with filtering and search
- **Task Management**: Monitor scheduled and active tasks

### 5. Security Features
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Argon2 password hashing
- **Role-Based Access Control**: Fine-grained permission system
- **Token Refresh**: Automatic token refresh mechanism

## 📊 Development Status

### ✅ Completed Features

#### Backend
- ✅ User authentication and authorization
- ✅ Stock data management and API integration
- ✅ Portfolio management
- ✅ Alert system with cumulative triggers
- ✅ Report generation with AI agents
- ✅ Admin panel APIs
- ✅ Advisor-specific features
- ✅ AI chat assistant
- ✅ System monitoring endpoints
- ✅ Background task scheduling
- ✅ Structured logging

#### Frontend
- ✅ Investor dashboard and features
- ✅ Advisor dashboard with client management
- ✅ Admin panel (Dashboard, User Management, Role Management)
- ✅ System monitoring pages (Performance, Tasks, Logs)
- ✅ System settings page
- ✅ AI chat interface
- ✅ Responsive design with Ant Design

### 🔄 Current Status
The system is **fully functional** with all core features implemented. The application is ready for deployment and further enhancements.

## 📝 License

MIT

## 🤝 Contributing

This is a university project for ELEC5620. For contributions or questions, please contact the development team.

## 📧 Contact

For issues or questions, please refer to the project documentation or contact the development team.

---

**Last Updated**: November 2025
**Version**: 1.0.0
