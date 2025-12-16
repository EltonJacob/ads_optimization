# Amazon PPC Optimization Tool

An intelligent Amazon PPC optimization tool that fetches campaign data from the Amazon Ads API, analyzes keyword performance using AI, and provides actionable bid adjustments and optimization recommendations through a web-based interface.

## Features

- **Dual Data Ingestion**: Fetch data via Amazon Ads API or upload spreadsheets as a fallback
- **AI-Powered Analysis**: Intelligent bid optimization and keyword management recommendations
- **Performance Dashboard**: Visualize campaign metrics, trends, and keyword performance
- **Automated Recommendations**: Get data-driven suggestions for bid adjustments, keyword pausing/enabling, and negative keywords
- **Decision Tracking**: Complete audit trail of all optimization actions
- **ROI Optimization**: Strategic insights to maximize ROAS and minimize wasted spend

## Architecture

### Backend Stack
- **Python 3.13**
- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL/SQLite** - Database
- **Alembic** - Database migrations
- **Amazon Ads API SDK** - Data retrieval
- **OpenAI/Anthropic Claude** - AI-powered analysis

### Frontend Stack
- **Next.js 14+** with React
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Recharts/Chart.js** - Data visualization
- **Axios** - HTTP client

## Project Structure

```
Amazon PPC/
├── agent/
│   ├── ui/
│   │   ├── api.py              # Main FastAPI application
│   │   ├── models.py           # Pydantic request/response models
│   │   └── config.py           # Configuration management
│   ├── jobs/
│   │   ├── fetch_reports.py    # Amazon API data fetching
│   │   └── import_spreadsheet.py # Spreadsheet import logic
│   ├── ai/
│   │   ├── client.py           # AI service wrapper
│   │   ├── prompts.py          # Prompt templates
│   │   └── analyzers/
│   │       ├── bid_optimizer.py
│   │       ├── keyword_optimizer.py
│   │       └── strategy_optimizer.py
│   └── database/
│       ├── models.py           # SQLAlchemy database models
│       └── migrations/         # Alembic migrations
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js app directory
│   │   ├── components/        # React components
│   │   ├── lib/              # Utilities and API client
│   │   └── styles/           # Global styles
│   └── public/               # Static assets
├── data/
│   ├── uploads/              # Uploaded spreadsheet files
│   └── reports/              # Downloaded Amazon API reports
├── logs/                     # Application logs
├── .env                      # Environment variables (not in repo)
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download Node.js](https://nodejs.org/)
- **PostgreSQL** (recommended) or SQLite - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads)

### API Keys Required

1. **Amazon Ads API Access**
   - Client ID
   - Client Secret
   - Refresh Token
   - [Amazon Ads API Getting Started Guide](https://advertising.amazon.com/API/docs/en-us/get-started/overview)

2. **AI Provider** (choose one)
   - OpenAI API Key - [Get API Key](https://platform.openai.com/api-keys)
   - Anthropic Claude API Key - [Get API Key](https://console.anthropic.com/)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Amazon PPC"
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

A `.env` file has been created with default values. **You must update it with your actual credentials.**

**Quick Setup:**

1. Open the `.env` file in the project root
2. Add your Amazon Ads API credentials
3. Add your AI provider API key (OpenAI or Anthropic)
4. Optionally adjust optimization parameters

**For detailed configuration instructions, see:** [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md)

**Minimum required settings:**

```bash
# Amazon Ads API (REQUIRED)
AMAZON_ADS_CLIENT_ID=your_client_id_here
AMAZON_ADS_CLIENT_SECRET=your_client_secret_here
AMAZON_ADS_REFRESH_TOKEN=your_refresh_token_here

# AI Provider (REQUIRED - choose one)
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here
AI_PROVIDER=openai  # or anthropic

# Database (default SQLite works out of the box)
DATABASE_URL=sqlite:///amazon_ppc.db
```

#### Initialize Database

Run database migrations:

```bash
# Navigate to the project directory
cd agent

