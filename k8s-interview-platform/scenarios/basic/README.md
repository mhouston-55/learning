# Basic Troubleshooting Scenario

## Challenge

You've been given access to a Kubernetes namespace with a deployment that isn't working correctly.

### Tasks:

1. **Find the CrashLooping Pod**
   - Identify which pod is failing
   - Determine why it's crashing
   - Fix the issue

2. **Fix the Failed Deployment**
   - The `web-app` deployment has issues
   - Check events and logs
   - Make it healthy

3. **Verify the Service**
   - Ensure the service is properly configured
   - Check endpoints

## Expected Outcome

- All pods should be in `Running` state
- All deployments should have desired replicas ready
- Services should have healthy endpoints

## Time Estimate

15-20 minutes
