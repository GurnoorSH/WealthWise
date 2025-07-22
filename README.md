# 💰 WealthWise - Personal Portfolio Management System

**WealthWise** is a comprehensive full-stack application for managing your investment portfolio, tracking asset performance, and monitoring your net worth over time. Built with modern technologies, it provides real-time price updates, secure data handling, and detailed analytics.

## 🌟 What is WealthWise?

WealthWise helps you:
- **Track Investments**: Monitor stocks, cryptocurrencies, and other assets
- **Calculate Net Worth**: See your total portfolio value in real-time
- **Analyze Performance**: View historical data and growth trends
- **Export Data**: Download your portfolio information as CSV or JSON
- **Stay Updated**: Automatic daily price updates from market APIs

---

## 🏗️ System Architecture

WealthWise consists of two main parts that work together:

### **Frontend (User Interface)**
- **Technology**: React + Vite (JavaScript framework)
- **Purpose**: The website you interact with
- **Location**: `WealthWise/` folder
- **What it does**: Provides forms, charts, and displays for managing your portfolio

### **Backend (Server & Database)**
- **Technology**: FastAPI (Python framework) + PostgreSQL database
- **Purpose**: Handles data storage, calculations, and external API calls
- **Location**: Would be in a separate backend structure
- **What it does**: Stores your data securely, fetches current prices, calculates net worth

---

## 🎯 Key Features Explained

### 1. **User Authentication & Security**
- **Sign Up/Login**: Create secure accounts with email and password
- **Password Protection**: Uses bcrypt hashing (military-grade security)
- **JWT Tokens**: Secure session management
- **Data Encryption**: Purchase prices encrypted with AES-256

### 2. **Portfolio Management**
- **Multiple Portfolios**: Create separate portfolios (e.g., "Retirement", "Trading")
- **Asset Tracking**: Add stocks, crypto, bonds, and other investments
- **Purchase History**: Record when and at what price you bought assets
- **Real-time Valuation**: See current value vs. purchase price

### 3. **Automated Price Updates**
- **Daily Schedule**: Runs automatically at 2:00 AM every day
- **Stock Prices**: Fetches from Alpha Vantage API
- **Crypto Prices**: Fetches from CoinGecko API
- **Historical Data**: Stores price history for trend analysis

### 4. **Net Worth Calculation**
- **Real-time Calculation**: Current portfolio value based on latest prices
- **Historical Tracking**: See how your wealth has grown over time
- **Portfolio Breakdown**: Detailed view of each portfolio's contribution
- **Gain/Loss Analysis**: Track performance vs. purchase prices

### 5. **Data Export**
- **CSV Export**: Spreadsheet-compatible format for Excel/Google Sheets
- **JSON Export**: Structured data format for developers
- **Complete Data**: Includes all portfolios, assets, and performance metrics

---

## 🔧 Technical Implementation

### **Frontend Architecture**
```
WealthWise/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Different screens (Dashboard, Portfolio, etc.)
│   ├── services/      # API communication with backend
│   ├── utils/         # Helper functions
│   └── App.jsx        # Main application component
├── public/            # Static files (images, icons)
└── package.json       # Dependencies and scripts
```

### **Backend Architecture** (Planned Structure)
```
backend/
├── models/            # Database table definitions
├── routers/           # API endpoints (/login, /portfolios, etc.)
├── services/          # Business logic (price fetching, calculations)
├── utils/             # Security and encryption utilities
├── scheduler/         # Automated tasks (daily price updates)
└── main.py           # FastAPI application entry point
```

### **Database Design**
- **Users Table**: Account information (email, password hash)
- **Portfolios Table**: Portfolio names and descriptions
- **Assets Table**: Individual investments with encrypted purchase prices
- **Price Snapshots Table**: Historical price data from APIs
- **Net Worth Snapshots Table**: Daily portfolio valuations

---

## 🚀 How Everything Works Together

### **User Journey Example:**

1. **Sign Up**: User creates account → Backend stores encrypted password
2. **Create Portfolio**: User adds "My Stocks" portfolio → Stored in database
3. **Add Assets**: User adds "100 shares of AAPL at $150" → Purchase price encrypted and stored
4. **Daily Updates**: At 2 AM, scheduler fetches current AAPL price ($160) → Stored in price snapshots
5. **View Dashboard**: User sees portfolio worth $16,000 (100 × $160) with $1,000 gain
6. **Export Data**: User downloads CSV with all portfolio details

### **Data Flow:**
```
Frontend (React) ↔ API Calls ↔ Backend (FastAPI) ↔ Database (PostgreSQL)
                                      ↕
                              External APIs (Alpha Vantage, CoinGecko)
```

---

## 🛠️ Setup Instructions

### **Prerequisites**
- Node.js (for frontend)
- Python 3.10+ (for backend)
- PostgreSQL database
- API keys from Alpha Vantage and CoinGecko

### **Frontend Setup**
```bash
# Navigate to frontend folder
cd WealthWise

# Install dependencies
npm install

# Start development server
npm run dev

# Access at: http://localhost:3000
```

### **Backend Setup** (When implemented)
```bash
# Navigate to backend folder
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL and API keys

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload

# Access at: http://localhost:8000
```

### **Environment Variables Needed**
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/wealthwise

# Security
JWT_SECRET_KEY=your-secret-key
AES_ENCRYPTION_KEY=your-encryption-key

# API Keys
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
COINGECKO_API_KEY=your-coingecko-key

