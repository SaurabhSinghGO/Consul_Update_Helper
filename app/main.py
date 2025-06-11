from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import get_or_post, transfer, compare

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(get_or_post.router)
app.include_router(compare.router)
app.include_router(transfer.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)