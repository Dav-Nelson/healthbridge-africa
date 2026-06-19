const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

require('./db/index');

const app = express();
const PORT = process.env.PORT || 5000;

// Security headers
app.use(helmet());

// CORS — locked to your Vercel frontend only
const allowedOrigins = [
  'https://healthbridge-africa.vercel.app',
  'http://localhost:3000'
];

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (mobile apps, curl, health checks)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json({ limit: '1mb' }));

// Rate limiting — 60 requests per 15 minutes per IP
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 60,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests. Please wait a few minutes and try again.' }
});

// Stricter limit on AI endpoints — 20 requests per 15 minutes per IP
const aiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'AI request limit reached. Please wait a few minutes and try again.' }
});

app.use(limiter);

// Health checks
app.head('/health', (req, res) => res.status(200).end());
app.get('/health', (req, res) => res.status(200).json({ status: 'ok' }));

app.use('/api/health', require('./routes/health'));
app.use('/api/voice', aiLimiter, require('./routes/voice'));

app.get('/', (req, res) => {
  res.json({
    message: 'HealthBridge Africa API is running',
    version: '1.0.0',
    status: 'ok'
  });
});

app.listen(PORT, () => {
  console.log(`HealthBridge Africa server running on port ${PORT}`);
});

module.exports = app;