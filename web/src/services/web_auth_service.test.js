import axios from 'axios';
import authService, { api } from './web_auth_service';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('Web Auth Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    delete window.location;
    window.location = { href: '' };
  });

  describe('API Configuration', () => {
    test('creates axios instance with correct base URL', () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: '/api',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    test('uses environment API URL when available', () => {
      const originalEnv = process.env.REACT_APP_API_URL;
      process.env.REACT_APP_API_URL = 'https://api.example.com';
      
      // Re-import to get new config
      jest.resetModules();
      require('./web_auth_service');
      
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: 'https://api.example.com',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      process.env.REACT_APP_API_URL = originalEnv;
    });
  });

  describe('Request Interceptor', () => {
    test('adds auth token to requests when available', () => {
      localStorage.setItem('token', 'test-token');
      
      const mockConfig = {
        headers: {},
      };
      
      // Get the request interceptor
      const requestInterceptor = axios.create.mock.results[0].value.interceptors.request.use.mock.calls[0][0];
      
      const result = requestInterceptor(mockConfig);
      
      expect(result.headers.Authorization).toBe('Bearer test-token');
    });

    test('does not add auth header when no token', () => {
      const mockConfig = {
        headers: {},
      };
      
      const requestInterceptor = axios.create.mock.results[0].value.interceptors.request.use.mock.calls[0][0];
      
      const result = requestInterceptor(mockConfig);
      
      expect(result.headers.Authorization).toBeUndefined();
    });
  });

  describe('Response Interceptor', () => {
    test('passes through successful responses', () => {
      const mockResponse = { data: { message: 'success' } };
      
      const responseInterceptor = axios.create.mock.results[0].value.interceptors.response.use.mock.calls[0][0];
      
      const result = responseInterceptor(mockResponse);
      
      expect(result).toBe(mockResponse);
    });

    test('handles 401 errors by clearing token and redirecting', () => {
      localStorage.setItem('token', 'invalid-token');
      
      const mockError = {
        response: {
          status: 401,
        },
      };
      
      const errorInterceptor = axios.create.mock.results[0].value.interceptors.response.use.mock.calls[0][1];
      
      expect(() => errorInterceptor(mockError)).rejects.toEqual(mockError);
      expect(localStorage.getItem('token')).toBeNull();
      expect(window.location.href).toBe('/login');
    });

    test('passes through non-401 errors', () => {
      const mockError = {
        response: {
          status: 500,
        },
      };
      
      const errorInterceptor = axios.create.mock.results[0].value.interceptors.response.use.mock.calls[0][1];
      
      expect(() => errorInterceptor(mockError)).rejects.toEqual(mockError);
    });
  });

  describe('Login', () => {
    test('successful login returns success response', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          user: { id: 1, username: 'testuser' },
        },
      };
      
      const mockAxiosInstance = {
        post: jest.fn().mockResolvedValue(mockResponse),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      // Re-import to get new instance
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const credentials = { username: 'testuser', password: 'testpass' };
      const result = await authService.login(credentials);
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/login', credentials);
      expect(result).toEqual({
        success: true,
        data: mockResponse.data,
      });
    });

    test('failed login returns error response', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Invalid credentials',
          },
        },
      };
      
      const mockAxiosInstance = {
        post: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const credentials = { username: 'wrong', password: 'wrong' };
      const result = await authService.login(credentials);
      
      expect(result).toEqual({
        success: false,
        error: 'Invalid credentials',
      });
    });

    test('login handles network errors', async () => {
      const mockError = new Error('Network error');
      
      const mockAxiosInstance = {
        post: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const credentials = { username: 'testuser', password: 'testpass' };
      const result = await authService.login(credentials);
      
      expect(result).toEqual({
        success: false,
        error: 'Login failed',
      });
    });
  });

  describe('Get Current User', () => {
    test('successful request returns user data', async () => {
      const mockResponse = {
        data: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
        },
      };
      
      const mockAxiosInstance = {
        get: jest.fn().mockResolvedValue(mockResponse),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const result = await authService.getCurrentUser();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/auth/me');
      expect(result).toEqual({
        success: true,
        data: mockResponse.data,
      });
    });

    test('failed request returns error response', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Token expired',
          },
        },
      };
      
      const mockAxiosInstance = {
        get: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const result = await authService.getCurrentUser();
      
      expect(result).toEqual({
        success: false,
        error: 'Token expired',
      });
    });

    test('handles network errors', async () => {
      const mockError = new Error('Network error');
      
      const mockAxiosInstance = {
        get: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const result = await authService.getCurrentUser();
      
      expect(result).toEqual({
        success: false,
        error: 'Failed to get user info',
      });
    });
  });

  describe('Register', () => {
    test('successful registration returns success response', async () => {
      const mockResponse = {
        data: {
          id: 1,
          username: 'newuser',
          email: 'new@example.com',
        },
      };
      
      const mockAxiosInstance = {
        post: jest.fn().mockResolvedValue(mockResponse),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
      };
      
      const result = await authService.register(userData);
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/register', userData);
      expect(result).toEqual({
        success: true,
        data: mockResponse.data,
      });
    });

    test('failed registration returns error response', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Username already exists',
          },
        },
      };
      
      const mockAxiosInstance = {
        post: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const userData = {
        username: 'existinguser',
        email: 'existing@example.com',
        password: 'password123',
      };
      
      const result = await authService.register(userData);
      
      expect(result).toEqual({
        success: false,
        error: 'Username already exists',
      });
    });

    test('handles network errors', async () => {
      const mockError = new Error('Network error');
      
      const mockAxiosInstance = {
        post: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123',
      };
      
      const result = await authService.register(userData);
      
      expect(result).toEqual({
        success: false,
        error: 'Registration failed',
      });
    });
  });

  describe('Logout', () => {
    test('removes token from localStorage', () => {
      localStorage.setItem('token', 'test-token');
      
      authService.logout();
      
      expect(localStorage.getItem('token')).toBeNull();
    });
  });

  describe('Error Handling', () => {
    test('handles errors without response object', async () => {
      const mockError = new Error('Network error');
      
      const mockAxiosInstance = {
        post: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const result = await authService.login({ username: 'test', password: 'test' });
      
      expect(result).toEqual({
        success: false,
        error: 'Login failed',
      });
    });

    test('handles errors without detail in response', async () => {
      const mockError = {
        response: {
          data: {},
        },
      };
      
      const mockAxiosInstance = {
        post: jest.fn().mockRejectedValue(mockError),
      };
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance);
      
      jest.resetModules();
      const { default: authService } = require('./web_auth_service');
      
      const result = await authService.login({ username: 'test', password: 'test' });
      
      expect(result).toEqual({
        success: false,
        error: 'Login failed',
      });
    });
  });

  describe('API Export', () => {
    test('exports api instance', () => {
      const { api } = require('./web_auth_service');
      expect(api).toBeDefined();
    });
  });
}); 