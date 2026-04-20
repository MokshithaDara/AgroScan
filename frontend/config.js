// ======================================================
// AGROSCAN CONFIGURATION
// ======================================================

/**
 * API Base URL
 * Change this for production deployments
 */
window.API_BASE_URL =
  window.__AGROSCAN_CONFIG__?.apiBaseUrl ||
  window.API_BASE_URL ||
  "http://127.0.0.1:8000";