# Run Alembic migrations
alembic upgrade head
```

If Alembic is not yet configured, initialize it first:

```bash
alembic init alembic
# Then configure alembic.ini and create migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 3. Frontend Setup

#### Install Node.js Dependencies

```bash
cd frontend
npm install
```

#### Configure Frontend Environment

Create a `.env.local` file in the `frontend` directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Start the Backend Server

From the project root:

```bash
# Using uvicorn directly
uvicorn agent.ui.api:app --reload --host 0.0.0.0 --port 8000

# Or if you have a startup script
python -m agent.ui.api
```

The backend API will be available at: `http://localhost:8000`

API documentation (Swagger UI) will be available at: `http://localhost:8000/docs`

### Start the Frontend Development Server

In a new terminal, from the `frontend` directory:

```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### Verify Installation

1. Open your browser and navigate to `http://localhost:3000`
2. Check the API health endpoint: `http://localhost:8000/api/health`
3. Access the API documentation: `http://localhost:8000/docs`

## Usage Guide

### 1. Import Data

**Option A: Fetch from Amazon Ads API**
1. Navigate to the "Data Import" page
2. Select your Amazon Ads profile
3. Choose a date range (preset or custom)
4. Click "Fetch from Amazon API"
5. Monitor the progress indicator

**Option B: Upload Spreadsheet (Fallback)**
1. Navigate to the "Data Import" page
2. Drag and drop your CSV/Excel file
3. Preview the data to ensure correct formatting
4. Click "Import Data"
5. Review the import summary

Required columns for spreadsheet:
- Campaign Name
- Ad Group Name
- Keyword
- Match Type
- Bid
- Impressions
- Clicks
- Spend
- Sales
- Orders
- Date

### 2. View Campaign Performance

1. Navigate to the "Campaigns" page
2. Select your profile and date range
3. View key metrics cards (Spend, Sales, ACOS, ROAS)
4. Explore the performance trends chart
5. Review keyword-level performance in the table
6. Filter by match type, state, or campaign
7. Export data as needed

### 3. Generate AI Recommendations

1. Navigate to the "Recommendations" page
2. Select your profile and analysis date range
3. Click "Generate Recommendations"
4. Wait for AI analysis to complete (typically 10-30 seconds)
5. Review recommendations by category:
   - **Bid Adjustments**: Increase/decrease bids for optimal ACOS
   - **Keywords to Pause**: Stop wasting spend on underperformers
   - **Keywords to Enable**: Reactivate promising paused keywords
   - **Negative Keywords**: Add to prevent irrelevant clicks
   - **Strategic Insights**: High-level optimization opportunities

### 4. Apply Recommendations

1. Review each recommendation's reasoning and confidence score
2. Modify recommendations if needed
3. Select individual recommendations or bulk select
4. Click "Apply Selected" or "Apply All"
5. Confirm the action in the modal
6. Changes will be applied to the database and synced to Amazon Ads API

### 5. Track Decision History

1. Navigate to the "History" page
2. View all applied optimizations
3. Filter by date range, action type, or campaign
4. Export decision history for reporting
5. (Optional) Revert recent changes if needed

## Configuration

### Optimization Parameters

You can customize optimization thresholds by editing the configuration:

```python
# agent/ai/config.py

OPTIMIZATION_CONFIG = {
    "target_acos": 30.0,  # Target ACOS percentage
    "min_impressions_for_pause": 5000,  # Minimum impressions before pausing
    "high_acos_multiplier": 2.0,  # Pause if ACOS > target * this value
    "low_ctr_threshold": 0.002,  # 0.2% CTR threshold
    "max_bid_increase": 0.20,  # Maximum 20% bid increase
    "max_bid_decrease": 0.30,  # Maximum 30% bid decrease
    "min_bid": 0.02,  # Minimum bid amount
    "max_bid": 10.00,  # Maximum bid amount
}
```

### AI Model Selection

In your `.env` file, choose your AI provider:

