# Hugging Face Spaces Deployment Guide

To deploy the full AgileGraph Machine Learning backend (including GATv2 and CodeBERT) for free using Hugging Face Spaces, follow these steps:

## 1. Create the Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. **Space name**: `agilegraph-api` (or your choice).
3. **License**: Optional (e.g., MIT).
4. **Select the Space SDK**: Choose **Docker**, then select **Blank**.
5. **Space hardware**: Keep the default free tier (2 vCPU, 16 GB RAM).
6. Click **Create Space**.

## 2. Configure Environment Secrets
Go to your Space's **Settings** tab, scroll down to **Variables and secrets**, and add the following **New Secrets**:
* `NEO4J_URI` (e.g., `neo4j+s://your-db.databases.neo4j.io`)
* `NEO4J_USER` (e.g., `neo4j`)
* `NEO4J_PASSWORD` (your database password)

## 3. Push Your Code
Hugging Face Spaces are essentially Git repositories. You need to push this code to the space.
In your local terminal, run the following (replace `<your-username>` with your Hugging Face username):

```bash
# Add Hugging Face as a remote
git remote add huggingface https://huggingface.co/spaces/<your-username>/agilegraph-api

# Hugging Face requires the Dockerfile to be named `Dockerfile` at the root.
# You can copy our specific HF Dockerfile over the root Dockerfile (or rename it):
cp Dockerfile.hf Dockerfile
git add Dockerfile backend/
git commit -m "Deploy to Hugging Face Spaces"

# Push to the space (this will trigger the build)
git push huggingface main
```

## 4. Update the Frontend
Once the Space is "Running", you will get a URL like `https://your-username-agilegraph-api.hf.space`. 

Update your frontend's environment variable to point to this new URL instead of the Railway URL. Since this instance has 16 GB of RAM and installs `requirements.txt`, the GATv2+CodeBERT pipeline will successfully execute and the `risk_score` will be driven by the actual Graph Neural Network!
