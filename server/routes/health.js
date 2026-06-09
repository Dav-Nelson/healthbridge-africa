const express = require('express');
const router = express.Router();

// Support both HEAD and GET methods for health checks
const handleHealthCheck = (req, res) => {
  res.status(200).json({ status: 'ok', message: 'HealthBridge Africa is live' });
};

router.get('/', handleHealthCheck);
router.head('/', handleHealthCheck);

module.exports = router;