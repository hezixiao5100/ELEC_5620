# Stock Analysis System Documentation

## Architecture Overview

This system follows a layered architecture:

1. **API Layer** (`app/api/`): RESTful API endpoints
2. **Service Layer** (`app/services/`): Business logic
3. **Agent Layer** (`app/agents/`): AI agents for analysis
4. **Repository Layer** (`app/repositories/`): Data access
5. **Model Layer** (`app/models/`): Database models

## Key Components

### AI Agents

- **AgentManager**: Coordinates all agents
- **DataCollectionAgent**: Collects stock data and news
- **RiskAnalysisAgent**: Analyzes investment risks
- **AnalysisAgent**: Performs technical and fundamental analysis
- **EmotionalAnalysisAgent**: Analyzes sentiment
- **ReportGenerateAgent**: Generates comprehensive reports

### User Roles

1. **Individual Investor**: Track stocks, receive alerts, view reports
2. **Financial Advisor**: Manage client portfolios
3. **System Administrator**: System management and monitoring

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Stocks
- `POST /api/v1/stocks/track` - Track a stock
- `DELETE /api/v1/stocks/track/{symbol}` - Untrack a stock
- `GET /api/v1/stocks/tracked` - Get tracked stocks
- `GET /api/v1/stocks/{symbol}` - Get stock info

### Portfolio
- `GET /api/v1/portfolio/overview` - Get portfolio overview
- `POST /api/v1/portfolio/analyze` - Analyze portfolio
- `GET /api/v1/portfolio/risk-assessment` - Get risk assessment

### Reports
- `POST /api/v1/reports/generate` - Generate analysis report
- `GET /api/v1/reports/` - Get user reports
- `GET /api/v1/reports/{report_id}` - Get specific report

### Alerts
- `GET /api/v1/alerts/` - Get user alerts
- `GET /api/v1/alerts/active` - Get active alerts
- `POST /api/v1/alerts/{alert_id}/acknowledge` - Acknowledge alert

### Admin
- `GET /api/v1/admin/users` - Get all users
- `PUT /api/v1/admin/users/{user_id}/role` - Update user role
- `GET /api/v1/admin/system/stats` - Get system statistics

## Database Schema

See `app/models/` for complete database schema.

## Development Guide

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` file
3. Create MySQL database
4. Run application: `uvicorn app.main:app --reload`

### Adding New Features
1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Create API routes in `app/api/`

## TODO Items

All files contain TODO comments for implementation. Search for `# TODO:` to find areas that need implementation.

