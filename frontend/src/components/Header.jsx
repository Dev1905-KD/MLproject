import React from 'react';
import { GraduationCap, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Header({ status }) {
  const isHealthy = status?.status === 'healthy' && status?.artifacts?.model;

  return (
    <header className="header glass-card">
      <div className="brand">
        <div className="brand-icon">
          <GraduationCap size={26} />
        </div>
        <div className="brand-text">
          <h1>EduPredict AI</h1>
          <p>Student Math Score Intelligence & Analytics Platform</p>
        </div>
      </div>
      <div className={`status-badge ${isHealthy ? '' : 'error'}`}>
        <div className="status-dot"></div>
        {isHealthy ? (
          <>
            <CheckCircle2 size={16} /> API Online
          </>
        ) : (
          <>
            <AlertCircle size={16} /> Service Connecting...
          </>
        )}
      </div>
    </header>
  );
}
