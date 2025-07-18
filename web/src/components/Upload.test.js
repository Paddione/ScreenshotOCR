import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Upload from './Upload';

// Mock the auth service
jest.mock('../services/authService', () => ({
  getAuthToken: jest.fn(() => 'mock-token'),
}));

// Mock the API service
jest.mock('../services/apiService', () => ({
  uploadScreenshot: jest.fn(),
  uploadClipboardText: jest.fn(),
  uploadClipboardImage: jest.fn(),
  batchUpload: jest.fn(),
}));

describe('Upload', () => {
  const mockOnUploadSuccess = jest.fn();
  const mockOnUploadError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload component', () => {
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    expect(screen.getByText('Upload Screenshot')).toBeInTheDocument();
  });

  it('displays drag and drop area', () => {
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    expect(screen.getByText(/Drag and drop files here/)).toBeInTheDocument();
  });

  it('shows file input button', () => {
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    expect(screen.getByRole('button', { name: /choose files/i })).toBeInTheDocument();
  });

  it('handles file selection via button', async () => {
    const mockFile = new File(['test image content'], 'test.png', { type: 'image/png' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });
  });

  it('handles drag and drop', async () => {
    const mockFile = new File(['test image content'], 'test.png', { type: 'image/png' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const dropZone = screen.getByText(/Drag and drop files here/).closest('div');
    
    fireEvent.dragEnter(dropZone);
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [mockFile]
      }
    });

    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });
  });

  it('validates file types', async () => {
    const invalidFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    await waitFor(() => {
      expect(screen.getByText(/Invalid file type/)).toBeInTheDocument();
    });
  });

  it('validates file size', async () => {
    // Create a large file (over 10MB)
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.png', { type: 'image/png' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    await waitFor(() => {
      expect(screen.getByText(/File too large/)).toBeInTheDocument();
    });
  });

  it('shows upload progress', async () => {
    const mockFile = new File(['test image content'], 'test.png', { type: 'image/png' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });

    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);

    expect(screen.getByText(/Uploading/)).toBeInTheDocument();
  });

  it('handles clipboard text upload', async () => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        readText: jest.fn().mockResolvedValue('Sample clipboard text'),
      },
    });

    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const clipboardButton = screen.getByRole('button', { name: /clipboard text/i });
    fireEvent.click(clipboardButton);

    await waitFor(() => {
      expect(screen.getByText('Sample clipboard text')).toBeInTheDocument();
    });
  });

  it('handles clipboard image upload', async () => {
    // Mock clipboard API for images
    const mockImageBlob = new Blob(['fake image data'], { type: 'image/png' });
    Object.assign(navigator, {
      clipboard: {
        read: jest.fn().mockResolvedValue([
          {
            type: 'image/png',
            getType: () => 'image/png',
            getAsFile: () => new File(['fake image data'], 'clipboard.png', { type: 'image/png' })
          }
        ]),
      },
    });

    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const clipboardButton = screen.getByRole('button', { name: /clipboard image/i });
    fireEvent.click(clipboardButton);

    await waitFor(() => {
      expect(screen.getByText('clipboard.png')).toBeInTheDocument();
    });
  });

  it('handles batch upload', async () => {
    const mockFiles = [
      new File(['test1'], 'test1.png', { type: 'image/png' }),
      new File(['test2'], 'test2.png', { type: 'image/png' }),
      new File(['test3'], 'test3.png', { type: 'image/png' })
    ];
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: mockFiles } });

    await waitFor(() => {
      expect(screen.getByText('test1.png')).toBeInTheDocument();
      expect(screen.getByText('test2.png')).toBeInTheDocument();
      expect(screen.getByText('test3.png')).toBeInTheDocument();
    });
  });

  it('limits batch upload size', async () => {
    const mockFiles = Array.from({ length: 25 }, (_, i) => 
      new File(['test'], `test${i}.png`, { type: 'image/png' })
    );
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: mockFiles } });

    await waitFor(() => {
      expect(screen.getByText(/Too many files/)).toBeInTheDocument();
    });
  });

  it('removes files from list', async () => {
    const mockFile = new File(['test image content'], 'test.png', { type: 'image/png' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });

    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);

    expect(screen.queryByText('test.png')).not.toBeInTheDocument();
  });

  it('clears all files', async () => {
    const mockFiles = [
      new File(['test1'], 'test1.png', { type: 'image/png' }),
      new File(['test2'], 'test2.png', { type: 'image/png' })
    ];
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: mockFiles } });

    await waitFor(() => {
      expect(screen.getByText('test1.png')).toBeInTheDocument();
      expect(screen.getByText('test2.png')).toBeInTheDocument();
    });

    const clearButton = screen.getByRole('button', { name: /clear all/i });
    fireEvent.click(clearButton);

    expect(screen.queryByText('test1.png')).not.toBeInTheDocument();
    expect(screen.queryByText('test2.png')).not.toBeInTheDocument();
  });

  it('shows selected folder information', () => {
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={{ id: 1, name: 'Test Folder' }}
      />
    );

    expect(screen.getByText(/Uploading to: Test Folder/)).toBeInTheDocument();
  });

  it('handles upload errors', async () => {
    const mockFile = new File(['test image content'], 'test.png', { type: 'image/png' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });

    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);

    // Simulate upload error
    await waitFor(() => {
      expect(mockOnUploadError).toHaveBeenCalled();
    });
  });

  it('handles successful upload', async () => {
    const mockFile = new File(['test image content'], 'test.png', { type: 'image/png' });
    
    render(
      <Upload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        selectedFolder={null}
      />
    );

    const fileInput = screen.getByLabelText(/choose files/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });

    const uploadButton = screen.getByRole('button', { name: /upload/i });
    fireEvent.click(uploadButton);

    // Simulate successful upload
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalled();
    });
  });
}); 