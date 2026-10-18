const crypto = require('crypto');
const cors = require('cors');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const jwt = require('jsonwebtoken');
const config = require('./config');

/** 1) Trazabilidad: asigna (o respeta) un x-request-id por petición. */
function requestId(req, res, next) {
  req.id = req.headers['x-request-id'] || crypto.randomUUID();
  res.setHeader('x-request-id', req.id);
  next();
}

/** 2) Logging centralizado: una línea JSON por petición. */
morgan.token('id', (req) => req.id);
morgan.token('user', (req) => (req.user ? req.user.sub : '-'));
const logger = morgan((tokens, req, res) =>
  JSON.stringify({
    time: new Date().toISOString(),
    requestId: tokens.id(req, res),
    method: tokens.method(req, res),
    url: tokens.url(req, res),
    status: Number(tokens.status(req, res)),
    ms: Number(tokens['response-time'](req, res)),
    user: tokens.user(req, res),
    ip: req.ip,
  }),
);

/** 3) CORS configurable por variable de entorno (CORS_ORIGINS=a,b,c o *). */
const corsMiddleware = cors({
  origin: config.corsOrigins.includes('*') ? true : config.corsOrigins,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'x-request-id'],
  exposedHeaders: ['x-request-id'],
});

/** 4) Rate limiting: límite global por IP y uno más estricto para el login. */
const tooMany = (msg) => ({ error: 'Too Many Requests', message: msg });
const globalLimiter = rateLimit({
  windowMs: config.rateLimitWindowMs,
  limit: config.rateLimitMax,
  standardHeaders: true,
  legacyHeaders: false,
  message: tooMany('Demasiadas peticiones, intenta de nuevo en un momento.'),
});
const loginLimiter = rateLimit({
  windowMs: config.rateLimitWindowMs,
  limit: config.loginRateLimitMax,
  standardHeaders: true,
  legacyHeaders: false,
  message: tooMany('Demasiados intentos de login, intenta de nuevo en un momento.'),
});

/** 5) Validación de tokens JWT (Authorization: Bearer <token>). */
function verifyJwt(req, res, next) {
  const header = req.headers.authorization || '';
  const [scheme, token] = header.split(' ');
  if (scheme !== 'Bearer' || !token) {
    return res.status(401).json({ error: 'Unauthorized', message: 'Falta el token Bearer.' });
  }
  try {
    req.user = jwt.verify(token, config.jwtSecret);
    return next();
  } catch (err) {
    const message = err.name === 'TokenExpiredError' ? 'El token expiró.' : 'Token inválido.';
    return res.status(401).json({ error: 'Unauthorized', message });
  }
}

module.exports = { requestId, logger, corsMiddleware, globalLimiter, loginLimiter, verifyJwt };
