# Helm Troubleshooting Scenario

## Challenge

A Helm release has been deployed but isn't working correctly. You need to debug and fix the issues.

### Tasks:

1. **Investigate the Helm Release**
   - List all Helm releases
   - Check the status of the `my-app` release
   - Identify what's wrong

2. **Fix Values Issues**
   - The release has incorrect configuration values
   - Review the current values
   - Update with correct values

3. **Upgrade the Release**
   - Apply fixes using `helm upgrade`
   - Verify the release is healthy

## Expected Outcome

- Understand Helm release management
- Know how to inspect and debug Helm deployments
- Successfully upgrade a failing release

## Time Estimate

25-30 minutes

## Provided Helm Chart

A simple Helm chart is available at `/tmp/my-app-chart` with the following structure:
- Chart.yaml
- values.yaml
- templates/deployment.yaml
- templates/service.yaml
