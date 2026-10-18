// Toda la configuración sale de variables de entorno (con valores por defecto para desarrollo).
const toList = (v) => (v || '').split(',').map((s) => s.trim()).filter(Boolean);

module.exports = {
  port: parseInt(process.env.PORT || '8080', 10),
  microserviceUrl: process.env.MICROSERVICE_URL || 'http://localhost:3000',
  jwtSecret: process.env.JWT_SECRET || 'cambia-este-secreto-en-produccion',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1h',
  adminUser: process.env.ADMIN_USER || 'admin',
  adminPassword: process.env.ADMIN_PASSWORD || 'herbario123',
  corsOrigins: toList(process.env.CORS_ORIGINS || '*'),
  rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10),
  rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX || '100', 10),
  loginRateLimitMax: parseInt(process.env.LOGIN_RATE_LIMIT_MAX || '10', 10),
};
