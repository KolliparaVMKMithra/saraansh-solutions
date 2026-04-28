/**
 * API Configuration
 * Dynamically determines the API URL based on the environment
 */

export const getApiUrl = (): string => {
  // Only run in browser
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_BASE_URL || 'https://applicants-api-service.azurewebsites.net/api';
  }

  // Production Azure deployment
  if (window.location.hostname === 'yellow-hill-06120a607.azurestaticapps.net') {
    return 'https://applicants-api-service.azurewebsites.net/api';
  }

  // Local development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5000/api';
  }

  // Fallback to environment variable or default to Azure backend
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'https://applicants-api-service.azurewebsites.net/api';
};
