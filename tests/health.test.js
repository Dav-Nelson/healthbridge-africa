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

  test('POST /api/voice/text-chat without message returns 400', async () => {
    const res = await request(app)
      .post('/api/voice/text-chat')
      .send({ sessionId: 'test-session' });
    expect(res.statusCode).toBe(400);
  });

  test('POST /api/voice/text-chat without sessionId returns 400', async () => {
    const res = await request(app)
      .post('/api/voice/text-chat')
      .send({ message: 'What are symptoms of malaria?', language: 'en' });
    expect(res.statusCode).toBe(400);
  });

  test('POST /api/voice/chat without audio file returns 400', async () => {
    const res = await request(app)
      .post('/api/voice/chat')
      .send({});
    expect(res.statusCode).toBe(400);
  });

  test('POST /api/voice/speak without text returns error', async () => {
    const res = await request(app)
      .post('/api/voice/speak')
      .send({ language: 'en' });
    expect(res.statusCode).toBeGreaterThanOrEqual(400);
  });
});