const express = require('express');
const cors = require('cors');
require('dotenv').config();

// 🚀 ADD THIS LINE HERE to force the database connection to initialize
require('./db/index'); 

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.use('/api/health', require('./routes/health'));
app.use('/api/voice', require('./routes/voice'));
app.use('/api/chat', require('./routes/chat'));

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