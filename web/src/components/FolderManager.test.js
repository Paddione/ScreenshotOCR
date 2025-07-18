import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FolderManager from './FolderManager';

// Mock the auth service
jest.mock('../services/authService', () => ({
  getAuthToken: jest.fn(() => 'mock-token'),
}));

// Mock the API service
jest.mock('../services/apiService', () => ({
  getFolders: jest.fn(),
  createFolder: jest.fn(),
  deleteFolder: jest.fn(),
}));

describe('FolderManager', () => {
  const mockFolders = [
    { id: 1, name: 'Test Folder 1', created_at: '2024-01-01T00:00:00Z' },
    { id: 2, name: 'Test Folder 2', created_at: '2024-01-02T00:00:00Z' },
  ];

  const mockOnFolderSelect = jest.fn();
  const mockOnFolderCreate = jest.fn();
  const mockOnFolderDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders folder manager component', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    expect(screen.getByText('Folders')).toBeInTheDocument();
    expect(screen.getByText('Create New Folder')).toBeInTheDocument();
  });

  it('displays list of folders', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    expect(screen.getByText('Test Folder 1')).toBeInTheDocument();
    expect(screen.getByText('Test Folder 2')).toBeInTheDocument();
  });

  it('shows empty state when no folders', () => {
    render(
      <FolderManager
        folders={[]}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    expect(screen.getByText('No folders yet')).toBeInTheDocument();
  });

  it('calls onFolderSelect when folder is clicked', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    fireEvent.click(screen.getByText('Test Folder 1'));
    expect(mockOnFolderSelect).toHaveBeenCalledWith(1);
  });

  it('highlights selected folder', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={1}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    const selectedFolder = screen.getByText('Test Folder 1').closest('div');
    expect(selectedFolder).toHaveClass('selected');
  });

  it('opens create folder dialog when button is clicked', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    fireEvent.click(screen.getByText('Create New Folder'));
    expect(screen.getByText('Create New Folder')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter folder name')).toBeInTheDocument();
  });

  it('creates new folder when form is submitted', async () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    // Open create dialog
    fireEvent.click(screen.getByText('Create New Folder'));
    
    // Fill in folder name
    const input = screen.getByPlaceholderText('Enter folder name');
    fireEvent.change(input, { target: { value: 'New Test Folder' } });
    
    // Submit form
    fireEvent.click(screen.getByText('Create'));
    
    await waitFor(() => {
      expect(mockOnFolderCreate).toHaveBeenCalledWith('New Test Folder');
    });
  });

  it('cancels folder creation when cancel button is clicked', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    // Open create dialog
    fireEvent.click(screen.getByText('Create New Folder'));
    
    // Click cancel
    fireEvent.click(screen.getByText('Cancel'));
    
    // Dialog should be closed
    expect(screen.queryByPlaceholderText('Enter folder name')).not.toBeInTheDocument();
  });

  it('shows delete confirmation when delete button is clicked', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={1}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    // Click delete button (assuming it exists)
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);
    
    expect(screen.getByText(/Are you sure/i)).toBeInTheDocument();
  });

  it('calls onFolderDelete when delete is confirmed', async () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={1}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    // Click delete button
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);
    
    // Confirm deletion
    fireEvent.click(screen.getByText('Delete'));
    
    await waitFor(() => {
      expect(mockOnFolderDelete).toHaveBeenCalledWith(1);
    });
  });

  it('cancels deletion when cancel is clicked', () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={1}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    // Click delete button
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);
    
    // Cancel deletion
    fireEvent.click(screen.getByText('Cancel'));
    
    // Confirmation dialog should be closed
    expect(screen.queryByText(/Are you sure/i)).not.toBeInTheDocument();
  });

  it('validates folder name input', async () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    // Open create dialog
    fireEvent.click(screen.getByText('Create New Folder'));
    
    // Try to submit empty name
    fireEvent.click(screen.getByText('Create'));
    
    await waitFor(() => {
      expect(screen.getByText('Folder name is required')).toBeInTheDocument();
    });
  });

  it('prevents duplicate folder names', async () => {
    render(
      <FolderManager
        folders={mockFolders}
        selectedFolder={null}
        onFolderSelect={mockOnFolderSelect}
        onFolderCreate={mockOnFolderCreate}
        onFolderDelete={mockOnFolderDelete}
      />
    );

    // Open create dialog
    fireEvent.click(screen.getByText('Create New Folder'));
    
    // Try to create folder with existing name
    const input = screen.getByPlaceholderText('Enter folder name');
    fireEvent.change(input, { target: { value: 'Test Folder 1' } });
    fireEvent.click(screen.getByText('Create'));
    
    await waitFor(() => {
      expect(screen.getByText('Folder name already exists')).toBeInTheDocument();
    });
  });
}); 