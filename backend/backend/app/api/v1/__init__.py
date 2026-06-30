"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import agent, events, health, tasks

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(tasks.router)
api_router.include_router(events.router)
api_router.include_router(agent.router)
