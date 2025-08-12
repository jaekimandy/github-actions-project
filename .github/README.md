# GitHub Actions for Local Kubernetes Deployment

This workflow deploys your application to a local Docker Desktop Kubernetes cluster instead of AWS.

## Prerequisites

1. **Docker Desktop with Kubernetes enabled**
   - Install Docker Desktop for Windows
   - Enable Kubernetes in Docker Desktop settings
   - Ensure kubectl is configured to use Docker Desktop

2. **GitHub Secrets Setup**
   You need to configure the following secrets in your GitHub repository:

   - `DOCKER_DESKTOP_KUBECONFIG`: Your local kubeconfig content
   - `SECRET_KEY`: A secret key for your Flask application
   - `DB_PASSWORD`: Database password (if applicable)

## Setting up the DOCKER_DESKTOP_KUBECONFIG Secret

1. **Get your local kubeconfig:**
   ```bash
   # On Windows, the kubeconfig is typically located at:
   type %USERPROFILE%\.kube\config
   
   # Or if using PowerShell:
   Get-Content $env:USERPROFILE\.kube\config
   ```

2. **Copy the entire output** and add it as a GitHub secret named `DOCKER_DESKTOP_KUBECONFIG`

## How the Workflow Works

1. **Test Stage**: Runs your application tests
2. **Build Stage**: Builds and pushes Docker image to GitHub Container Registry
3. **Deploy Stage**: Deploys to your local Kubernetes cluster
4. **Notify Stage**: Provides deployment status and access information

## Workflow Triggers

- Push to `main` or `develop` branches
- Pull requests to `main` branch
- Manual workflow dispatch

## Accessing Your Application

After successful deployment:

1. **Check deployment status:**
   ```bash
   kubectl get pods -n production
   kubectl get services -n production
   ```

2. **Port forward to access the application:**
   ```bash
   kubectl port-forward -n production svc/devops-demo-service 8000:8000
   ```

3. **Access your application at:** `http://localhost:8000`

## Troubleshooting

### Common Issues

1. **Kubeconfig not found:**
   - Ensure Docker Desktop Kubernetes is running
   - Verify the kubeconfig secret is properly set

2. **Image pull errors:**
   - Check if the Docker image was built and pushed successfully
   - Verify GitHub Container Registry permissions

3. **Pod startup issues:**
   - Check pod logs: `kubectl logs -n production <pod-name>`
   - Verify resource limits and requests

### Useful Commands

```bash
# Check all resources in production namespace
kubectl get all -n production

# View detailed pod information
kubectl describe pod -n production <pod-name>

# View application logs
kubectl logs -n production -l app=devops-demo

# Delete and recreate deployment
kubectl delete deployment devops-demo-app -n production
kubectl apply -f k8s/production/deployment.yaml

# Check service endpoints
kubectl get endpoints -n production
```

## Security Notes

- The workflow runs with minimal permissions
- Secrets are stored securely in GitHub
- The application runs as a non-root user
- Resource limits are enforced to prevent resource exhaustion

## Customization

You can customize the workflow by:

1. **Modifying resource limits** in `k8s/production/deployment.yaml`
2. **Adding environment variables** in `k8s/production/configmap.yaml`
3. **Changing the service type** in `k8s/production/service.yaml`
4. **Adding ingress rules** for external access

## Monitoring

The deployment includes:
- Health checks (liveness, readiness, startup probes)
- Prometheus metrics endpoints
- Structured logging
- Resource monitoring 