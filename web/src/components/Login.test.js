import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Login from './Login';
import { renderWithRouter } from '../utils/testUtils';

describe('Login Component', () => {
  const mockOnLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders login form elements', () => {
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      expect(screen.getByRole('heading', { name: /screenshot ai analyzer/i })).toBeInTheDocument();
      expect(screen.getByText(/sign in to access your analysis dashboard/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    test('renders default credentials information', () => {
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      expect(screen.getByText(/default credentials: admin \/ admin123/i)).toBeInTheDocument();
    });

    test('renders password toggle button', () => {
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const passwordToggle = screen.getByRole('button', { name: '' });
      expect(passwordToggle).toBeInTheDocument();
    });
  });

  describe('Form Interaction', () => {
    test('allows user to type in username and password fields', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'testpass');

      expect(usernameInput).toHaveValue('testuser');
      expect(passwordInput).toHaveValue('testpass');
    });

    test('toggles password visibility', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const passwordInput = screen.getByLabelText(/password/i);
      const toggleButton = screen.getByRole('button', { name: '' });

      // Initially password should be hidden
      expect(passwordInput).toHaveAttribute('type', 'password');

      // Click toggle to show password
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'text');

      // Click again to hide password
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('clears error message when user starts typing', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockResolvedValue({
        success: false,
        error: 'Invalid credentials'
      });

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter both username and password/i)).toBeInTheDocument();
      });

      const usernameInput = screen.getByLabelText(/username/i);
      await user.type(usernameInput, 'test');

      expect(screen.queryByText(/please enter both username and password/i)).not.toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    test('shows error when submitting empty form', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter both username and password/i)).toBeInTheDocument();
      });

      expect(mockOnLogin).not.toHaveBeenCalled();
    });

    test('shows error when submitting with empty username', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const passwordInput = screen.getByLabelText(/password/i);
      await user.type(passwordInput, 'testpass');

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter both username and password/i)).toBeInTheDocument();
      });

      expect(mockOnLogin).not.toHaveBeenCalled();
    });

    test('shows error when submitting with empty password', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      await user.type(usernameInput, 'testuser');

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter both username and password/i)).toBeInTheDocument();
      });

      expect(mockOnLogin).not.toHaveBeenCalled();
    });
  });

  describe('Form Submission', () => {
    test('calls onLogin with correct credentials on successful submission', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockResolvedValue({ success: true });

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'admin');
      await user.type(passwordInput, 'admin123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnLogin).toHaveBeenCalledWith({
          username: 'admin',
          password: 'admin123'
        });
      });
    });

    test('shows loading state during submission', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockImplementation(() => new Promise(() => {})); // Never resolves

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'admin');
      await user.type(passwordInput, 'admin123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/signing in/i)).toBeInTheDocument();
        expect(submitButton).toBeDisabled();
      });
    });

    test('disables form inputs during submission', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockImplementation(() => new Promise(() => {})); // Never resolves

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const toggleButton = screen.getByRole('button', { name: '' });
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'admin');
      await user.type(passwordInput, 'admin123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(usernameInput).toBeDisabled();
        expect(passwordInput).toBeDisabled();
        expect(toggleButton).toBeDisabled();
        expect(submitButton).toBeDisabled();
      });
    });

    test('handles form submission with Enter key', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockResolvedValue({ success: true });

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);

      await user.type(usernameInput, 'admin');
      await user.type(passwordInput, 'admin123');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(mockOnLogin).toHaveBeenCalledWith({
          username: 'admin',
          password: 'admin123'
        });
      });
    });
  });

  describe('Error Handling', () => {
    test('displays error message on login failure', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockResolvedValue({
        success: false,
        error: 'Invalid credentials'
      });

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'wrong');
      await user.type(passwordInput, 'wrong');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    test('displays default error message when no specific error provided', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockResolvedValue({
        success: false
      });

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'admin');
      await user.type(passwordInput, 'admin123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/login failed/i)).toBeInTheDocument();
      });
    });

    test('resets loading state after error', async () => {
      const user = userEvent.setup();
      mockOnLogin.mockResolvedValue({
        success: false,
        error: 'Invalid credentials'
      });

      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(usernameInput, 'wrong');
      await user.type(passwordInput, 'wrong');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
        expect(submitButton).not.toBeDisabled();
        expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper form labels', () => {
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);

      expect(usernameInput).toHaveAttribute('id', 'username');
      expect(passwordInput).toHaveAttribute('id', 'password');
    });

    test('has proper autocomplete attributes', () => {
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);

      expect(usernameInput).toHaveAttribute('autocomplete', 'username');
      expect(passwordInput).toHaveAttribute('autocomplete', 'current-password');
    });

    test('has proper form submission behavior', () => {
      renderWithRouter(<Login onLogin={mockOnLogin} />);

      const form = screen.getByRole('form');
      expect(form).toBeInTheDocument();
    });
  });
}); 