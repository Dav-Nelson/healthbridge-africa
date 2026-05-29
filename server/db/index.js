const { Pool } = require('pg');
require('dotenv').config();

// Immediate check to ensure your environment variables are actually loading
if (!process.env.DATABASE_URL) {
  console.error('❌ CRITICAL ERROR: DATABASE_URL is not defined in your .env file!');
  process.exit(1); 
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    // Neon requires SSL. rejectUnauthorized: false prevents local SSL handshake errors
    rejectUnauthorized: false,
  },
});

// Self-invoking function to handle the connection test cleanly without silent failures
(async () => {
  try {
    console.log('🔄 Attempting to connect to Neon PostgreSQL...');
    const res = await pool.query('SELECT NOW()');
    console.log('🚀 SUCCESS: Connected to Neon database at:', res.rows[0].now);
  } catch (err) {
    console.error('❌ DATABASE CONNECTION FAILED:');
    console.error(err.message);
    console.error(err.stack);
  }
})();

module.exports = pool;