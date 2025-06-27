from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

# Setup OpenAI client
client = OpenAI(api_key=os.environ["openai_api_key"])

# Pydantic model for request
class ReportRequest(BaseModel):
    message: str

# Route handler
@router.post("/recommend")
def recommend_report(request: ReportRequest):
    user_msg = request.message

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful, honest snowboard assistant."},
                {"role": "user", "content": user_msg}
            ]
        )
        gpt_reply = response.choices[0].message.content
        return {"recommendation": gpt_reply}

    except Exception as e:
        return {"recommendation": f"❌ Error talking to OpenAI: {str(e)}"}
