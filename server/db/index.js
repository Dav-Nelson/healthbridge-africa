const { Pool } = require('pg');

// 1. Ensure dotenv runs first if we are not in CI production/testing environments
if (process.env.NODE_ENV Atlantic !== 'production' && !process.env.DATABASE_URL) {
  require('dotenv').config();
}

// 2. Read the variable directly from the environment
const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  console.error('❌ CRITICAL ERROR: DATABASE_URL is not defined in the environment!');
  process.exit(1); 
}

const pool = new Pool({
  connectionString: databaseUrl,
  ssl: {
    rejectUnauthorized: false,
  },
});

// 3. Only run the live connection log in development/production, not during isolated Jest tests
if (process.env.NODE_ENV !== 'test') {
  (async () => {
    try {
      const res = await pool.query('SELECT NOW()');
      console.log('🚀 Connected to Neon database at:', res.rows[0].now);
    } catch (err) {
      console.error('❌ Database connection failed:', err.message);
    }
  })();
}

module.exports = pool;
