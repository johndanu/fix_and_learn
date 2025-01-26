from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import sys
import os
import requests

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
security = HTTPBearer()

# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AgentRequest(BaseModel):
    query: str
    user_id: str
    request_id: str
    session_id: str

class AgentResponse(BaseModel):
    success: bool

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify the bearer token against environment variable."""
    expected_token = os.getenv("API_BEARER_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="API_BEARER_TOKEN environment variable not set"
        )
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return True

async def fetch_conversation_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the most recent conversation history for a session."""
    try:
        response = supabase.table("messages") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        # Convert to list and reverse to get chronological order
        messages = response.data[::-1]
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch conversation history: {str(e)}")

async def store_message(session_id: str, message_type: str, content: str, data: Optional[Dict] = None):
    """Store a message in the Supabase messages table."""
    message_obj = {
        "type": message_type,
        "content": content
    }
    if data:
        message_obj["data"] = data

    try:
        supabase.table("messages").insert({
            "session_id": session_id,
            "message": message_obj
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store message: {str(e)}")

@app.post("/api/sample-supabase-agent", response_model=AgentResponse)
async def sample_supabase_agent(
    request: AgentRequest,
    authenticated: bool = Depends(verify_token)
):
    try:
        # Fetch conversation history from the DB
        conversation_history = await fetch_conversation_history(request.session_id)
        
        # Convert conversation history to format expected by agent
        # This will be different depending on your framework (Pydantic AI, LangChain, etc.)
        messages = []
        for msg in conversation_history:
            msg_data = msg["message"]
            msg_type = msg_data["type"]
            msg_content = msg_data["content"]
            msg = {"role": msg_type, "content": msg_content}
            messages.append(msg)

        # Store user's query
        await store_message(
            session_id=request.session_id,
            message_type="human",
            content=request.query
        )            
        
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
            "Content-Type": "application/json"
        }
        content = (
            "Identify the programming language used in the provided code snippet and list its programming concepts. "
            f"{request.query}"
            "If the language is identified, organize the response as follows: "
            "Programming Language: Name of the language. "
            "Programming Concepts: "
            "- Concept 1: "
            "  - Subconcept 1: Explanation (in simple terms, up to 100 words, with examples). "
            "  - Subconcept 2: Explanation (in simple terms, up to 100 words, with examples). "
            "(Continue for additional concepts as needed). "
            "If the code provided error : "
             "Programming Concepts to learn to fix the eror: "
            "- Concept 1: "
            "  - Subconcept 1: Explanation (in simple terms, up to 100 words, with examples). "
            "  - Subconcept 2: Explanation (in simple terms, up to 100 words, with examples). "
            "(Continue for additional concepts as needed). "
            "If the programming language cannot be identified: "
            "Provide an explanation of the possible programming concepts behind the snippet, following the structure above."
        )
        payload = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "messages": [
                {
                    "role": "user",
                    "content": content   }
            ]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
             # Parse the JSON response
            response_data = response.json()
            model_response = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if model_response:
                print("Model Response:", model_response)
            else:
                print("No response content found.")
            print(response)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))

        """
        TODO:
        This is where you insert the custom logic to get the response from your agent.
        Your agent can also insert more records into the database to communicate
        actions/status as it is handling the user's question/request.
        Additionally:
            - Use the 'messages' array defined about for the chat history. This won't include the latest message from the user.
            - Use request.query for the user's prompt.
            - Use request.session_id if you need to insert more messages into the DB in the agent logic.
        """
        agent_response = model_response

        # Store agent's response
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content=agent_response,
            data={"request_id": request.request_id}
        )

        return AgentResponse(success=True)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        # Store error message in conversation
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content="I apologize, but I encountered an error processing your request.",
            data={"error": str(e), "request_id": request.request_id}
        )
        return AgentResponse(success=False)

if __name__ == "__main__":
    import uvicorn
    # Feel free to change the port here if you need
    uvicorn.run(app, host="0.0.0.0", port=8001)
