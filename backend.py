from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

# Create FastAPI instance
app = FastAPI()

# Load OpenAI key from Replit secrets
openai_api_key = os.environ["openai_api_key"]

# Setup client
client = OpenAI(api_key=openai_api_key)

# === Pydantic Model ===
class ReportRequest(BaseModel):
    message: str

# === Root Route ===
@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}

# === GPT Recommendation Endpoint ===
@app.post("/recommend")
def recommend_report(request: ReportRequest):
    user_msg = request.message

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful, honest snowboard assistant."},
                {"role": "user", "content": user_msg}
            ]
        )
        gpt_reply = response.choices[0].message.content
        return {"recommendation": gpt_reply}

    except Exception as e:
        return {"recommendation": f"❌ Error talking to OpenAI: {str(e)}"}
