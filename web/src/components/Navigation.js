import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FileText, 
  Folder, 
  Upload, 
  LogOut, 
  User 
} from 'lucide-react';

const Navigation = ({ user, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/responses', icon: FileText, label: 'Responses' },
    { path: '/folders', icon: Folder, label: 'Folders' },
    { path: '/upload', icon: Upload, label: 'Upload' },
  ];

  return (
    <nav className="navigation">
      <div className="nav-header">
        <h1>ScreenshotOCR</h1>
        <p>AI Analysis System</p>
      </div>

      <div className="nav-menu">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              {item.label}
            </Link>
          );
        })}
      </div>

      <div className="nav-footer">
        <div className="user-info">
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <User size={16} style={{ marginRight: '8px' }} />
            <span>{user?.username || 'User'}</span>
          </div>
        </div>
        
        <button
          onClick={onLogout}
          className="logout-button"
        >
          <LogOut size={16} style={{ marginRight: '6px' }} />
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navigation; 