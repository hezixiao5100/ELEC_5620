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
- **AI**: OpenAI GPT models
- **Task Queue**: Celery
- **Background Tasks**: Celery Beat

## Installation

1. Clone the repository
```bash
git clone https://github.com/hezixiao5100/ELEC_5620.git
cd ELEC_5620
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
ELEC_5620/
├── app/
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API routes
│   ├── agents/          # AI agents
│   │   ├── emotional_analysis_agent.py
│   │   ├── data_collection_agent.py
│   │   ├── risk_analysis_agent.py
│   │   └── report_generate_agent.py
│   ├── services/        # Business logic
│   ├── repositories/    # Data access layer
│   ├── external/        # External API clients
│   ├── core/            # Core functionality
│   └── utils/           # Utility functions
├── docs/                # Documentation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## AI Agents

### Emotional Analysis Agent
- Analyzes market sentiment from news articles
- Calculates Fear & Greed Index
- Generates emotional trading signals

### Data Collection Agent
- Collects real-time stock data
- Fetches relevant news articles
- Manages historical data storage

### Risk Analysis Agent
- Calculates volatility metrics
- Assesses investment risk levels
- Provides risk recommendations

### Report Generation Agent
- Creates comprehensive analysis reports
- Generates executive summaries
- Formats data for visualization

## User Roles

1. **Individual Investor**: Track stocks, receive alerts, view reports
2. **Financial Advisor**: Manage client portfolios, generate reports
3. **System Administrator**: System monitoring, user management, model updates

## Environment Variables

Create a `.env` file with the following variables:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/stock_analysis
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
NEWS_API_KEY=your-news-api-key
```

## Running Background Tasks

Start Celery worker for background tasks:
```bash
celery -A app.celery_app worker --loglevel=info
```

Start Celery beat for scheduled tasks:
```bash
celery -A app.celery_app beat --loglevel=info
```

## License

MIT