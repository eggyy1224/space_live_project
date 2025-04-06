import React, { Component, ErrorInfo, ReactNode } from 'react';
import logger, { LogCategory } from '../utils/LogManager';

interface Props {
  children: ReactNode;
  fallback?: ReactNode; // Optional fallback UI component
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error, errorInfo: null }; // Reset errorInfo here
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to our logger
    logger.error('捕獲到渲染錯誤:', LogCategory.GENERAL, {
      message: error.message,
      componentStack: errorInfo.componentStack,
      errorObject: error, // Include the full error object
    });

    // Also update state with errorInfo for potential display or further processing
    // Note: getDerivedStateFromError runs first, then componentDidCatch
    this.setState({ errorInfo });
  }

  public render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      // Default fallback UI
      return (
        <div style={styles.container}>
          <h1 style={styles.title}>糟糕！發生了一些錯誤。</h1>
          <p style={styles.message}>我們已經記錄了這個問題，正在努力修復它。</p>
          {/* Optionally display error details in development */}
          {import.meta.env.DEV && this.state.error && (
            <details style={styles.details}>
              <summary>錯誤詳情</summary>
              <pre style={styles.pre}>
                {this.state.error.toString()}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    padding: '20px',
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
    textAlign: 'center' as 'center',
  },
  title: {
    color: '#ff4d4d',
    marginBottom: '15px',
  },
  message: {
    fontSize: '1.1em',
    marginBottom: '20px',
  },
  details: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    borderRadius: '5px',
    width: '80%',
    maxWidth: '600px',
    textAlign: 'left' as 'left',
  },
  pre: {
    whiteSpace: 'pre-wrap' as 'pre-wrap',
    wordWrap: 'break-word' as 'break-word',
    fontSize: '0.9em',
    color: '#ccc',
    maxHeight: '300px',
    overflowY: 'auto' as 'auto',
  },
};

export default ErrorBoundary; 