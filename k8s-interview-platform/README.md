# Kubernetes Interview Platform

A web-based platform for conducting technical Kubernetes interviews. Send candidates a link, and they'll get access to a real Kubernetes environment with pre-configured challenges to test their troubleshooting, log analysis, and Helm skills.

## Features

- **Web-Based Terminal**: Candidates interact with kubectl through a browser-based terminal
- **Isolated Namespaces**: Each interview session gets its own Kubernetes namespace
- **Pre-Built Scenarios**: Multiple difficulty levels (beginner to advanced)
- **Auto-Cleanup**: Sessions automatically expire after 2 hours
- **Real Kubernetes**: Not a simulation - actual kubectl commands on real resources

## Quick Start

### Option 1: Docker Compose (Easiest)

**Prerequisites:**
- Docker and Docker Compose
- Access to a Kubernetes cluster
- kubectl configured with cluster access

```bash
# Clone the repository
git clone <your-repo>
cd k8s-interview-platform

# Start the platform
docker-compose up -d

# Access the admin panel
open http://localhost:3000
```

### Option 2: Deploy to Kubernetes

**Prerequisites:**
- Kubernetes cluster (v1.24+)
- kubectl configured
- Ingress controller (nginx recommended)

```bash
# Create namespace and RBAC
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/rbac.yaml

# Build and push images (update registry in deployment files)
docker build -t your-registry/k8s-interview-backend:latest ./backend
docker build -t your-registry/k8s-interview-frontend:latest ./frontend
docker push your-registry/k8s-interview-backend:latest
docker push your-registry/k8s-interview-frontend:latest

# Deploy application
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/ingress.yaml
```

### Option 3: Local Development

```bash
# Terminal 1: Start backend
cd backend
npm install
npm start

# Terminal 2: Start frontend
cd frontend
npm install
npm start

# Access at http://localhost:3000
```

## Using the Platform

### For Interviewers

