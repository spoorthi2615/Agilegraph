FROM python:3.10-slim

WORKDIR /app

# Install git and other essentials
RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Pre-install pytorch cpu first to speed up and avoid cuda bloat since we don't need nvidia wheels for building the env
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install the rest
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the huggingface model to bake it into the image
RUN python -c "from transformers import AutoTokenizer, AutoModel; AutoTokenizer.from_pretrained('microsoft/codebert-base'); AutoModel.from_pretrained('microsoft/codebert-base')" || true

COPY . .

EXPOSE 7860

# We use app.py as the entrypoint because it does some pre-download checks, 
# but uvicorn will run correctly.
CMD ["python", "app.py"]
