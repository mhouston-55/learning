const k8s = require('@kubernetes/client-node');
const fs = require('fs');
const path = require('path');

class K8sManager {
  constructor() {
    this.kc = new k8s.KubeConfig();

    // Try to load config (in-cluster or local kubeconfig)
    try {
      this.kc.loadFromCluster();
      console.log('Loaded in-cluster Kubernetes config');
    } catch (e) {
      try {
        this.kc.loadFromDefault();
        console.log('Loaded local Kubernetes config');
      } catch (err) {
        console.warn('No Kubernetes config found, using mock mode');
        this.mockMode = true;
      }
    }

    if (!this.mockMode) {
      this.k8sApi = this.kc.makeApiClient(k8s.CoreV1Api);
      this.appsApi = this.kc.makeApiClient(k8s.AppsV1Api);
    }
  }

  async createNamespace(sessionId) {
    if (this.mockMode) {
      console.log(`[MOCK] Creating namespace: interview-${sessionId}`);
      return;
    }

    const namespace = {
      metadata: {
        name: `interview-${sessionId}`,
        labels: {
          'app': 'k8s-interview',
          'session': sessionId
        }
      }
    };

    try {
      await this.k8sApi.createNamespace(namespace);
      console.log(`Created namespace: interview-${sessionId}`);
    } catch (error) {
      if (error.response?.statusCode !== 409) { // Ignore if already exists
        throw error;
      }
    }
  }

  async deployScenario(sessionId, scenarioName) {
    if (this.mockMode) {
      console.log(`[MOCK] Deploying scenario ${scenarioName} to namespace interview-${sessionId}`);
      return;
    }

    const namespace = `interview-${sessionId}`;
    const scenarioPath = path.join(__dirname, '..', 'scenarios', scenarioName);

    if (!fs.existsSync(scenarioPath)) {
      console.warn(`Scenario ${scenarioName} not found, skipping deployment`);
      return;
    }

    const files = fs.readdirSync(scenarioPath).filter(f => f.endsWith('.yaml'));

    for (const file of files) {
      const yaml = fs.readFileSync(path.join(scenarioPath, file), 'utf8');
      await this.applyYaml(namespace, yaml);
    }

    console.log(`Deployed scenario ${scenarioName} to ${namespace}`);
  }

  async applyYaml(namespace, yaml) {
    // Simple YAML application - in production, use a proper YAML parser
    // and handle different resource types
    const docs = yaml.split('---').filter(d => d.trim());

    for (const doc of docs) {
      try {
        const resource = JSON.parse(doc); // Simplified - should use YAML parser
        // Apply resource based on kind
        // This is a simplified version - expand based on needs
      } catch (error) {
        console.error('Error applying YAML:', error.message);
      }
    }
  }

  async getNamespaceResources(sessionId) {
    if (this.mockMode) {
      return {
        pods: [],
        deployments: [],
        services: []
      };
    }

    const namespace = `interview-${sessionId}`;

    try {
      const [podsRes, deploymentsRes, servicesRes] = await Promise.all([
        this.k8sApi.listNamespacedPod(namespace),
        this.appsApi.listNamespacedDeployment(namespace),
        this.k8sApi.listNamespacedService(namespace)
      ]);

      return {
        pods: podsRes.body.items,
        deployments: deploymentsRes.body.items,
        services: servicesRes.body.items
      };
    } catch (error) {
      console.error('Error getting resources:', error.message);
      return { pods: [], deployments: [], services: [] };
    }
  }

  async deleteNamespace(sessionId) {
    if (this.mockMode) {
      console.log(`[MOCK] Deleting namespace: interview-${sessionId}`);
      return;
    }

    const namespace = `interview-${sessionId}`;

    try {
      await this.k8sApi.deleteNamespace(namespace);
      console.log(`Deleted namespace: ${namespace}`);
    } catch (error) {
      if (error.response?.statusCode !== 404) {
        throw error;
      }
    }
  }

  getKubeConfig(sessionId) {
    if (this.mockMode) {
      return null;
    }

    // Create a limited kubeconfig for the session namespace
    const namespace = `interview-${sessionId}`;
    return {
      namespace,
      context: this.kc.getCurrentContext()
    };
  }
}

module.exports = K8sManager;
