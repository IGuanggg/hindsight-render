"""
Hindsight API - 简化版，用于 Render 部署
支持混元(Hunyuan)和 Gemini
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import os

app = FastAPI(title="Hindsight API", version="1.0.0")

# LLM 配置
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "bailian")  # bailian / hunyuan / gemini
BAILIAN_API_KEY = os.getenv("BAILIAN_API_KEY")
BAILIAN_BASE_URL = os.getenv("BAILIAN_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1")
BAILIAN_MODEL = os.getenv("BAILIAN_MODEL", "qwen3.5-plus")

# 内存存储（生产环境应使用 PostgreSQL）
memory_db: Dict[str, List[dict]] = {}

class MemoryBlock(BaseModel):
    content: str
    keywords: List[str] = []
    metadata: dict = {}
    lessons_learned: Optional[str] = None

class MemoryResponse(BaseModel):
    id: str
    bank_id: str
    content: str
    keywords: List[str]
    metadata: dict
    lessons_learned: Optional[str]
    created_at: str
    retrieval_count: int = 0
    feedback_score: int = 0

@app.get("/")
def root():
    return {"message": "Hindsight API", "version": "1.0.0"}

@app.get("/ping")
def ping():
    """Keep alive endpoint"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

@app.post("/banks/{bank_id}/memory-blocks", response_model=MemoryResponse)
def create_memory_block(bank_id: str, block: MemoryBlock):
    """创建记忆块"""
    if bank_id not in memory_db:
        memory_db[bank_id] = []
    
    memory = {
        "id": str(uuid.uuid4()),
        "bank_id": bank_id,
        "content": block.content,
        "keywords": block.keywords,
        "metadata": block.metadata,
        "lessons_learned": block.lessons_learned,
        "created_at": datetime.now().isoformat(),
        "retrieval_count": 0,
        "feedback_score": 0
    }
    
    memory_db[bank_id].append(memory)
    return MemoryResponse(**memory)

@app.get("/banks/{bank_id}/memory-blocks")
def retrieve_memories(bank_id: str, query: Optional[str] = None, limit: int = 10):
    """检索记忆块"""
    if bank_id not in memory_db:
        return []
    
    memories = memory_db[bank_id]
    
    if query:
        # 简单关键词匹配
        query_lower = query.lower()
        scored = []
        for mem in memories:
            score = 0
            if query_lower in mem["content"].lower():
                score += 2
            for kw in mem["keywords"]:
                if query_lower in kw.lower():
                    score += 3
            if score > 0:
                mem["retrieval_count"] += 1
                scored.append((mem, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        memories = [x[0] for x in scored[:limit]]
    
    return memories[:limit]

@app.get("/banks/{bank_id}/memory-blocks/{memory_id}")
def get_memory(bank_id: str, memory_id: str):
    """获取单个记忆块"""
    if bank_id not in memory_db:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    for mem in memory_db[bank_id]:
        if mem["id"] == memory_id:
            return mem
    
    raise HTTPException(status_code=404, detail="Memory not found")

@app.post("/banks/{bank_id}/memory-blocks/{memory_id}/feedback")
def report_feedback(bank_id: str, memory_id: str, feedback_type: str, comment: Optional[str] = None):
    """反馈记忆质量"""
    if bank_id not in memory_db:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    for mem in memory_db[bank_id]:
        if mem["id"] == memory_id:
            if feedback_type == "positive":
                mem["feedback_score"] += 1
            elif feedback_type == "negative":
                mem["feedback_score"] -= 1
            return {"status": "success"}
    
    raise HTTPException(status_code=404, detail="Memory not found")

@app.get("/banks/{bank_id}/stats")
def get_bank_stats(bank_id: str):
    """获取记忆库统计"""
    if bank_id not in memory_db:
        return {"total_memories": 0}
    
    return {
        "bank_id": bank_id,
        "total_memories": len(memory_db[bank_id]),
        "created_at": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
