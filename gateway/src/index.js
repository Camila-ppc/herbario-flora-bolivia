const express = require('express');
const jwt = require('jsonwebtoken');
const { createProxyMiddleware } = require('http-proxy-middleware');
const config = require('./config');
const mw = require('./middlewares');

const app = express();
app.set('trust proxy', 1);
app.disable('x-powered-by');

// --- Middlewares transversales (orden importa) ---
app.use(mw.requestId);
app.use(mw.logger);
app.use(mw.corsMiddleware);
app.use(mw.globalLimiter);

// --- Rutas propias del gateway ---
app.get('/health', (req, res) => res.json({ status: 'ok', service: 'gateway' }));

// Login simple (usuario administrador definido por variables de entorno).
// express.json() se aplica SOLO aquí: el resto del tráfico se reenvía intacto al microservicio.
app.post('/auth/login', mw.loginLimiter, express.json(), (req, res) => {
  const { username, password } = req.body || {};
  if (username !== config.adminUser || password !== config.adminPassword) {
    return res.status(401).json({ error: 'Unauthorized', message: 'Credenciales inválidas.' });
  }
  const token = jwt.sign({ sub: username, role: 'admin' }, config.jwtSecret, {
    expiresIn: config.jwtExpiresIn,
  });
  return res.json({ access_token: token, token_type: 'Bearer', expires_in: config.jwtExpiresIn });
});

// --- Autenticación para la API; Swagger (/docs) queda público ---
app.use('/api', mw.verifyJwt);

// --- Proxy inverso hacia el microservicio ---
app.use(
  createProxyMiddleware({
    target: config.microserviceUrl,
    changeOrigin: true,
    pathFilter: ['/api', '/docs'],
    on: {
      proxyReq: (proxyReq, req) => {
        proxyReq.setHeader('x-request-id', req.id);
        if (req.user) proxyReq.setHeader('x-user', req.user.sub);
      },
      error: (err, req, res) => {
        console.error(JSON.stringify({ level: 'error', requestId: req.id, message: err.message }));
        if (!res.headersSent) {
          res.writeHead(502, { 'Content-Type': 'application/json' });
        }
        res.end(JSON.stringify({ error: 'Bad Gateway', message: 'El microservicio no responde.' }));
      },
    },
  }),
);

// --- 404 y errores ---
app.use((req, res) =>
  res.status(404).json({ error: 'Not Found', message: `Ruta ${req.method} ${req.path} no existe.` }),
);
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  console.error(JSON.stringify({ level: 'error', requestId: req.id, message: err.message }));
  res.status(500).json({ error: 'Internal Server Error', message: 'Error inesperado en el gateway.' });
});

app.listen(config.port, '0.0.0.0', () => {
  console.log(
    JSON.stringify({ level: 'info', message: `Gateway escuchando en :${config.port} -> ${config.microserviceUrl}` }),
  );
});
