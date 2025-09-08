export interface Environment {
  production: boolean;
  apiUrl: string;
  apiVersion: string;
  enableMockData: boolean;
  enableLogging: boolean;
}

export const environment: Environment = {
  production: false,
  apiUrl: 'http://localhost:8000', // Adjust to your Django backend URL
  apiVersion: 'api/v1',
  enableMockData: true, // Set to true to use mock data during development
  enableLogging: true
};

export const environmentProd: Environment = {
  production: true,
  apiUrl: 'https://bio.tools', // Production API URL
  apiVersion: 'api',
  enableMockData: false,
  enableLogging: false
};
