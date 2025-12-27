# Advanced Multi-Service Debugging

## Challenge

A microservices application is deployed but experiencing multiple issues across different components.

### Architecture

- Frontend (nginx) → API Gateway → Backend Service → Database
- Redis cache (sidecar)
- Ingress for external access

### Tasks:

1. **Service Communication Issues**
   - Frontend can't reach the API
   - Debug service discovery
   - Fix networking issues

2. **Resource Constraints**
   - Some pods are being OOMKilled
   - Others are CPU throttled
   - Adjust resource limits appropriately

3. **ConfigMap and Secrets**
   - Application config is incorrect
   - Secrets are not mounted properly
   - Fix configuration management

4. **Health Checks**
   - Liveness and readiness probes are misconfigured
   - Pods are restarting unnecessarily
   - Configure proper health checks

## Expected Outcome

- All services communicating properly
- No resource-related crashes
- Proper configuration loaded
- Stable, healthy application

## Time Estimate

45-60 minutes
