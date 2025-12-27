const express = require('express');
const cors = require('cors');
const { WebSocketServer } = require('ws');
const http = require('http');
const { v4: uuidv4 } = require('uuid');
const K8sManager = require('./k8s-manager');
const TerminalManager = require('./terminal-manager');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

app.use(cors());
app.use(express.json());

const k8sManager = new K8sManager();
const terminalManager = new TerminalManager(k8sManager);

// Store active sessions
const sessions = new Map();

// Create a new interview session
app.post('/api/session/create', async (req, res) => {
  try {
    const sessionId = uuidv4();
    const { scenario = 'basic' } = req.body;

    console.log(`Creating session ${sessionId} with scenario ${scenario}`);

    // Create namespace and deploy scenario
    await k8sManager.createNamespace(sessionId);
    await k8sManager.deployScenario(sessionId, scenario);

    sessions.set(sessionId, {
      id: sessionId,
      scenario,
      createdAt: new Date(),
      status: 'active'
    });

    res.json({
      sessionId,
      url: `/interview/${sessionId}`,
      expiresIn: 7200 // 2 hours
    });
  } catch (error) {
    console.error('Error creating session:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get session info
app.get('/api/session/:sessionId', async (req, res) => {
  const { sessionId } = req.params;
  const session = sessions.get(sessionId);

  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  try {
    const resources = await k8sManager.getNamespaceResources(sessionId);
    res.json({
      ...session,
      resources
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// List available scenarios
app.get('/api/scenarios', (req, res) => {
  res.json({
    scenarios: [
      {
        id: 'basic',
        name: 'Basic Troubleshooting',
        description: 'Fix CrashLooping pods and failed deployments',
        difficulty: 'beginner'
      },
      {
        id: 'logs',
        name: 'Log Analysis',
        description: 'Debug applications by analyzing logs',
        difficulty: 'beginner'
      },
      {
        id: 'helm',
        name: 'Helm Deployment',
        description: 'Troubleshoot and fix a broken Helm release',
        difficulty: 'intermediate'
      },
      {
        id: 'advanced',
        name: 'Multi-service Debugging',
        description: 'Debug a complex microservices deployment',
        difficulty: 'advanced'
      }
    ]
  });
});

// Cleanup session
app.delete('/api/session/:sessionId', async (req, res) => {
  const { sessionId } = req.params;

  try {
    await k8sManager.deleteNamespace(sessionId);
    sessions.delete(sessionId);
    res.json({ message: 'Session cleaned up' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// WebSocket for terminal
wss.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const sessionId = url.searchParams.get('session');

  if (!sessionId || !sessions.has(sessionId)) {
    ws.close(1008, 'Invalid session');
    return;
  }

  console.log(`Terminal connected for session ${sessionId}`);

  const terminal = terminalManager.createTerminal(sessionId, ws);

  ws.on('message', (data) => {
    terminal.write(data);
  });

  ws.on('close', () => {
    console.log(`Terminal disconnected for session ${sessionId}`);
    terminal.kill();
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`K8s Interview Platform API running on port ${PORT}`);
});

// Cleanup old sessions every hour
setInterval(() => {
  const now = Date.now();
  for (const [sessionId, session] of sessions.entries()) {
    const age = now - session.createdAt.getTime();
    if (age > 2 * 60 * 60 * 1000) { // 2 hours
      console.log(`Cleaning up expired session ${sessionId}`);
      k8sManager.deleteNamespace(sessionId).catch(console.error);
      sessions.delete(sessionId);
    }
  }
}, 60 * 60 * 1000);
