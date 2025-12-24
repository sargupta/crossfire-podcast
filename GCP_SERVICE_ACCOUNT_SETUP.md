# GCP Service Account Setup for CI/CD

## Step-by-Step Instructions

### Step 1: Create Service Account

Run this command in your terminal:

```bash
gcloud iam service-accounts create crossfire-ci-cd \
  --display-name="CROSSFIRE CI/CD Pipeline" \
  --project=aipodcaster-481909
```

**Expected Output:**
```
Created service account [crossfire-ci-cd].
```

---

### Step 2: Grant Required Permissions

Run these commands to grant the necessary roles:

```bash
# 1. Storage Admin (for pushing to Google Container Registry)
gcloud projects add-iam-policy-binding aipodcaster-481909 \
  --member="serviceAccount:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# 2. Cloud Run Admin (for deploying services)
gcloud projects add-iam-policy-binding aipodcaster-481909 \
  --member="serviceAccount:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# 3. Service Account User (for Cloud Run to use service accounts)
gcloud projects add-iam-policy-binding aipodcaster-481909 \
  --member="serviceAccount:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# 4. Artifact Registry Writer (if using Artifact Registry instead of GCR)
gcloud projects add-iam-policy-binding aipodcaster-481909 \
  --member="serviceAccount:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

**Expected Output (for each):**
```
Updated IAM policy for project [aipodcaster-481909].
```

---

### Step 3: Create and Download Key

```bash
gcloud iam service-accounts keys create ~/crossfire-ci-cd-key.json \
  --iam-account=crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com
```

**Expected Output:**
```
created key [...] of type [json] as [/Users/sargupta/crossfire-ci-cd-key.json]
```

---

### Step 4: Encode Key for GitHub

```bash
# Base64 encode the key
cat ~/crossfire-ci-cd-key.json | base64 > ~/crossfire-ci-cd-key-base64.txt

# Display the encoded key (you'll copy this)
cat ~/crossfire-ci-cd-key-base64.txt
```

**Copy the output** - you'll need this for GitHub.

---

### Step 5: Add Secret to GitHub

1. **Go to GitHub Repository Settings:**
   - URL: https://github.com/sargupta/crossfire-podcast/settings/secrets/actions
   - Or: Repository → Settings → Secrets and variables → Actions

2. **Click "New repository secret"**

3. **Enter Details:**
   - **Name:** `GCP_SA_KEY`
   - **Value:** Paste the base64-encoded key from Step 4

4. **Click "Add secret"**

---

### Step 6: Clean Up Local Files (Security)

```bash
# Delete the key files from your local machine
rm ~/crossfire-ci-cd-key.json
rm ~/crossfire-ci-cd-key-base64.txt
```

**Important:** Never commit these files to git!

---

### Step 7: Test the Pipeline

```bash
# Trigger the CI/CD pipeline
git commit --allow-empty -m "test: Trigger CI/CD with GCP credentials"
git push origin develop
```

Then watch the GitHub Actions tab to see the pipeline run.

---

## Verification

### Check Service Account

```bash
# List service accounts
gcloud iam service-accounts list --project=aipodcaster-481909

# Check permissions
gcloud projects get-iam-policy aipodcaster-481909 \
  --flatten="bindings[].members" \
  --filter="bindings.members:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com"
```

### Check GitHub Secret

1. Go to: https://github.com/sargupta/crossfire-podcast/settings/secrets/actions
2. Verify `GCP_SA_KEY` is listed
3. You won't be able to view the value (security feature)

### Monitor Pipeline

1. Go to: https://github.com/sargupta/crossfire-podcast/actions
2. Watch the latest workflow run
3. Verify all jobs complete successfully:
   - ✅ Run Tests
   - ✅ Code Quality
   - ✅ Build Docker Image
   - ✅ Deploy to Staging

---

## Troubleshooting

### If Build Still Fails

**Check Docker authentication:**
```bash
# The workflow should show this in logs:
gcloud auth configure-docker
```

**Check image push:**
```bash
# Verify image exists in GCR
gcloud container images list --repository=gcr.io/aipodcaster-481909
```

### If Deployment Fails

**Check Cloud Run permissions:**
```bash
# Verify service account has Cloud Run Admin
gcloud projects get-iam-policy aipodcaster-481909 \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/run.admin"
```

**Check Cloud Run service:**
```bash
# List Cloud Run services
gcloud run services list --platform=managed --region=us-central1
```

---

## Expected Results

After successful setup:

1. **Build Job:**
   - Builds Docker image
   - Pushes to `gcr.io/aipodcaster-481909/crossfire-backend:latest`
   - Pushes to `gcr.io/aipodcaster-481909/crossfire-backend:[commit-sha]`

2. **Deploy to Staging:**
   - Deploys to Cloud Run service: `crossfire-backend-staging`
   - Region: `us-central1`
   - URL: `https://crossfire-backend-staging-[hash]-uc.a.run.app`

3. **Deploy to Production** (only on release branches):
   - Deploys to Cloud Run service: `crossfire-backend`
   - Creates git tag
   - Creates GitHub release

---

## Quick Reference

```bash
# All commands in one script
gcloud iam service-accounts create crossfire-ci-cd --display-name="CROSSFIRE CI/CD Pipeline" --project=aipodcaster-481909
gcloud projects add-iam-policy-binding aipodcaster-481909 --member="serviceAccount:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding aipodcaster-481909 --member="serviceAccount:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com" --role="roles/run.admin"
gcloud projects add-iam-policy-binding aipodcaster-481909 --member="serviceAccount:crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
gcloud iam service-accounts keys create ~/crossfire-ci-cd-key.json --iam-account=crossfire-ci-cd@aipodcaster-481909.iam.gserviceaccount.com
cat ~/crossfire-ci-cd-key.json | base64 > ~/crossfire-ci-cd-key-base64.txt
cat ~/crossfire-ci-cd-key-base64.txt
# Copy the output and add to GitHub as GCP_SA_KEY secret
rm ~/crossfire-ci-cd-key.json ~/crossfire-ci-cd-key-base64.txt
```

---

**Estimated Time:** 15-20 minutes
**Difficulty:** Medium
**Prerequisites:** gcloud CLI installed and authenticated
