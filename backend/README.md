# WealthWise Backend API

A comprehensive FastAPI backend for personal portfolio management with automated price tracking, net worth calculations, and data export capabilities.

## Features

- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Portfolio Management**: Create and manage multiple investment portfolios
- **Asset Tracking**: Support for stocks, cryptocurrencies, and other asset types
- **Automated Price Updates**: Daily scheduled tasks to fetch current market prices
- **Net Worth Calculation**: Real-time and historical net worth tracking
- **Data Security**: AES-256 encryption for sensitive financial data
- **Data Export**: CSV and JSON export functionality
- **API Integration**: Alpha Vantage (stocks) and CoinGecko (crypto) price feeds

## Project Structure

```
backend/
├── models/              # Database models
│   ├── __init__.py
│   └── models.py
├── schemas/             # Pydantic schemas
│   ├── __init__.py
│   └── schemas.py
├── routers/             # API route handlers
│   ├── __init__.py
│   ├── auth.py
│   ├── portfolios.py
│   ├── networth.py
│   └── export.py
├── services/            # Business logic services
│   ├── __init__.py
│   ├── price_service.py
│   └── portfolio_service.py
├── scheduler/           # Scheduled tasks
│   ├── __init__.py
│   └── scheduler_service.py
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── auth.py
│   └── encryption.py
├── tests/               # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_portfolios.py
├── alembic/             # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── main.py              # FastAPI application
├── config.py            # Application settings
├── database.py          # Database configuration
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
├── docker-compose.yml   # Docker services
├── alembic.ini         # Migration configuration
└── .env.example        # Environment variables template
```

## Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT with bcrypt
- **Encryption**: AES-256 for sensitive data
- **Scheduling**: APScheduler for automated tasks
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL
- Docker & Docker Compose (optional)

### Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL=postgresql://wealthwise:password@localhost:5432/wealthwise
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
   AES_ENCRYPTION_KEY=your-32-byte-base64-encoded-encryption-key
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
   COINGECKO_API_KEY=your-coingecko-api-key
   VITE_API_BASE_URL=http://localhost:3000
   ```

3. **Generate encryption key**
   ```python
   import base64
   import os
   key = base64.b64encode(os.urandom(32)).decode()
   print(f"AES_ENCRYPTION_KEY={key}")
   ```

### Running with Docker (Recommended)

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **The API will be available at**: `http://localhost:8000`

3. **API Documentation**: `http://localhost:8000/docs`

### Running Locally

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**
   ```bash
   createdb wealthwise
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - User login

### Portfolios
- `GET /portfolios/` - Get user portfolios
- `POST /portfolios/` - Create new portfolio
- `GET /portfolios/{id}` - Get specific portfolio
- `PUT /portfolios/{id}` - Update portfolio
- `DELETE /portfolios/{id}` - Delete portfolio

### Assets
- `POST /portfolios/{id}/assets` - Add asset to portfolio
- `GET /portfolios/{id}/assets` - Get portfolio assets

### Net Worth
- `GET /networth/current` - Get current net worth
- `GET /networth/history` - Get net worth history

### Export
- `GET /export/csv` - Export data as CSV
- `GET /export/json` - Export data as JSON

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1
```

## Testing

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run with coverage
```bash
pytest --cov=. tests/
```

## Scheduler

The application includes an automated scheduler that runs daily at 02:00 to:

1. **Fetch Current Prices**: Updates stock prices from Alpha Vantage and crypto prices from CoinGecko
2. **Calculate Valuations**: Computes current portfolio values
3. **Store Snapshots**: Saves net worth snapshots for historical tracking

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Secure token-based auth
- **AES-256 Encryption**: Purchase prices encrypted at rest
- **CORS Protection**: Configured for frontend integration
- **Input Validation**: Pydantic schemas for all endpoints

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `AES_ENCRYPTION_KEY` | Base64 encoded 32-byte key | Yes |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Yes |
| `COINGECKO_API_KEY` | CoinGecko API key | No |
| `VITE_API_BASE_URL` | Frontend URL for CORS | Yes |

## Development

### Adding New Features

1. **Create new models** in `models/models.py`
2. **Generate migration**: `alembic revision --autogenerate -m "Add new feature"`
3. **Create schemas** in `schemas/schemas.py`
4. **Implement service logic** in `services/`
5. **Add API routes** in `routers/`
6. **Write tests** in `tests/`

## API Keys Setup

### Alpha Vantage (Stock Prices)
1. Sign up at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Get your free API key
3. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

### CoinGecko (Crypto Prices)
1. Sign up at [CoinGecko](https://www.coingecko.com/en/api)
2. Get your API key (optional for basic usage)
3. Add to `.env`: `COINGECKO_API_KEY=your_key_here`

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in `.env`
   - Ensure database exists

2. **Migration Errors**
   - Check database permissions
   - Verify alembic configuration
   - Run `alembic current` to check status

3. **API Key Issues**
   - Verify API keys are valid
   - Check rate limits
   - Ensure proper environment variable names

4. **Scheduler Not Running**
   - Check logs for errors
   - Verify timezone settings
   - Ensure database connectivity

## License

This project is licensed under the MIT License.