1. **Navigate to the admin panel** (http://your-domain.com)

2. **Select a scenario:**
   - **Basic Troubleshooting**: Fix CrashLooping pods and failed deployments
   - **Log Analysis**: Debug applications by analyzing logs
   - **Helm Deployment**: Troubleshoot and fix a broken Helm release
   - **Advanced Multi-Service**: Debug complex microservices issues

3. **Create interview link** - Click "Create Interview Link"

4. **Send link to candidate** - Copy and send the generated URL

5. **Monitor (optional)** - You can observe their namespace with:
   ```bash
   kubectl get pods -n interview-<session-id>
   ```

### For Candidates

1. **Open the interview link** sent by your interviewer

2. **Read the scenario** - Type `cat README.md` or check the scenario description

3. **Use kubectl commands** to investigate and fix issues:
   ```bash
   kubectl get pods
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   kubectl get events
   ```

4. **Test your fixes** to ensure everything is working

## Available Scenarios

### Basic Troubleshooting (Beginner)
- **Duration**: 15-20 minutes
- **Tests**: Pod debugging, deployment fixes, service configuration
- **Skills**: kubectl basics, reading pod status, understanding errors

### Log Analysis (Beginner)
- **Duration**: 20-25 minutes
- **Tests**: Reading logs, init containers, multi-container pods
- **Skills**: kubectl logs, container-specific logs, log interpretation

### Helm Troubleshooting (Intermediate)
- **Duration**: 25-30 minutes
- **Tests**: Helm release debugging, values configuration
- **Skills**: helm commands, chart debugging, release management

### Advanced Multi-Service (Advanced)
- **Duration**: 45-60 minutes
- **Tests**: Microservices debugging, resource management, configuration
- **Skills**: Service networking, ConfigMaps, Secrets, health probes

## Architecture

```
┌─────────────┐
│  Frontend   │  React + xterm.js
│  (Port 3000)│  Terminal emulator
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Backend    │  Node.js + Express
│  (Port 3001)│  Session management
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│    Kubernetes Cluster           │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Namespace: interview-   │   │
│  │          abc123         │   │
│  │                         │   │
│  │  - Broken pods          │   │
│  │  - Failed deployments   │   │
│  │  - Misconfigured svcs   │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

## Configuration

### Environment Variables

**Backend:**
- `PORT`: API server port (default: 3001)
- `NODE_ENV`: Environment (production/development)

**Frontend:**
- Built-time configuration in `package.json`

### Kubernetes Access

The backend needs access to your Kubernetes cluster. This can be configured:

1. **In-cluster**: Deploy to K8s, uses ServiceAccount
2. **Local kubeconfig**: Mount `~/.kube/config`
3. **Custom**: Set `KUBECONFIG` environment variable

## Session Management

- **Session Duration**: 2 hours (configurable in `server.js`)
- **Cleanup**: Automatic namespace deletion after expiry
- **Isolation**: Each session gets a unique namespace

## Security Considerations

### Production Deployment

1. **Enable authentication** - Add auth middleware to protect admin routes
2. **Rate limiting** - Prevent session spam
3. **Resource quotas** - Limit resources per namespace:
   ```yaml
   apiVersion: v1
   kind: ResourceQuota
   metadata:
     name: interview-quota
   spec:
     hard:
       requests.cpu: "2"
       requests.memory: 4Gi
       pods: "10"
   ```
4. **Network policies** - Isolate interview namespaces
5. **TLS/HTTPS** - Use ingress with TLS certificates
6. **RBAC restrictions** - Limit what candidates can do

### Recommended RBAC for Interview Namespaces

Create a Role that candidates can't escape their namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: interview-role
rules:
- apiGroups: ["", "apps"]
  resources: ["pods", "deployments", "services", "configmaps"]
  verbs: ["get", "list", "describe", "logs"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]  # Only if you want to allow exec
```

## Customization

### Adding New Scenarios

1. Create a new directory: `scenarios/your-scenario-name/`

2. Add Kubernetes YAML files with intentional issues

3. Create a `README.md` explaining the challenge

4. Update `server.js` to include the new scenario:
   ```javascript
   {
     id: 'your-scenario',
     name: 'Your Scenario Name',
     description: 'What candidates will debug',
     difficulty: 'intermediate'
   }
   ```

### Modifying Existing Scenarios

Edit YAML files in `scenarios/` directory. Common patterns:

- **Wrong image tags**: `image: nginx:invalid-tag`
- **Incorrect env vars**: Wrong hostnames, ports
- **Resource limits**: Too low memory/CPU causing OOMKill
- **Missing volumes**: ConfigMaps not mounted
- **Wrong secrets**: Invalid secret keys
- **Bad probes**: Health checks on wrong ports

## Troubleshooting

### Backend can't connect to Kubernetes

```bash
# Check kubeconfig
kubectl cluster-info

# Verify backend has access
docker-compose logs backend
```

### WebSocket connection fails

- Check firewall rules for port 3001
- Verify proxy configuration (nginx.conf)
- Check browser console for errors

### Sessions not cleaning up

```bash
# Manually cleanup
kubectl get namespaces | grep interview-
kubectl delete namespace interview-<session-id>
```

### Pods not starting in interview namespace

```bash
# Check events
kubectl get events -n interview-<session-id> --sort-by='.lastTimestamp'

# Check resource availability
kubectl describe nodes
```

## Development

### Project Structure

```
k8s-interview-platform/
├── backend/              # Node.js API
│   ├── server.js         # Main server
│   ├── k8s-manager.js    # Kubernetes operations
│   └── terminal-manager.js # PTY/WebSocket handling
├── frontend/             # React app
│   └── src/
│       ├── components/
│       │   ├── AdminPanel.js      # Create sessions
│       │   └── InterviewSession.js # Terminal interface
│       └── App.js
├── scenarios/            # Interview challenges
│   ├── basic/
│   ├── logs/
│   ├── helm/
│   └── advanced/
├── kubernetes/           # K8s deployment manifests
└── docker-compose.yml    # Local deployment
```

### Running Tests

```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional scenarios (statefulsets, persistent volumes, networking)
- [ ] Built-in scoring/evaluation system
- [ ] Recording/playback of sessions
- [ ] Multi-language support
- [ ] Integration with ATS systems

## License

MIT License - feel free to use for your hiring process!

## Support

For issues or questions:
- Open a GitHub issue
- Check the troubleshooting section
- Review server logs: `docker-compose logs -f`

## Credits

Built with:
- [xterm.js](https://xtermjs.org/) - Terminal emulator
- [node-pty](https://github.com/microsoft/node-pty) - Pseudoterminal
- [@kubernetes/client-node](https://github.com/kubernetes-client/javascript) - K8s client
- [React](https://react.dev/) - Frontend framework
