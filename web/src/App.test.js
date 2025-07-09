import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import authService from './services/web_auth_service';
import { 
  mockUser, 
  mockAuthenticatedState, 
  mockUnauthenticatedState,
  mockApiResponse,
  mockApiError
} from './utils/testUtils';

// Mock the auth service
jest.mock('./services/web_auth_service');

// Mock all the components to avoid complex dependencies
jest.mock('./components/Login', () => {
  return function MockLogin({ onLogin }) {
    return (
      <div data-testid="login-component">
        <button onClick={() => onLogin({ username: 'test', password: 'test' })}>
          Login
        </button>
      </div>
    );
  };
});

jest.mock('./components/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard-component">Dashboard</div>;
  };
});

jest.mock('./components/Navigation', () => {
  return function MockNavigation({ user, onLogout }) {
    return (
      <nav data-testid="navigation-component">
        <span>Welcome {user?.username}</span>
        <button onClick={onLogout}>Logout</button>
      </nav>
    );
  };
});

jest.mock('./components/ResponseList', () => {
  return function MockResponseList() {
    return <div data-testid="response-list-component">Response List</div>;
  };
});

jest.mock('./components/ResponseDetail', () => {
  return function MockResponseDetail() {
    return <div data-testid="response-detail-component">Response Detail</div>;
  };
});

jest.mock('./components/FolderManager', () => {
  return function MockFolderManager() {
    return <div data-testid="folder-manager-component">Folder Manager</div>;
  };
});

jest.mock('./components/Upload', () => {
  return function MockUpload() {
    return <div data-testid="upload-component">Upload</div>;
  };
});

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Authentication Flow', () => {
    test('shows loading spinner initially', async () => {
      authService.getCurrentUser.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    test('shows login when not authenticated', async () => {
      mockUnauthenticatedState();

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });
    });

    test('shows dashboard when authenticated', async () => {
      mockAuthenticatedState();

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('dashboard-component')).toBeInTheDocument();
        expect(screen.getByTestId('navigation-component')).toBeInTheDocument();
      });
    });

    test('handles authentication check failure', async () => {
      localStorage.setItem('token', 'invalid-token');
      authService.getCurrentUser.mockResolvedValue({
        success: false,
        error: 'Invalid token'
      });

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
        expect(localStorage.getItem('token')).toBeNull();
      });
    });
  });

  describe('Login Functionality', () => {
    test('handles successful login', async () => {
      mockUnauthenticatedState();
      authService.login.mockResolvedValue({
        success: true,
        data: {
          access_token: 'new-token',
          user: mockUser
        }
      });

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });

      const loginButton = screen.getByText('Login');
      loginButton.click();

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBe('new-token');
        expect(screen.getByTestId('dashboard-component')).toBeInTheDocument();
      });
    });

    test('handles login failure', async () => {
      mockUnauthenticatedState();
      authService.login.mockResolvedValue({
        success: false,
        error: 'Invalid credentials'
      });

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });

      const loginButton = screen.getByText('Login');
      loginButton.click();

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBeNull();
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });
    });
  });

  describe('Logout Functionality', () => {
    test('handles logout correctly', async () => {
      mockAuthenticatedState();

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('navigation-component')).toBeInTheDocument();
      });

      const logoutButton = screen.getByText('Logout');
      logoutButton.click();

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBeNull();
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('handles authentication check error gracefully', async () => {
      localStorage.setItem('token', 'some-token');
      authService.getCurrentUser.mockRejectedValue(new Error('Network error'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
        expect(localStorage.getItem('token')).toBeNull();
        expect(consoleSpy).toHaveBeenCalledWith('Authentication check failed:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

    test('handles login exception', async () => {
      mockUnauthenticatedState();
      authService.login.mockRejectedValue(new Error('Network error'));

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });

      const loginButton = screen.getByText('Login');
      loginButton.click();

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBeNull();
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });
    });
  });

  describe('User State Management', () => {
    test('manages user state correctly on login', async () => {
      mockUnauthenticatedState();
      authService.login.mockResolvedValue({
        success: true,
        data: {
          access_token: 'new-token',
          user: mockUser
        }
      });

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });

      const loginButton = screen.getByText('Login');
      loginButton.click();

      await waitFor(() => {
        expect(screen.getByText(`Welcome ${mockUser.username}`)).toBeInTheDocument();
      });
    });

    test('clears user state on logout', async () => {
      mockAuthenticatedState();

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(`Welcome ${mockUser.username}`)).toBeInTheDocument();
      });

      const logoutButton = screen.getByText('Logout');
      logoutButton.click();

      await waitFor(() => {
        expect(screen.queryByText(`Welcome ${mockUser.username}`)).not.toBeInTheDocument();
      });
    });
  });

  describe('Token Management', () => {
    test('uses existing token on app load', async () => {
      localStorage.setItem('token', 'existing-token');
      authService.getCurrentUser.mockResolvedValue({
        success: true,
        data: mockUser
      });

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(authService.getCurrentUser).toHaveBeenCalled();
        expect(screen.getByTestId('dashboard-component')).toBeInTheDocument();
      });
    });

    test('removes invalid token', async () => {
      localStorage.setItem('token', 'invalid-token');
      authService.getCurrentUser.mockResolvedValue({
        success: false,
        error: 'Token expired'
      });

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBeNull();
        expect(screen.getByTestId('login-component')).toBeInTheDocument();
      });
    });
  });
}); 