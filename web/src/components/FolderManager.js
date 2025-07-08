import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Trash2, 
  Edit, 
  Folder,
  FolderOpen,
  Save,
  X
} from 'lucide-react';
import { api } from '../services/web_auth_service';

const FolderManager = () => {
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingFolder, setEditingFolder] = useState(null);
  const [newFolderName, setNewFolderName] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadFolders();
  }, []);

  const loadFolders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/folders');
      if (response.data) {
        setFolders(response.data);
      }
    } catch (error) {
      console.error('Error loading folders:', error);
      setError('Failed to load folders');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFolder = async (e) => {
    e.preventDefault();
    
    if (!newFolderName.trim()) {
      setError('Folder name is required');
      return;
    }

    try {
      const response = await api.post('/folders', {
        name: newFolderName.trim()
      });
      
      if (response.data) {
        setFolders([...folders, response.data]);
        setNewFolderName('');
        setShowCreateForm(false);
        setError('');
      }
    } catch (error) {
      console.error('Error creating folder:', error);
      setError(error.response?.data?.detail || 'Failed to create folder');
    }
  };

  const handleDeleteFolder = async (folderId, folderName) => {
    if (!window.confirm(`Are you sure you want to delete the folder "${folderName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await api.delete(`/folders/${folderId}`);
      setFolders(folders.filter(folder => folder.id !== folderId));
    } catch (error) {
      console.error('Error deleting folder:', error);
      alert('Failed to delete folder');
    }
  };

  const startEditing = (folder) => {
    setEditingFolder(folder.id);
    setNewFolderName(folder.name);
  };

  const cancelEditing = () => {
    setEditingFolder(null);
    setNewFolderName('');
    setError('');
  };

  const handleUpdateFolder = async (folderId) => {
    if (!newFolderName.trim()) {
      setError('Folder name is required');
      return;
    }

    try {
      const response = await api.put(`/folders/${folderId}`, {
        name: newFolderName.trim()
      });
      
      if (response.data) {
        setFolders(folders.map(folder => 
          folder.id === folderId ? response.data : folder
        ));
        setEditingFolder(null);
        setNewFolderName('');
        setError('');
      }
    } catch (error) {
      console.error('Error updating folder:', error);
      setError(error.response?.data?.detail || 'Failed to update folder');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading folders...</p>
      </div>
    );
  }

  return (
    <div className="folder-manager">
      <div className="page-header">
        <h1>Folder Management</h1>
        <p>Organize your responses into folders</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Your Folders</h2>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn btn-primary"
          >
            <Plus size={16} />
            Create Folder
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {showCreateForm && (
          <div className="create-form">
            <form onSubmit={handleCreateFolder}>
              <div className="form-row">
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="Enter folder name"
                  className="form-control"
                  autoFocus
                />
                <button type="submit" className="btn btn-primary">
                  <Save size={16} />
                  Create
                </button>
                <button 
                  type="button" 
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewFolderName('');
                    setError('');
                  }}
                  className="btn btn-secondary"
                >
                  <X size={16} />
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="folders-list">
          {folders.length > 0 ? (
            folders.map((folder) => (
              <div key={folder.id} className="folder-item">
                <div className="folder-icon">
                  <Folder size={24} />
                </div>
                
                <div className="folder-content">
                  {editingFolder === folder.id ? (
                    <div className="edit-form">
                      <input
                        type="text"
                        value={newFolderName}
                        onChange={(e) => setNewFolderName(e.target.value)}
                        className="form-control"
                        autoFocus
                      />
                    </div>
                  ) : (
                    <div className="folder-info">
                      <h3>{folder.name}</h3>
                      <p>Created: {formatDate(folder.created_at)}</p>
                    </div>
                  )}
                </div>
                
                <div className="folder-actions">
                  {editingFolder === folder.id ? (
                    <>
                      <button
                        onClick={() => handleUpdateFolder(folder.id)}
                        className="btn btn-primary btn-sm"
                      >
                        <Save size={16} />
                        Save
                      </button>
                      <button
                        onClick={cancelEditing}
                        className="btn btn-secondary btn-sm"
                      >
                        <X size={16} />
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => startEditing(folder)}
                        className="btn btn-secondary btn-sm"
                      >
                        <Edit size={16} />
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteFolder(folder.id, folder.name)}
                        className="btn btn-danger btn-sm"
                      >
                        <Trash2 size={16} />
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <FolderOpen size={48} />
              <h3>No folders yet</h3>
              <p>Create your first folder to organize your responses</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="btn btn-primary"
              >
                <Plus size={16} />
                Create First Folder
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Folder Tips</h2>
          <p>Best practices for organizing your responses</p>
        </div>
        
        <div className="tips-list">
          <div className="tip-item">
            <h4>Organize by Project</h4>
            <p>Create folders for different projects or clients to keep responses organized</p>
          </div>
          
          <div className="tip-item">
            <h4>Use Descriptive Names</h4>
            <p>Choose clear, descriptive names that make it easy to find what you're looking for</p>
          </div>
          
          <div className="tip-item">
            <h4>Regular Cleanup</h4>
            <p>Periodically review and clean up folders that are no longer needed</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FolderManager; 