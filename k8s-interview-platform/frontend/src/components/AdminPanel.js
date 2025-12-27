import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AdminPanel() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('basic');
  const [sessionUrl, setSessionUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      const response = await axios.get('/api/scenarios');
      setScenarios(response.data.scenarios);
    } catch (err) {
      setError('Failed to load scenarios');
    }
  };

  const createSession = async () => {
    setLoading(true);
    setError('');
    setSessionUrl('');

    try {
      const response = await axios.post('/api/session/create', {
        scenario: selectedScenario
      });

      const fullUrl = `${window.location.origin}/interview/${response.data.sessionId}`;
      setSessionUrl(fullUrl);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create session');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(sessionUrl);
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🎯 Kubernetes Interview Platform</h1>
        <p>Create interactive Kubernetes challenges for your candidates</p>
      </div>

      <div className="card">
        <h2>Create New Interview Session</h2>

        <div className="input-group">
          <label>Select Scenario</label>
          <div className="scenario-grid">
            {scenarios.map((scenario) => (
              <div
                key={scenario.id}
                className={`scenario-card ${selectedScenario === scenario.id ? 'selected' : ''}`}
                onClick={() => setSelectedScenario(scenario.id)}
              >
                <h3>{scenario.name}</h3>
                <p>{scenario.description}</p>
                <span className={`difficulty-badge difficulty-${scenario.difficulty}`}>
                  {scenario.difficulty}
                </span>
              </div>
            ))}
          </div>
        </div>

        <button
          className="button"
          onClick={createSession}
          disabled={loading}
        >
          {loading ? 'Creating Session...' : 'Create Interview Link'}
        </button>

        {sessionUrl && (
          <div className="link-box">
            <input
              type="text"
              value={sessionUrl}
              readOnly
            />
            <button className="button button-secondary" onClick={copyToClipboard}>
              Copy Link
            </button>
          </div>
        )}

        {error && (
          <div className="error">
            {error}
          </div>
        )}
      </div>

      <div className="card">
        <h2>How to Use</h2>
        <ol style={{ color: '#cccccc', lineHeight: '1.8', paddingLeft: '20px' }}>
          <li>Select a scenario that matches the interview level</li>
          <li>Click "Create Interview Link" to generate a unique session</li>
          <li>Send the generated link to your candidate</li>
          <li>The candidate will have access to a Kubernetes environment with kubectl</li>
          <li>Sessions automatically expire after 2 hours</li>
        </ol>
      </div>
    </div>
  );
}

export default AdminPanel;
