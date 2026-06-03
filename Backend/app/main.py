import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import get_settings
from app.database import init_db
from app.graph.builder import build_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

compiled_graph = None
_checkpointer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global compiled_graph

    settings = get_settings()
    logger.info("Starting Mental Health Chatbot Backend")
    logger.info("Model: %s", settings.gemini_model_name)

    await init_db()
    logger.info("Database tables initialized")

    db_url = settings.checkpointer_db_url
    async with AsyncPostgresSaver.from_conn_string(db_url) as checkpointer:
        await checkpointer.setup()
        logger.info("LangGraph checkpointer initialized")

        graph = build_graph()
        compiled_graph = graph.compile(checkpointer=checkpointer)
        logger.info("LangGraph agent compiled and ready")

        yield

    logger.info("Shutting down")


app = FastAPI(
    title="Mental Health Chatbot API",
    description="An empathetic AI companion for mental health support, powered by LangGraph and Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import auth, chat, mood, resources  # noqa: E402

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(mood.router)
app.include_router(resources.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "mental-health-chatbot"}
