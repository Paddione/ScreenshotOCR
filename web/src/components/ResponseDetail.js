import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Download, 
  Trash2, 
  Edit, 
  Folder,
  Calendar,
  Brain,
  FileText
} from 'lucide-react';
import { api } from '../services/web_auth_service';

const ResponseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadResponse();
  }, [id]);

  const loadResponse = async () => {
    try {
      setLoading(true);
      const result = await api.get(`/responses/${id}`);
      if (result.data) {
        setResponse(result.data);
      } else {
        setError('Response not found');
      }
    } catch (error) {
      console.error('Error loading response:', error);
      setError('Failed to load response');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this response?')) {
      return;
    }

    try {
      await api.delete(`/responses/${id}`);
      navigate('/responses');
    } catch (error) {
      console.error('Error deleting response:', error);
      alert('Failed to delete response');
    }
  };

  const handleExportPDF = async () => {
    try {
      const result = await api.get(`/export/${id}/pdf`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([result.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_report_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('Failed to export PDF');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading response...</p>
      </div>
    );
  }

  if (error || !response) {
    return (
      <div className="error-state">
        <h2>Error</h2>
        <p>{error || 'Response not found'}</p>
        <Link to="/responses" className="btn btn-primary">
          <ArrowLeft size={16} />
          Back to Responses
        </Link>
      </div>
    );
  }

  return (
    <div className="response-detail">
      <div className="response-header">
        <div className="header-actions">
          <Link to="/responses" className="btn btn-secondary">
            <ArrowLeft size={16} />
            Back to Responses
          </Link>
          
          <div className="action-buttons">
            <button
              onClick={handleExportPDF}
              className="btn btn-secondary"
            >
              <Download size={16} />
              Export PDF
            </button>
            
            <button
              onClick={handleDelete}
              className="btn btn-danger"
            >
              <Trash2 size={16} />
              Delete
            </button>
          </div>
        </div>
        
        <div className="response-meta">
          <h1>Analysis Details</h1>
          
          <div className="meta-info">
            <div className="meta-item">
              <Calendar size={16} />
              <span>Created: {formatDate(response.created_at)}</span>
            </div>
            
            {response.folder_name && (
              <div className="meta-item">
                <Folder size={16} />
                <span>Folder: {response.folder_name}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="response-content">
        <div className="content-section">
          <div className="section-header">
            <FileText size={20} />
            <h2>Extracted Text</h2>
          </div>
          
          <div className="content-box">
            {response.ocr_text ? (
              <div className="text-content">
                <pre>{response.ocr_text}</pre>
              </div>
            ) : (
              <div className="empty-content">
                <p>No text was extracted from this image.</p>
              </div>
            )}
          </div>
        </div>

        <div className="content-section">
          <div className="section-header">
            <Brain size={20} />
            <h2>AI Analysis</h2>
          </div>
          
          <div className="content-box">
            {response.ai_response ? (
              <div className="analysis-content">
                <div className="analysis-text">
                  {response.ai_response.split('\n').map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
              </div>
            ) : (
              <div className="empty-content">
                <p>No AI analysis is available for this response.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponseDetail; 