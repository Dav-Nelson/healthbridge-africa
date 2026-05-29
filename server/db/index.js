const { Pool } = require('pg');

// 🚀 FIXED: Removed the stray typo word
if (process.env.NODE_ENV !== 'production' && !process.env.DATABASE_URL) {
  require('dotenv').config();
}

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