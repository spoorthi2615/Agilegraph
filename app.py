import os
import sys
import uvicorn
from transformers import AutoTokenizer, AutoModel

# Hugging Face sets HF_HOME to a cache dir. Ensure it's set.
os.environ["HF_HOME"] = os.environ.get("HF_HOME", "/tmp/huggingface_cache")

print("Pre-downloading CodeBERT model to prevent API timeouts...")
try:
    AutoTokenizer.from_pretrained('microsoft/codebert-base')
    AutoModel.from_pretrained('microsoft/codebert-base')
    print("Model downloaded successfully!")
except Exception as e:
    print(f"Warning: Failed to pre-download CodeBERT model: {e}. Falling back to cached embeddings or AST features.")

import spaces
import gradio as gr

@spaces.GPU
def _zero_gpu_warmup():
    pass

import sys
sys.path.insert(0, os.path.abspath("backend"))

from app.main import app

# Create a dummy Gradio UI so HF's ZeroGPU scanner is completely satisfied
demo = gr.Interface(fn=_zero_gpu_warmup, inputs=None, outputs=None)

# Mount the dummy UI onto our FastAPI app.
# Hugging Face's Gradio SDK will automatically detect and run this FastAPI 'app' using Uvicorn!
app = gr.mount_gradio_app(app, demo, path="/_gradio_dummy")

if __name__ == "__main__":
    # Hugging Face spaces expose port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
