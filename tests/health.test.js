const request = require('supertest');
const app = require('../server/index');

describe('HealthBridge Africa API', () => {
  test('GET / returns status ok', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  test('GET /api/health returns ok', async () => {
    const res = await request(app).get('/api/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  test('POST /api/chat without query returns 400', async () => {
    const res = await request(app)
      .post('/api/chat')
      .send({});
    expect(res.statusCode).toBe(400);
  });

  test('POST /api/chat with query returns 200', async () => {
    const res = await request(app)
      .post('/api/chat')
      .send({ query: 'What are symptoms of malaria?', language: 'english' });
    expect(res.statusCode).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.response).toBeDefined();
  }, 30000);

  test('POST /api/voice/transcribe without file returns 400', async () => {
    const res = await request(app)
      .post('/api/voice/transcribe')
      .send({});
    expect(res.statusCode).toBe(400);
  });
});