# Frontend URL
VITE_API_BASE_URL=http://localhost:3000
```

---

## 🔐 Security Features

### **Data Protection**
- **Encrypted Storage**: Purchase prices encrypted with AES-256
- **Secure Authentication**: JWT tokens with expiration
- **Password Hashing**: bcrypt with salt for password storage
- **CORS Protection**: Prevents unauthorized cross-origin requests

### **Privacy**
- **User Isolation**: Each user can only access their own data
- **API Rate Limiting**: Prevents abuse of external APIs
- **Input Validation**: All data validated before storage

---

## 📊 API Endpoints

### **Authentication**
- `POST /auth/signup` - Create new account
- `POST /auth/login` - User login

### **Portfolio Management**
- `GET /portfolios/` - Get all user portfolios
- `POST /portfolios/` - Create new portfolio
- `GET /portfolios/{id}` - Get specific portfolio
- `PUT /portfolios/{id}` - Update portfolio
- `DELETE /portfolios/{id}` - Delete portfolio

### **Asset Management**
- `POST /portfolios/{id}/assets` - Add asset to portfolio
- `GET /portfolios/{id}/assets` - Get portfolio assets

### **Net Worth Tracking**
- `GET /networth/current` - Current net worth
- `GET /networth/history` - Historical net worth data

### **Data Export**
- `GET /export/csv` - Download CSV file
- `GET /export/json` - Download JSON file

---

## 🤖 Automated Features

### **Daily Price Updates (2:00 AM)**
1. **Fetch Prices**: Gets latest prices for all tracked assets
2. **Calculate Values**: Computes current portfolio values
3. **Store Snapshots**: Saves net worth history
4. **Error Handling**: Logs any API failures for manual review

### **Supported Assets**
- **Stocks**: Any symbol on major exchanges (AAPL, GOOGL, TSLA, etc.)
- **Cryptocurrencies**: Bitcoin, Ethereum, and 100+ other coins
- **Future**: Bonds, ETFs, and other asset types

---

## 🎨 User Interface Features

### **Dashboard**
- Portfolio overview with current values
- Gain/loss indicators with color coding
- Charts showing portfolio performance over time
- Quick access to add new assets

### **Portfolio Management**
- Create and organize multiple portfolios
- Drag-and-drop asset organization
- Bulk import from CSV files
- Portfolio comparison tools

### **Asset Details**
- Individual asset performance tracking
- Price history charts
- Buy/sell transaction history
- Performance metrics (ROI, volatility)

### **Reports & Analytics**
- Net worth growth over time
- Asset allocation pie charts
- Performance comparison between portfolios
- Tax reporting assistance

---

## 🔄 Integration Details

### **Frontend ↔ Backend Communication**
- **HTTP Requests**: RESTful API calls using Axios
- **Authentication**: JWT tokens in request headers
- **Error Handling**: User-friendly error messages
- **Loading States**: Progress indicators during API calls

### **External API Integration**
- **Alpha Vantage**: Stock prices with 5 requests/minute limit
- **CoinGecko**: Crypto prices with higher rate limits
- **Fallback Handling**: Graceful degradation if APIs are down
- **Caching**: Reduces API calls by storing recent prices

---

## 🚦 Getting Started (Beginner Guide)

### **Step 1: Understanding the Project**
- This is a web application for tracking investments
- You'll have a website (frontend) and a server (backend)
- The server talks to external APIs to get current prices

### **Step 2: What You Need**
- A computer with internet connection
- Basic knowledge of using command line/terminal
- API keys (free to get from Alpha Vantage and CoinGecko)

### **Step 3: First Time Setup**
1. Download/clone this project
2. Get API keys from Alpha Vantage and CoinGecko
3. Install Node.js and Python on your computer
4. Follow the setup instructions above

### **Step 4: Using the Application**
1. Open the website in your browser
2. Create an account
3. Add a portfolio (e.g., "My Investments")
4. Add some assets (stocks/crypto you own)
5. Wait for daily updates or manually refresh prices
6. View your net worth and performance

---

## 🛟 Troubleshooting

### **Common Issues**

**Frontend won't start:**
- Check if Node.js is installed: `node --version`
- Install dependencies: `npm install`
- Check for port conflicts (3000 already in use)

**Backend connection errors:**
- Verify database is running
- Check environment variables in `.env`
- Ensure API keys are valid

**Price updates not working:**
- Check API key limits (Alpha Vantage: 5 calls/minute)
- Verify internet connection
- Check server logs for error messages

**Authentication issues:**
- Clear browser cookies/localStorage
- Check JWT token expiration
- Verify password requirements

---

## 📈 Future Enhancements

### **Planned Features**
- Mobile app (React Native)
- Advanced charting and analytics
- Social features (share portfolios)
- Integration with brokers (automatic import)
- Tax optimization suggestions
- Alerts and notifications

### **Technical Improvements**
- Real-time WebSocket updates
- Advanced caching strategies
- Machine learning price predictions
- Multi-currency support
- Backup and sync features

---

## 🤝 Contributing

### **How to Contribute**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### **Development Guidelines**
- Follow existing code style
- Write clear commit messages
- Add documentation for new features
- Test thoroughly before submitting

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

### **Getting Help**
- Check this README first
- Look at existing issues on GitHub
- Create a new issue with detailed description
- Include error messages and steps to reproduce

### **Contact**
- GitHub Issues: For bugs and feature requests
- Email: For security concerns
- Documentation: Check inline code comments

---

## 🎉 Conclusion

WealthWise is designed to be your comprehensive investment tracking solution. Whether you're a beginner investor or an experienced trader, it provides the tools you need to monitor and analyze your portfolio performance.

The combination of automated price updates, secure data handling, and intuitive user interface makes it easy to stay on top of your investments and make informed financial decisions.

**Happy Investing! 💰📈**
