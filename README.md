# Stock Analysis System

An intelligent stock analysis and alert system powered by AI agents.

## Features

- Real-time stock monitoring
- Multi-dimensional analysis (Technical, Fundamental, Sentiment, Risk)
- Intelligent alert system
- Portfolio management
- Role-based access control (Investor, Advisor, Admin)

## Tech Stack

- **Backend**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd stock-analysis-system
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Create MySQL database
```bash
mysql -u root -p
CREATE DATABASE stock_analysis;
```

6. Run the application
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
stock-analysis-system/
├── app/
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API routes
│   ├── agents/          # AI agents
│   ├── services/        # Business logic
│   ├── repositories/    # Data access layer
│   ├── external/        # External API clients
│   ├── core/            # Core functionality
│   └── utils/           # Utility functions
```

## User Roles

1. **Individual Investor**: Track stocks, receive alerts, view reports
2. **Financial Advisor**: Manage client portfolios, generate reports
3. **System Administrator**: System monitoring, user management, model updates

## License

MIT





