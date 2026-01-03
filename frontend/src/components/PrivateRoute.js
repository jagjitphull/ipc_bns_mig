import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * PrivateRoute component to protect routes requiring authentication
 * Redirects to login if user is not authenticated
 */
function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '400px',
        fontSize: '1.2rem',
        color: '#5a6c7d'
      }}>
        <div>
          <div style={{ textAlign: 'center', marginBottom: '1rem' }}>🔐</div>
          <div>Verifying authentication...</div>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Render protected content if authenticated
  return children;
}

export default PrivateRoute;
