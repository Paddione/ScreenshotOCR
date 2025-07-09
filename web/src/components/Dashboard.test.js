import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from './Dashboard';
import { api } from '../services/web_auth_service';
import { renderWithRouter, mockStats, mockResponse } from '../utils/testUtils';

// Mock the API service
jest.mock('../services/web_auth_service', () => ({
  api: {
    get: jest.fn(),
  },
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Loading State', () => {
    test('shows loading spinner initially', () => {
      api.get.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      renderWithRouter(<Dashboard />);
      
      expect(screen.getByText(/loading dashboard/i)).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });

  describe('Data Loading', () => {
    test('loads dashboard data on mount', async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [mockResponse] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith('/stats');
        expect(api.get).toHaveBeenCalledWith('/responses?per_page=5');
      });
    });

    test('handles API errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      api.get.mockRejectedValue(new Error('API Error'));

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error loading dashboard data:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Stats Display', () => {
    beforeEach(async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [] } });
    });

    test('displays total responses stat', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(mockStats.total_responses.toString())).toBeInTheDocument();
        expect(screen.getByText(/total responses/i)).toBeInTheDocument();
      });
    });

    test('displays total folders stat', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(mockStats.total_folders.toString())).toBeInTheDocument();
        expect(screen.getByText(/folders/i)).toBeInTheDocument();
      });
    });

    test('displays member since date', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/jan 1, 2023/i)).toBeInTheDocument();
        expect(screen.getByText(/member since/i)).toBeInTheDocument();
      });
    });

    test('displays system status', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/active/i)).toBeInTheDocument();
        expect(screen.getByText(/system status/i)).toBeInTheDocument();
      });
    });

    test('handles missing stats data', async () => {
      api.get.mockResolvedValueOnce({ data: null });
      api.get.mockResolvedValueOnce({ data: { items: [] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('0')).toBeInTheDocument(); // Should show 0 for missing data
      });
    });
  });

  describe('Quick Actions', () => {
    beforeEach(async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [] } });
    });

    test('renders quick action cards', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/upload screenshot/i)).toBeInTheDocument();
        expect(screen.getByText(/view responses/i)).toBeInTheDocument();
        expect(screen.getByText(/manage folders/i)).toBeInTheDocument();
      });
    });

    test('quick action links have correct destinations', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const uploadLink = screen.getByRole('link', { name: /upload screenshot/i });
        const responsesLink = screen.getByRole('link', { name: /view responses/i });
        const foldersLink = screen.getByRole('link', { name: /manage folders/i });

        expect(uploadLink).toHaveAttribute('href', '/upload');
        expect(responsesLink).toHaveAttribute('href', '/responses');
        expect(foldersLink).toHaveAttribute('href', '/folders');
      });
    });

    test('quick action cards display descriptions', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/upload an image for ocr and ai analysis/i)).toBeInTheDocument();
        expect(screen.getByText(/browse and manage your analysis results/i)).toBeInTheDocument();
        expect(screen.getByText(/organize your responses into folders/i)).toBeInTheDocument();
      });
    });
  });

  describe('Recent Responses', () => {
    test('displays recent responses when available', async () => {
      const recentResponses = [
        {
          id: 1,
          ocr_text: 'Sample OCR text from image',
          created_at: '2023-01-01T10:00:00Z',
          folder_name: 'Test Folder'
        },
        {
          id: 2,
          ocr_text: 'Another response with longer text that should be truncated because it exceeds the maximum length',
          created_at: '2023-01-02T11:00:00Z',
          folder_name: null
        }
      ];

      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: recentResponses } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/recent responses/i)).toBeInTheDocument();
        expect(screen.getByText(/sample ocr text from image/i)).toBeInTheDocument();
        expect(screen.getByText(/test folder/i)).toBeInTheDocument();
      });
    });

    test('truncates long response text', async () => {
      const longResponse = {
        id: 1,
        ocr_text: 'This is a very long response text that should be truncated because it exceeds the maximum length limit set for display in the dashboard component',
        created_at: '2023-01-01T10:00:00Z',
        folder_name: 'Test Folder'
      };

      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [longResponse] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const truncatedText = screen.getByText(/this is a very long response text that should be truncated/i);
        expect(truncatedText.textContent).toMatch(/\.\.\.$/);
      });
    });

    test('handles responses without OCR text', async () => {
      const responseWithoutText = {
        id: 1,
        ocr_text: '',
        created_at: '2023-01-01T10:00:00Z',
        folder_name: 'Test Folder'
      };

      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [responseWithoutText] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/no text extracted/i)).toBeInTheDocument();
      });
    });

    test('shows view all responses link', async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [mockResponse] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const viewAllLink = screen.getByRole('link', { name: /view all responses/i });
        expect(viewAllLink).toHaveAttribute('href', '/responses');
      });
    });

    test('displays empty state when no responses', async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/no responses yet/i)).toBeInTheDocument();
      });
    });
  });

  describe('Date Formatting', () => {
    test('formats dates correctly', async () => {
      const testResponse = {
        id: 1,
        ocr_text: 'Test text',
        created_at: '2023-12-25T14:30:00Z',
        folder_name: 'Test Folder'
      };

      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [testResponse] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/dec 25, 2023/i)).toBeInTheDocument();
      });
    });

    test('handles invalid dates gracefully', async () => {
      const testResponse = {
        id: 1,
        ocr_text: 'Test text',
        created_at: 'invalid-date',
        folder_name: 'Test Folder'
      };

      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [testResponse] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/invalid date/i)).toBeInTheDocument();
      });
    });
  });

  describe('Component Structure', () => {
    test('renders dashboard header', async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
        expect(screen.getByText(/welcome to your screenshot analysis dashboard/i)).toBeInTheDocument();
      });
    });

    test('renders all main sections', async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/quick actions/i)).toBeInTheDocument();
        expect(screen.getByText(/recent responses/i)).toBeInTheDocument();
        expect(screen.getByText(/common tasks and shortcuts/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper heading hierarchy', async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const mainHeading = screen.getByRole('heading', { level: 1, name: /dashboard/i });
        const sectionHeadings = screen.getAllByRole('heading', { level: 2 });
        
        expect(mainHeading).toBeInTheDocument();
        expect(sectionHeadings).toHaveLength(2); // Quick Actions and Recent Responses
      });
    });

    test('has proper link text for screen readers', async () => {
      api.get.mockResolvedValueOnce({ data: mockStats });
      api.get.mockResolvedValueOnce({ data: { items: [mockResponse] } });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const viewLink = screen.getByRole('link', { name: /view/i });
        expect(viewLink).toHaveAttribute('href', `/responses/${mockResponse.id}`);
      });
    });
  });
}); 