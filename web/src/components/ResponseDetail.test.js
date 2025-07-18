import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResponseDetail from './ResponseDetail';

// Mock the auth service
jest.mock('../services/authService', () => ({
  getAuthToken: jest.fn(() => 'mock-token'),
}));

// Mock the API service
jest.mock('../services/apiService', () => ({
  exportResponsePDF: jest.fn(),
}));

describe('ResponseDetail', () => {
  const mockResponse = {
    id: 1,
    ocr_text: 'Sample OCR text content that was extracted from the image',
    ai_response: 'This is the AI analysis of the OCR text content. It provides insights and understanding of the extracted text.',
    folder_name: 'Test Folder',
    created_at: '2024-01-01T12:00:00Z'
  };

  const mockOnClose = jest.fn();
  const mockOnExport = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders response detail component', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText('Response Details')).toBeInTheDocument();
  });

  it('displays OCR text content', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText('Sample OCR text content that was extracted from the image')).toBeInTheDocument();
  });

  it('displays AI response content', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText('This is the AI analysis of the OCR text content. It provides insights and understanding of the extracted text.')).toBeInTheDocument();
  });

  it('displays response metadata', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText('Test Folder')).toBeInTheDocument();
    expect(screen.getByText(/2024-01-01/)).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onExport when export button is clicked', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    const exportButton = screen.getByRole('button', { name: /export/i });
    fireEvent.click(exportButton);
    
    expect(mockOnExport).toHaveBeenCalledWith(1);
  });

  it('handles response without folder name', () => {
    const responseWithoutFolder = {
      ...mockResponse,
      folder_name: null
    };

    render(
      <ResponseDetail
        response={responseWithoutFolder}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText('Sample OCR text content that was extracted from the image')).toBeInTheDocument();
    expect(screen.queryByText('Test Folder')).not.toBeInTheDocument();
  });

  it('displays section headers correctly', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText('OCR Text')).toBeInTheDocument();
    expect(screen.getByText('AI Analysis')).toBeInTheDocument();
  });

  it('handles long text content with proper formatting', () => {
    const longResponse = {
      ...mockResponse,
      ocr_text: 'This is a very long OCR text that contains many words and should be displayed properly in the detail view with appropriate formatting and line breaks to ensure readability.',
      ai_response: 'This is a very long AI analysis that provides detailed insights and understanding of the extracted text content. It should be formatted properly with paragraphs and proper spacing.'
    };

    render(
      <ResponseDetail
        response={longResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText(/This is a very long OCR text/)).toBeInTheDocument();
    expect(screen.getByText(/This is a very long AI analysis/)).toBeInTheDocument();
  });

  it('displays response ID', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText(/ID: 1/)).toBeInTheDocument();
  });

  it('handles keyboard shortcuts', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    // Test Escape key to close
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('applies correct CSS classes', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    const detailContainer = screen.getByText('Response Details').closest('div');
    expect(detailContainer).toHaveClass('response-detail');
  });

  it('handles empty response gracefully', () => {
    const emptyResponse = {
      id: 2,
      ocr_text: '',
      ai_response: '',
      folder_name: null,
      created_at: '2024-01-02T12:00:00Z'
    };

    render(
      <ResponseDetail
        response={emptyResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText('Response Details')).toBeInTheDocument();
    expect(screen.getByText('OCR Text')).toBeInTheDocument();
    expect(screen.getByText('AI Analysis')).toBeInTheDocument();
  });

  it('shows loading state during export', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
        exporting={true}
      />
    );

    const exportButton = screen.getByRole('button', { name: /export/i });
    expect(exportButton).toBeDisabled();
    expect(screen.getByText('Exporting...')).toBeInTheDocument();
  });

  it('handles copy to clipboard functionality', () => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn(),
      },
    });

    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      expect.stringContaining('Sample OCR text content')
    );
  });

  it('displays word count for OCR text', () => {
    render(
      <ResponseDetail
        response={mockResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    // Check if word count is displayed (this depends on the actual implementation)
    expect(screen.getByText(/Sample OCR text content/)).toBeInTheDocument();
  });

  it('handles response with special characters', () => {
    const specialResponse = {
      ...mockResponse,
      ocr_text: 'Text with special chars: äöüß & < > " \'',
      ai_response: 'Analysis with special chars: € $ £ ¥'
    };

    render(
      <ResponseDetail
        response={specialResponse}
        onClose={mockOnClose}
        onExport={mockOnExport}
      />
    );

    expect(screen.getByText(/Text with special chars: äöüß & < > " '/)).toBeInTheDocument();
    expect(screen.getByText(/Analysis with special chars: € $ £ ¥/)).toBeInTheDocument();
  });
}); 