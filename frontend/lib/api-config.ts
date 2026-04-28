export const getApiUrl = (): string => {
  // Server-side rendering
  if (typeof window === 'undefined') {
    return 'https://applicants-api-service-djekhgdgfbd8dee4.centralus-01.azurewebsites.net/api';
  }

  // Local development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5000/api';
  }

  // Production (Azure Static Web Apps or any other deployed domain)
  return 'https://applicants-api-service-djekhgdgfbd8dee4.centralus-01.azurewebsites.net/api';
};