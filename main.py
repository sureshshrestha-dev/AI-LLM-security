from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base, get_db, engine

from core.gemini_agent import GeminiEngine
app = FastAPI()

@app.get("/")
async def root():   
    return {"message": "Hello World!"}


@app.on_event("startup")
async def startup_event():
    # Create the database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

    # Initialize Gemini Engine and load system prompt
    app.state.engine = GeminiEngine()
    with open("core/system_prompt.txt", "r") as f:
        app.state.system_instruction = f.read()
    print("Gemini Engine initialized")


@app.on_event("shutdown")
async def shutdown_event():
    # Close the database session when the application shuts down
    # Ensure any open sessions are closed; get_db yields a session
    try:
        db = next(get_db())
        db.close()
    except Exception:
        pass
    print("Database session closed")

@app.middleware("http")
async def db_session_middleware(request, call_next):
    response = None
    try:
        request.state.db = next(get_db())
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

@app.post("/chat")
async def chat(query: str, request: Request):
    engine = request.app.state.engine
    system_instruction = request.app.state.system_instruction
    response = await engine.call(system_instruction=system_instruction, user_prompt=query)
    return {"response": response}


@app.get("/student")
async def get_student(name: str, request: Request):
    """Return rows from the `students` table matching the given name."""
    db = getattr(request.state, "db", None)
    if db is None:
        raise HTTPException(status_code=500, detail="Database session not available")

    from sqlalchemy import text

    try:
        stmt = text("SELECT * FROM students WHERE name = :name")
        result = db.execute(stmt, {"name": name})
        rows = [dict(r) for r in result.mappings().all()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not rows:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"students": rows}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("Server is running on http://0.0.0.0:8000")
    chat_query = "What is the capital of France?"
    import asyncio
    response = asyncio.run(chat(chat_query))
    print(f"Chat response: {response}")