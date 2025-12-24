# CROSSFIRE Production Deployment Guide

## Deployment Configuration

### Google Cloud Platform Setup

**Project**: aipodcaster-481909  
**Region**: us-central1  
**Services Required**:
- Agent Engine (for managed agent deployment)
- Cloud Run (for FastAPI backend)
- Cloud Trace (for observability)
- Cloud Monitoring (for metrics)
- Cloud Logging (for structured logs)
- Vertex AI (for quality evaluation)

---

## Step 1: Environment Setup

### Required Environment Variables

```bash
# GCP Configuration
export GOOGLE_CLOUD_PROJECT=aipodcaster-481909
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Application Configuration
export ENVIRONMENT=production
export PORT=8080
export LOG_LEVEL=INFO
```

### Service Account Permissions

Required IAM roles for service account:
- `roles/aiplatform.user` (for Agent Engine)
- `roles/logging.logWriter` (for Cloud Logging)
- `roles/monitoring.metricWriter` (for Cloud Monitoring)
- `roles/cloudtrace.agent` (for Cloud Trace)

---

## Step 2: Deploy Agents to Agent Engine

```bash
cd backend
source venv/bin/activate
python deploy_to_agent_engine.py
```

**Expected Output**:
```
======================================================================
DEPLOYING CROSSFIRE AGENTS TO AGENT ENGINE
======================================================================
✅ shakti_moderator configured for deployment
✅ sovereignist configured for deployment
✅ reformist configured for deployment
✅ technocrat configured for deployment
✅ humanist configured for deployment

✅ Deployed 5 agents
======================================================================
📄 Deployment manifest saved to deployment_manifest.json
```

---

## Step 3: Deploy Backend to Cloud Run

### Create Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Deploy Command

```bash
gcloud run deploy crossfire-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=aipodcaster-481909 \
  --service-account crossfire-agents@aipodcaster-481909.iam.gserviceaccount.com \
  --min-instances 1 \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 2
```

---

## Step 4: Configure Observability

### Cloud Monitoring Dashboards

Create monitoring dashboard:

```bash
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

**monitoring-dashboard.json**:
```json
{
  "displayName": "CROSSFIRE Production Metrics",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Debates Generated",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"custom.googleapis.com/crossfire/debates_generated\""
                }
              }
            }]
          }
        }
      },
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Average Quality Scores",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"custom.googleapis.com/crossfire/quality_coherence\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

### Set Up Alerts

```bash
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="CROSSFIRE Safety Alert" \
  --condition-display-name="Low Safety Score" \
  --condition-threshold-value=0.85 \
  --condition-threshold-duration=60s \
  --condition-threshold-comparison=COMPARISON_LT \
  --condition-threshold-filter='metric.type="custom.googleapis.com/crossfire/quality_safety"'
```

---

## Step 5: Production Testing

### Health Check

```bash
curl https://crossfire-backend-{hash}-uc.a.run.app/
```

**Expected**: `{"status": "Omni-Cast ADK Backend Operational"}`

### WebSocket Test

```bash
# Install websocat if needed
brew install websocat

echo '{"topic":"Production Test","turns":2}' | \
  websocat wss://crossfire-backend-{hash}-uc.a.run.app/api/debate/stream-production
```

### Metrics Check

```bash
curl https://crossfire-backend-{hash}-uc.a.run.app/api/metrics
```

---

## Endpoints

### Production Endpoints

| Endpoint | Type | Purpose |
|----------|------|---------|
| `/` | GET | Health check |
| `/api/debate/stream-production` | WebSocket | Production debate stream |
| `/api/debate/stream-adk` | WebSocket | Basic ADK stream |
| `/api/metrics` | GET | Current metrics |
| `/api/debate/generate` | POST | Legacy batch endpoint |

---

## Monitoring URLs

After deployment, access:

1. **Cloud Run Service**: https://console.cloud.google.com/run
2. **Cloud Trace**: https://console.cloud.google.com/traces
3. **Cloud Monitoring**: https://console.cloud.google.com/monitoring
4. **Cloud Logging**: https://console.cloud.google.com/logs

---

## Production Checklist

- [ ] All 5 agents deployed to Agent Engine
- [ ] Backend deployed to Cloud Run
- [ ] Environment variables configured
- [ ] Service account permissions granted
- [ ] Monitoring dashboards created
- [ ] Alerts configured
- [ ] Health checks passing
- [ ] WebSocket connectivity verified
- [ ] Metrics endpoint responding
- [ ] Quality evaluation active (>0.85 coherence, >0.90 safety)
- [ ] Load testing completed
- [ ] Documentation updated

---

## Rollback Plan

If issues arise:

```bash
# Rollback Cloud Run deployment
gcloud run services update-traffic crossfire-backend \
  --to-revisions=PREVIOUS_REVISION=100

# Check previous revision
gcloud run revisions list --service=crossfire-backend
```

---

## Support

- **Logs**: `gcloud logging read "resource.type=cloud_run_revision"`
- **Metrics**: Check Cloud Monitoring dashboard
- **Traces**: View in Cloud Trace console

---

*Deployment Guide Version: 1.0*  
*Last Updated: December 24, 2024*
