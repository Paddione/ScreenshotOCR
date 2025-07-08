import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Eye, 
  Download, 
  Trash2, 
  Search, 
  Filter,
  ChevronLeft,
  ChevronRight,
  Folder
} from 'lucide-react';
import { api } from '../services/web_auth_service';

const ResponseList = () => {
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFolder, setSelectedFolder] = useState('');
  const [folders, setFolders] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  });

  useEffect(() => {
    loadResponses();
    loadFolders();
  }, [pagination.page, selectedFolder]);

  const loadResponses = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString()
      });
      
      if (selectedFolder) {
        params.append('folder_id', selectedFolder);
      }

      const response = await api.get(`/responses?${params}`);
      if (response.data) {
        setResponses(response.data.items);
        setPagination(prev => ({
          ...prev,
          total: response.data.total,
          pages: response.data.pages
        }));
      }
    } catch (error) {
      console.error('Error loading responses:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFolders = async () => {
    try {
      const response = await api.get('/folders');
      if (response.data) {
        setFolders(response.data);
      }
    } catch (error) {
      console.error('Error loading folders:', error);
    }
  };

  const handleDelete = async (responseId) => {
    if (!window.confirm('Are you sure you want to delete this response?')) {
      return;
    }

    try {
      await api.delete(`/responses/${responseId}`);
      loadResponses(); // Reload list
    } catch (error) {
      console.error('Error deleting response:', error);
      alert('Failed to delete response');
    }
  };

  const handleExportPDF = async (responseId) => {
    try {
      const response = await api.get(`/export/${responseId}/pdf`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis_report_${responseId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('Failed to export PDF');
    }
  };

  const filteredResponses = responses.filter(response =>
    response.ocr_text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    response.ai_response?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text, maxLength = 150) => {
    if (!text) return 'No text extracted';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="response-list">
      <div className="page-header">
        <h1>Responses</h1>
        <p>Manage your screenshot analysis results</p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="filters">
          <div className="search-box">
            <Search size={20} />
            <input
              type="text"
              placeholder="Search responses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-control"
            />
          </div>
          
          <div className="filter-select">
            <Filter size={20} />
            <select
              value={selectedFolder}
              onChange={(e) => setSelectedFolder(e.target.value)}
              className="form-control"
            >
              <option value="">All Folders</option>
              {folders.map(folder => (
                <option key={folder.id} value={folder.id}>
                  {folder.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Response List */}
      <div className="card">
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading responses...</p>
          </div>
        ) : filteredResponses.length > 0 ? (
          <>
            <div className="response-grid">
              {filteredResponses.map(response => (
                <div key={response.id} className="response-card">
                  <div className="response-header">
                    <span className="response-date">
                      {formatDate(response.created_at)}
                    </span>
                    {response.folder_name && (
                      <span className="response-folder">
                        <Folder size={14} />
                        {response.folder_name}
                      </span>
                    )}
                  </div>
                  
                  <div className="response-content">
                    <div className="response-text">
                      <h4>Extracted Text</h4>
                      <p>{truncateText(response.ocr_text)}</p>
                    </div>
                    
                    <div className="response-analysis">
                      <h4>AI Analysis</h4>
                      <p>{truncateText(response.ai_response)}</p>
                    </div>
                  </div>
                  
                  <div className="response-actions">
                    <Link 
                      to={`/responses/${response.id}`}
                      className="btn btn-primary btn-sm"
                    >
                      <Eye size={16} />
                      View
                    </Link>
                    
                    <button
                      onClick={() => handleExportPDF(response.id)}
                      className="btn btn-secondary btn-sm"
                    >
                      <Download size={16} />
                      PDF
                    </button>
                    
                    <button
                      onClick={() => handleDelete(response.id)}
                      className="btn btn-danger btn-sm"
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                  disabled={pagination.page === 1}
                  className="btn btn-secondary"
                >
                  <ChevronLeft size={16} />
                  Previous
                </button>
                
                <span className="pagination-info">
                  Page {pagination.page} of {pagination.pages}
                </span>
                
                <button
                  onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                  disabled={pagination.page === pagination.pages}
                  className="btn btn-secondary"
                >
                  Next
                  <ChevronRight size={16} />
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="empty-state">
            <Search size={48} />
            <h3>No responses found</h3>
            <p>
              {searchTerm || selectedFolder 
                ? 'Try adjusting your search or filter criteria'
                : 'Upload your first screenshot to get started'
              }
            </p>
            <Link to="/upload" className="btn btn-primary">
              Upload Screenshot
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResponseList; 