import express from 'express';
import client from 'prom-client';

const app = express();
const register = client.register;

// Thu thập metrics Node.js
client.collectDefaultMetrics({ register });

// Route trang web
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

// Route /metrics cho Prometheus
app.get('/metrics', async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
});

// Chạy server
app.listen(80, () => console.log('Web frontend running on port 80'));
