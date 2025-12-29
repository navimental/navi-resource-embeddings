from fastapi import FastAPI
from dotenv import load_dotenv

# Load .env BEFORE importing any routers or deps
load_dotenv()

from app.api.similar_case_studies import router as case_study_router
# from app.api.recommended_resources import router as resource_router
# from app.api.recommended_tasks import router as task_router

app = FastAPI()

app.include_router(case_study_router, prefix="/similar-case-studies", tags=["similar-case-studies"])
# app.include_router(resource_router, prefix="/recommended-resources", tags=["recommended-resources"])
# app.include_router(task_router, prefix="/recommended-tasks", tags=["recommended-tasks"])
