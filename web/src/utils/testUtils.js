import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';

// Test utilities for React components
export const TestWrapper = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

export const renderWithRouter = (ui, options = {}) => {
  return render(ui, { wrapper: TestWrapper, ...options });
};

// Mock data for tests
export const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  created_at: '2023-01-01T00:00:00Z',
};

export const mockResponse = {
  id: 1,
  ocr_text: 'This is extracted text from the image',
  ai_analysis: 'This is the AI analysis of the content',
  created_at: '2023-01-01T10:00:00Z',
  folder_name: 'Test Folder',
  folder_id: 1,
};

export const mockFolder = {
  id: 1,
  name: 'Test Folder',
  created_at: '2023-01-01T00:00:00Z',
  response_count: 5,
};

export const mockStats = {
  total_responses: 25,
  total_folders: 3,
  user_since: '2023-01-01T00:00:00Z',
};

// Mock axios responses
export const mockAxios = axios;

export const mockApiResponse = (data, status = 200) => {
  return Promise.resolve({
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {},
  });
};

export const mockApiError = (message = 'API Error', status = 500) => {
  const error = new Error(message);
  error.response = {
    data: { detail: message },
    status,
    statusText: 'Error',
  };
  return Promise.reject(error);
};

// Custom matchers for common assertions
export const customMatchers = {
  toBeInTheDocument: (received) => {
    const pass = received !== null && received !== undefined;
    return {
      message: () => `expected element ${pass ? 'not ' : ''}to be in document`,
      pass,
    };
  },
};

// Test helpers
export const waitForLoadingToFinish = async () => {
  const { waitForElementToBeRemoved, queryByText } = await import('@testing-library/react');
  const loadingElement = queryByText(/loading/i);
  if (loadingElement) {
    await waitForElementToBeRemoved(loadingElement);
  }
};

export const fillFormFields = async (fields) => {
  const { screen } = await import('@testing-library/react');
  const userEvent = await import('@testing-library/user-event');
  
  for (const [label, value] of Object.entries(fields)) {
    const field = screen.getByLabelText(new RegExp(label, 'i'));
    await userEvent.default.clear(field);
    await userEvent.default.type(field, value);
  }
};

// Mock implementations for common services
export const mockAuthService = {
  login: jest.fn(),
  getCurrentUser: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
};

export const mockApiService = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
};

// Authentication state helpers
export const mockAuthenticatedState = () => {
  localStorage.setItem('token', 'mock-jwt-token');
  mockAuthService.getCurrentUser.mockResolvedValue({
    success: true,
    data: mockUser,
  });
};

export const mockUnauthenticatedState = () => {
  localStorage.removeItem('token');
  mockAuthService.getCurrentUser.mockResolvedValue({
    success: false,
    error: 'Unauthorized',
  });
};

// DOM event helpers
export const createMockFile = (name = 'test.png', type = 'image/png') => {
  return new File(['mock file content'], name, { type });
};

export const createMockFileList = (files) => {
  const fileList = {
    length: files.length,
    item: (index) => files[index],
    [Symbol.iterator]: function* () {
      for (let i = 0; i < files.length; i++) {
        yield files[i];
      }
    },
  };
  
  files.forEach((file, index) => {
    fileList[index] = file;
  });
  
  return fileList;
}; 