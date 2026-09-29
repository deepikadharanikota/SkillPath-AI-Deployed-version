import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  handleGoHome = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.navigate) {
      this.props.navigate('/dashboard');
    } else {
      window.history.pushState({}, '', '/dashboard');
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '60vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <div className="glass-card" style={{ maxWidth: '520px', padding: '2.5rem', borderRadius: '16px' }}>
            <AlertTriangle size={48} color="#f59e0b" style={{ margin: '0 auto 1rem' }} />
            <h2 style={{ fontSize: '1.4rem', marginBottom: '8px', color: '#fff' }}>Something went wrong</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              {this.state.error?.message || 'An unexpected rendering error occurred.'}
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={this.handleRetry} className="btn-primary">
                <RefreshCw size={16} />
                <span>Try Again</span>
              </button>
              <button onClick={this.handleGoHome} className="btn-secondary">
                <Home size={16} />
                <span>Return to Dashboard</span>
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
