from pydantic import BaseModel, Field


class CVProfile(BaseModel):
    candidate_name: str
    education: list[str] = Field(default_factory=list)
    technical_skills: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    machine_learning_skills: list[str] = Field(default_factory=list)
    nlp_skills: list[str] = Field(default_factory=list)
    frameworks_and_libraries: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)