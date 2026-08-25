from pydantic import BaseModel, Field


class JobProfile(BaseModel):
    job_title: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    years_of_experience_required: int = 0