# FastAPI entry point for self-fixing AI system
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
from typing import AsyncGenerator, List, Dict, Any

from app.graph.planner import TreeOfThoughtPlanner
from app.utils.llm import LLMProvider
from app.utils.rag import RAGRetriever

app = FastAPI(title="Self-Fixing AI System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}

class ExplainRequest(BaseModel):
    query: str
    include_reasoning: bool = True

# NOVEL: Initialize core components with dependency injection
llm_provider = LLMProvider()
rag_retriever = RAGRetriever()
tot_planner = TreeOfThoughtPlanner(llm_provider, rag_retriever)

@app.post("/chat-tot")
async def chat_with_tree_of_thought(request: ChatRequest):
    """Main endpoint for Tree-of-Thought enhanced chat with self-fixing capabilities"""
    
    async def stream_response() -> AsyncGenerator[str, None]:
        try:
            # NOVEL: Stream reasoning process in real-time
            async for step in tot_planner.plan_and_execute(
                query=request.message,
                context=request.context
            ):
                yield f"data: {json.dumps(step)}\n\n"
                
        except Exception as e:
            error_response = {
                "type": "error",
                "content": f"Planning failed: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }
            yield f"data: {json.dumps(error_response)}\n\n"
    
    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.post("/explain")
async def explain_reasoning(request: ExplainRequest):
    """Explainability endpoint showing RAG retrieval + reasoning tree"""
    
    try:
        # NOVEL: Combined RAG + reasoning explanation
        retrieved_docs = await rag_retriever.retrieve_relevant_docs(
            query=request.query,
            top_k=5
        )
        
        if request.include_reasoning:
            reasoning_tree = await tot_planner.explain_reasoning(
                query=request.query,
                retrieved_docs=retrieved_docs
            )
            
            return {
                "retrieved_docs": retrieved_docs,
                "reasoning_tree": reasoning_tree,
                "explainability_score": tot_planner.calculate_explainability_score(reasoning_tree)
            }
        
        return {"retrieved_docs": retrieved_docs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """System health check including component status"""
    return {
        "status": "healthy",
        "components": {
            "llm_provider": await llm_provider.health_check(),
            "rag_retriever": await rag_retriever.health_check(),
            "tot_planner": tot_planner.is_healthy()
        }
    }

@app.get("/metrics")
async def get_metrics():
    """System metrics for monitoring and optimization"""
    return await tot_planner.get_performance_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
