import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

import { Component, type ErrorInfo, type ReactNode } from 'react';

// --- DEBUGGING UTILITIES ---
// Capture global errors and display them on screen
window.onerror = function (message, source, lineno, colno, error) {
  const div = document.createElement('div');
  div.style.cssText = 'position:fixed;top:0;left:0;width:100%;z-index:99999;background:red;color:white;padding:20px;font-family:monospace;white-space:pre-wrap;';
  div.textContent = `GLOBAL ERROR: ${message}\nAt: ${source}:${lineno}:${colno}\nStack: ${error?.stack}`;
  document.body.appendChild(div);
};

window.addEventListener('unhandledrejection', (event) => {
  const div = document.createElement('div');
  div.style.cssText = 'position:fixed;bottom:0;left:0;width:100%;z-index:99999;background:darkred;color:white;padding:20px;font-family:monospace;white-space:pre-wrap;';
  div.textContent = `UNHANDLED PROMISE: ${event.reason}`;
  document.body.appendChild(div);
});
// ---------------------------

class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: Error | null }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: 'red', fontFamily: 'sans-serif' }}>
          <h1>Something went wrong.</h1>
          <pre>{this.state.error?.toString()}</pre>
          <pre>{this.state.error?.stack}</pre>
        </div>
      );
    }

    return this.props.children;
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </BrowserRouter>
  </StrictMode>,
)
