const pty = require('node-pty');
const os = require('os');

class TerminalManager {
  constructor(k8sManager) {
    this.k8sManager = k8sManager;
    this.terminals = new Map();
  }

  createTerminal(sessionId, ws) {
    const namespace = `interview-${sessionId}`;
    const shell = os.platform() === 'win32' ? 'powershell.exe' : 'bash';

    // Create a PTY with kubectl context set to the session namespace
    const ptyProcess = pty.spawn(shell, [], {
      name: 'xterm-color',
      cols: 80,
      rows: 30,
      cwd: process.env.HOME,
      env: {
        ...process.env,
        KUBECTL_NAMESPACE: namespace,
        PS1: `interview-${sessionId.substring(0, 8)}> `
      }
    });

    // Send welcome message
    const welcomeMsg = `
╔════════════════════════════════════════════════════════════╗
║        Kubernetes Interview Environment                    ║
║        Session: ${sessionId.substring(0, 8)}                              ║
╚════════════════════════════════════════════════════════════╝

Your namespace: ${namespace}

Available commands:
  kubectl get pods                    - List all pods
  kubectl get deployments             - List deployments
  kubectl logs <pod-name>             - View pod logs
  kubectl describe pod <pod-name>     - Describe a pod
  kubectl get events                  - View recent events
  helm list                           - List Helm releases

Tips:
  - All kubectl commands are scoped to your namespace
  - Type 'scenario' to see your current challenge
  - Type 'hint' if you need help

Ready to start! Type your commands below:
\r\n`;

    ws.send(welcomeMsg);

    // Set default namespace for kubectl
    ptyProcess.write(`export KUBECONFIG=/tmp/kubeconfig-${sessionId}\r`);
    ptyProcess.write(`alias kubectl='kubectl -n ${namespace}'\r`);
    ptyProcess.write(`clear\r`);

    // Forward terminal output to WebSocket
    ptyProcess.onData((data) => {
      try {
        ws.send(data);
      } catch (error) {
        console.error('Error sending terminal data:', error);
      }
    });

    // Forward WebSocket input to terminal
    const writeToTerminal = (data) => {
      try {
        ptyProcess.write(data);
      } catch (error) {
        console.error('Error writing to terminal:', error);
      }
    };

    ptyProcess.onExit(() => {
      this.terminals.delete(sessionId);
      ws.close();
    });

    this.terminals.set(sessionId, ptyProcess);

    return {
      write: writeToTerminal,
      kill: () => {
        ptyProcess.kill();
        this.terminals.delete(sessionId);
      }
    };
  }

  getTerminal(sessionId) {
    return this.terminals.get(sessionId);
  }
}

module.exports = TerminalManager;
