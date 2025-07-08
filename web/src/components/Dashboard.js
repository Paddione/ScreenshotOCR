import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Folder, 
  Clock, 
  TrendingUp,
  Upload,
  Eye
} from 'lucide-react';
import { api } from '../services/web_auth_service';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_responses: 0,
    total_folders: 0,
    user_since: null
  });
  const [recentResponses, setRecentResponses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load stats
      const statsResponse = await api.get('/stats');
      if (statsResponse.data) {
        setStats(statsResponse.data);
      }

      // Load recent responses
      const responsesResponse = await api.get('/responses?per_page=5');
      if (responsesResponse.data?.items) {
        setRecentResponses(responsesResponse.data.items);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text) return 'No text extracted';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome to your screenshot analysis dashboard</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <FileText size={24} />
          </div>
          <div className="stat-content">
            <h3>{stats.total_responses}</h3>
            <p>Total Responses</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Folder size={24} />
          </div>
          <div className="stat-content">
            <h3>{stats.total_folders}</h3>
            <p>Folders</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Clock size={24} />
          </div>
          <div className="stat-content">
            <h3>{stats.user_since ? formatDate(stats.user_since) : 'N/A'}</h3>
            <p>Member Since</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <h3>Active</h3>
            <p>System Status</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h2>Quick Actions</h2>
          <p>Common tasks and shortcuts</p>
        </div>
        
        <div className="quick-actions">
          <Link to="/upload" className="action-card">
            <Upload size={32} />
            <h3>Upload Screenshot</h3>
            <p>Upload an image for OCR and AI analysis</p>
          </Link>
          
          <Link to="/responses" className="action-card">
            <FileText size={32} />
            <h3>View Responses</h3>
            <p>Browse and manage your analysis results</p>
          </Link>
          
          <Link to="/folders" className="action-card">
            <Folder size={32} />
            <h3>Manage Folders</h3>
            <p>Organize your responses into folders</p>
          </Link>
        </div>
      </div>

      {/* Recent Responses */}
      <div className="card">
        <div className="card-header">
          <h2>Recent Responses</h2>
          <p>Your latest screenshot analyses</p>
        </div>
        
        {recentResponses.length > 0 ? (
          <div className="recent-responses">
            {recentResponses.map((response) => (
              <div key={response.id} className="response-item">
                <div className="response-content">
                  <div className="response-header">
                    <span className="response-date">
                      {formatDateTime(response.created_at)}
                    </span>
                    {response.folder_name && (
                      <span className="response-folder">
                        <Folder size={14} />
                        {response.folder_name}
                      </span>
                    )}
                  </div>
                  <p className="response-text">
                    {truncateText(response.ocr_text)}
                  </p>
                </div>
                <Link 
                  to={`/responses/${response.id}`}
                  className="response-action"
                >
                  <Eye size={16} />
                  View
                </Link>
              </div>
            ))}
            
            <div className="view-all">
              <Link to="/responses" className="btn btn-secondary">
                View All Responses
              </Link>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <FileText size={48} />
            <h3>No responses yet</h3>
            <p>Upload your first screenshot to get started</p>
            <Link to="/upload" className="btn btn-primary">
              <Upload size={16} />
              Upload Screenshot
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 