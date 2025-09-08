export interface Environment {
  production: boolean;
  apiUrl: string;
  apiVersion: string;
  enableMockData: boolean;
  enableLogging: boolean;
}

export const environment: Environment = {
  production: true,
  apiUrl: 'https://bio.tools',
  apiVersion: 'api',
  enableMockData: false,
  enableLogging: false
};