```bash
# For OpenAI GPT-4
AI_PROVIDER=openai
AI_MODEL=gpt-4-turbo-preview

# For Anthropic Claude
AI_PROVIDER=anthropic
AI_MODEL=claude-3-opus-20240229
```

## Troubleshooting

### Backend Issues

**Problem**: Database connection errors
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Test connection
psql -U username -d amazon_ppc -h localhost
```

**Problem**: Amazon API timeouts
- Use the spreadsheet upload fallback
- Reduce date range (fetch in smaller chunks)
- Check Amazon API status and rate limits

**Problem**: Import errors
```bash
# Check logs
tail -f logs/app.log

# Verify Python dependencies
pip list | grep fastapi
```

### Frontend Issues

**Problem**: Cannot connect to backend
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check CORS configuration in `agent/ui/api.py`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**Problem**: Build errors
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

### Common Issues

**API Rate Limiting**: Amazon Ads API has rate limits. If you encounter 429 errors, wait and retry later.

**Memory Issues with Large Datasets**: For campaigns with 10,000+ keywords, consider:
- Implementing pagination
- Adding database indexes
- Increasing server resources

**File Upload Limits**: Default max file size is 100MB. Adjust in `agent/ui/api.py`:
```python
app.add_middleware(
    TrustedHostMiddleware,
    max_upload_size=200 * 1024 * 1024  # 200MB
)
```

## Testing

### Run Backend Tests

```bash
# Install testing dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# With coverage
pytest --cov=agent tests/
```

### Run Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e
```

## Deployment

### Docker Deployment

Build and run with Docker Compose:

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

For production deployment:

1. **Backend**: Deploy to AWS, DigitalOcean, or similar
   - Use Gunicorn with Uvicorn workers
   - Set up SSL/TLS certificates
   - Configure environment variables securely
   - Enable production logging and monitoring

2. **Frontend**: Deploy to Vercel, Netlify, or similar
   - Configure production API URL
   - Enable caching and CDN
   - Set up custom domain

3. **Database**: Use managed PostgreSQL
   - Regular backups
   - Connection pooling
   - Read replicas for scaling

See [project_plan.txt](project_plan.txt) Phase 5 for detailed deployment steps.

## Performance Optimization

- **Database Indexing**: Ensure indexes on frequently queried columns (keyword_id, date, profile_id)
- **Caching**: Implement Redis caching for frequently accessed data
- **Pagination**: Use pagination for large keyword lists (50-100 per page)
- **Async Processing**: Use background jobs for long-running AI analysis

## Security Best Practices

- Never commit `.env` files to version control
- Rotate API keys regularly
- Implement rate limiting on API endpoints
- Validate and sanitize all file uploads
- Use HTTPS in production
- Implement proper authentication and authorization
- Regular security audits

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -m "Add your feature"`
3. Push to the branch: `git push origin feature/your-feature`
4. Submit a pull request

## License

[Add your license information here]

## Support

For questions, issues, or feature requests:
- Review detailed plan: [project_plan.txt](project_plan.txt)
- Check application logs: `/logs` directory
- API documentation: `http://localhost:8000/docs` (when running)

## Roadmap

See [project_plan.txt](project_plan.txt) for detailed implementation phases and future enhancements including:
- Automated scheduling and auto-apply
- A/B testing framework
- Custom rules engine
- Mobile app
- Multi-user support
- Advanced forecasting with ML

---

**Current Status**: Phase 1.4 Complete - Performance Query Endpoints implemented

**Next Steps**: Phase 2 - Web UI Foundation (Frontend Development)

**Recent Updates:**
- ✅ Phase 1.4: Performance summary endpoint
- ✅ Phase 1.4: Keywords list endpoint with pagination & sorting
- ✅ Phase 1.4: Trends endpoint with daily/weekly/monthly grouping
- ✅ Phase 1.4: Data sources endpoint
- ✅ All performance query tests passing
- ✅ **Phase 1 Backend API Foundation: 100% COMPLETE**

Last Updated: 2025-12-16
