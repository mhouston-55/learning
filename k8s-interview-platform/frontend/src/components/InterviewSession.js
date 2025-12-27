import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';
import './InterviewSession.css';

function InterviewSession() {
  const { sessionId } = useParams();
  const terminalRef = useRef(null);
  const terminal = useRef(null);
  const ws = useRef(null);
  const fitAddon = useRef(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    initTerminal();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (terminal.current) {
        terminal.current.dispose();
      }
    };
  }, [sessionId]);

  const initTerminal = () => {
    // Initialize xterm.js
    terminal.current = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#d4d4d4',
        black: '#000000',
        red: '#cd3131',
        green: '#0dbc79',
        yellow: '#e5e510',
        blue: '#2472c8',
        magenta: '#bc3fbc',
        cyan: '#11a8cd',
        white: '#e5e5e5',
        brightBlack: '#666666',
        brightRed: '#f14c4c',
        brightGreen: '#23d18b',
        brightYellow: '#f5f543',
        brightBlue: '#3b8eea',
        brightMagenta: '#d670d6',
        brightCyan: '#29b8db',
        brightWhite: '#e5e5e5'
      },
      rows: 30,
      cols: 100
    });

    fitAddon.current = new FitAddon();
    terminal.current.loadAddon(fitAddon.current);
    terminal.current.loadAddon(new WebLinksAddon());

    terminal.current.open(terminalRef.current);
    fitAddon.current.fit();

    // Connect to WebSocket
    connectWebSocket();

    // Handle window resize
    const handleResize = () => {
      if (fitAddon.current) {
        fitAddon.current.fit();
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  };

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:3001/terminal?session=${sessionId}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setConnected(true);
      setError('');

      // Send input from terminal to server
      terminal.current.onData((data) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(data);
        }
      });
    };

    ws.current.onmessage = (event) => {
      terminal.current.write(event.data);
    };

    ws.current.onerror = (err) => {
      setError('WebSocket connection error');
      console.error('WebSocket error:', err);
    };

    ws.current.onclose = () => {
      setConnected(false);
      terminal.current.write('\r\n\n\x1b[31mConnection closed\x1b[0m\r\n');
    };
  };

  return (
    <div className="interview-session">
      <div className="terminal-header">
        <div className="header-content">
          <h1>Kubernetes Interview Session</h1>
          <div className="connection-status">
            {connected ? (
              <span className="status-connected">● Connected</span>
            ) : (
              <span className="status-disconnected">● Disconnected</span>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <div className="terminal-container">
        <div className="terminal-wrapper" ref={terminalRef}></div>
      </div>

      <div className="help-panel">
        <h3>Quick Reference</h3>
        <div className="command-list">
          <code>kubectl get pods</code>
          <code>kubectl describe pod &lt;name&gt;</code>
          <code>kubectl logs &lt;pod-name&gt;</code>
          <code>kubectl get events --sort-by='.lastTimestamp'</code>
          <code>helm list</code>
        </div>
      </div>
    </div>
  );
}

export default InterviewSession;
