import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Navigation from './Navigation';

// Mock the auth service
jest.mock('../services/authService', () => ({
  logout: jest.fn(),
  getCurrentUser: jest.fn(),
}));

describe('Navigation', () => {
  const mockUser = {
    username: 'testuser',
    email: 'test@example.com'
  };

  const mockOnLogout = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders navigation component', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    expect(screen.getByText('ScreenshotOCR')).toBeInTheDocument();
  });

  it('displays user information when logged in', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('shows logout button when user is logged in', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('calls onLogout when logout button is clicked', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /logout/i }));
    expect(mockOnLogout).toHaveBeenCalled();
  });

  it('displays navigation links', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    // Check for common navigation elements
    expect(screen.getByText('ScreenshotOCR')).toBeInTheDocument();
  });

  it('handles user menu toggle', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    // Find and click user menu toggle (if it exists)
    const userMenuButton = screen.getByText('testuser');
    fireEvent.click(userMenuButton);
    
    // Should show logout option
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('renders without user when not logged in', () => {
    render(
      <Navigation 
        user={null}
        onLogout={mockOnLogout}
      />
    );

    expect(screen.getByText('ScreenshotOCR')).toBeInTheDocument();
    expect(screen.queryByText('testuser')).not.toBeInTheDocument();
  });

  it('does not show logout button when user is not logged in', () => {
    render(
      <Navigation 
        user={null}
        onLogout={mockOnLogout}
      />
    );

    expect(screen.queryByRole('button', { name: /logout/i })).not.toBeInTheDocument();
  });

  it('displays user email when available', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('handles missing user properties gracefully', () => {
    const incompleteUser = { username: 'testuser' };
    
    render(
      <Navigation 
        user={incompleteUser}
        onLogout={mockOnLogout}
      />
    );

    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.queryByText('test@example.com')).not.toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    const nav = screen.getByRole('navigation');
    expect(nav).toHaveClass('navigation');
  });

  it('handles logout confirmation', () => {
    // Mock window.confirm
    const mockConfirm = jest.spyOn(window, 'confirm').mockImplementation(() => true);
    
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /logout/i }));
    
    expect(mockConfirm).toHaveBeenCalled();
    expect(mockOnLogout).toHaveBeenCalled();
    
    mockConfirm.mockRestore();
  });

  it('cancels logout when user declines confirmation', () => {
    // Mock window.confirm to return false
    const mockConfirm = jest.spyOn(window, 'confirm').mockImplementation(() => false);
    
    render(
      <Navigation 
        user={mockUser}
        onLogout={mockOnLogout}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /logout/i }));
    
    expect(mockConfirm).toHaveBeenCalled();
    expect(mockOnLogout).not.toHaveBeenCalled();
    
    mockConfirm.mockRestore();
  });
}); 