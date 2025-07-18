import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResponseList from './ResponseList';

// Mock the auth service
jest.mock('../services/authService', () => ({
  getAuthToken: jest.fn(() => 'mock-token'),
}));

// Mock the API service
jest.mock('../services/apiService', () => ({
  getResponses: jest.fn(),
  deleteResponse: jest.fn(),
}));

describe('ResponseList', () => {
  const mockResponses = [
    {
      id: 1,
      ocr_text: 'Sample OCR text 1',
      ai_response: 'AI analysis 1',
      folder_name: 'Test Folder',
      created_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 2,
      ocr_text: 'Sample OCR text 2',
      ai_response: 'AI analysis 2',
      folder_name: 'Test Folder',
      created_at: '2024-01-02T00:00:00Z'
    }
  ];

  const mockOnResponseSelect = jest.fn();
  const mockOnResponseDelete = jest.fn();
  const mockOnPageChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders response list component', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    expect(screen.getByText('Responses')).toBeInTheDocument();
  });

  it('displays list of responses', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    expect(screen.getByText('Sample OCR text 1')).toBeInTheDocument();
    expect(screen.getByText('Sample OCR text 2')).toBeInTheDocument();
  });

  it('shows empty state when no responses', () => {
    render(
      <ResponseList
        responses={[]}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    expect(screen.getByText('No responses yet')).toBeInTheDocument();
  });

  it('calls onResponseSelect when response is clicked', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    fireEvent.click(screen.getByText('Sample OCR text 1'));
    expect(mockOnResponseSelect).toHaveBeenCalledWith(1);
  });

  it('highlights selected response', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={1}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    const selectedResponse = screen.getByText('Sample OCR text 1').closest('div');
    expect(selectedResponse).toHaveClass('selected');
  });

  it('shows loading state', () => {
    render(
      <ResponseList
        responses={[]}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={true}
      />
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('displays pagination controls when multiple pages', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={3}
        loading={false}
      />
    );

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('calls onPageChange when page is clicked', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={3}
        loading={false}
      />
    );

    fireEvent.click(screen.getByText('2'));
    expect(mockOnPageChange).toHaveBeenCalledWith(2);
  });

  it('shows delete button for each response', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    expect(deleteButtons).toHaveLength(2);
  });

  it('calls onResponseDelete when delete button is clicked', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    expect(mockOnResponseDelete).toHaveBeenCalledWith(1);
  });

  it('displays response metadata', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    expect(screen.getByText('Test Folder')).toBeInTheDocument();
    expect(screen.getByText(/2024-01-01/)).toBeInTheDocument();
  });

  it('truncates long OCR text', () => {
    const longResponse = {
      id: 3,
      ocr_text: 'This is a very long OCR text that should be truncated when displayed in the list view to prevent the UI from becoming cluttered and difficult to read',
      ai_response: 'AI analysis',
      folder_name: 'Test Folder',
      created_at: '2024-01-03T00:00:00Z'
    };

    render(
      <ResponseList
        responses={[longResponse]}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    const truncatedText = screen.getByText(/This is a very long OCR text/);
    expect(truncatedText).toBeInTheDocument();
  });

  it('handles response without folder name', () => {
    const responseWithoutFolder = {
      id: 4,
      ocr_text: 'Sample text',
      ai_response: 'AI analysis',
      folder_name: null,
      created_at: '2024-01-04T00:00:00Z'
    };

    render(
      <ResponseList
        responses={[responseWithoutFolder]}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    expect(screen.getByText('Sample text')).toBeInTheDocument();
    expect(screen.queryByText('Test Folder')).not.toBeInTheDocument();
  });

  it('formats dates correctly', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    // Check that dates are formatted (this will depend on the actual formatting used)
    expect(screen.getByText(/2024-01-01/)).toBeInTheDocument();
  });

  it('handles keyboard navigation', () => {
    render(
      <ResponseList
        responses={mockResponses}
        selectedResponse={null}
        onResponseSelect={mockOnResponseSelect}
        onResponseDelete={mockOnResponseDelete}
        onPageChange={mockOnPageChange}
        currentPage={1}
        totalPages={1}
        loading={false}
      />
    );

    const firstResponse = screen.getByText('Sample OCR text 1');
    fireEvent.keyDown(firstResponse, { key: 'Enter' });
    
    expect(mockOnResponseSelect).toHaveBeenCalledWith(1);
  });
}); 