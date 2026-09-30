const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const apiRoutes = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 5000;
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';

// 1. CORS Configuration restricted to frontend origin
app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (like mobile apps, curl, snapshot generator)
    if (!origin) return callback(null, true);
    if (origin === FRONTEND_URL || origin === 'http://localhost:3000' || origin === 'http://localhost:5173') {
      return callback(null, true);
    }
    return callback(new Error('Blocked by CORS policy'));
  },
  credentials: true
}));

// 2. Rate Limiting to protect database pool
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: parseInt(process.env.RATE_LIMIT_MAX || '200', 10),
  standardHeaders: true,
  legacyHeaders: false,
  message: { success: false, error: 'Too many requests. Please try again later.' }
});
app.use('/api', limiter);

// 3. Body parsing (JSON)
app.use(express.json());

// 4. API Endpoints
app.use('/api', apiRoutes);

// 5. Root route
app.get('/', (req, res) => {
  res.json({
    name: 'Flipkart Analytics Hub API',
    status: 'online',
    endpoints: '/api/overview, /api/revenue/monthly, /api/festival, etc.',
    health: '/api/health'
  });
});

// 6. 404 Handler
app.use((req, res) => {
  res.status(404).json({ success: false, error: 'Endpoint not found' });
});

// 7. Global Error Handler
app.use((err, req, res, next) => {
  console.error('Unhandled server error:', err.message);
  res.status(500).json({ success: false, error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Flipkart Analytics API server running on port ${PORT}`);
  console.log(`CORS allowed frontend: ${FRONTEND_URL}`);
});
