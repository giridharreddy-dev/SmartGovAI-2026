"""Strict four-block contract for reviewed scheme details and review drafts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, field_validator, model_validator

SectionStatus = Literal["verified", "official_source_unspecified", "verification_pending"]
Section = Literal["eligibility", "required_documents", "benefits", "application_process"]
DocumentId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)


class Text(Record):
    en: str | None = None
    te: str | None = None

    @model_validator(mode="after")
    def require_text(self):
        if not (self.en or self.te):
            raise ValueError("At least one language must contain text")
        return self


class Eligibility(Record):
    age_range: Text | None = None
    income_ceiling: Text | None = None
    caste_category: list[Text] = Field(default_factory=list)
    residence: Text | None = None
    target_group: Text | None = None
    criteria: list[Text] = Field(default_factory=list)
    exclusions: list[Text] = Field(default_factory=list)


class Document(Record):
    id: DocumentId | None = None
    name: Text
    purpose: Text | None = None
    mandatory: bool | None = None


class Benefits(Record):
    coverage_amount: Text | None = None
    coverage_type: Text | None = None
    subsidy_percentage: Text | None = None
    disbursement: Text | None = None
    cashless: bool | None = None
    details: list[Text] = Field(default_factory=list)


class Application(Record):
    mode: Text | None = None
    nodal_agency: Text | None = None
    official_url: HttpUrl | None = None
    offline_office: Text | None = None
    steps: list[Text] = Field(default_factory=list)
    verification: Text | None = None

    @field_validator("official_url")
    @classmethod
    def official_https(cls, url):
        if url and (url.scheme != "https" or url.username or url.password):
            raise ValueError("The official application URL must use HTTPS without credentials")
        return url


class SchemeOperations(Record):
    eligibility: Eligibility
    required_documents: list[Document]
    benefits: Benefits
    application_process: Application


class OperationalDraft(SchemeOperations):
    id: str
    title: Text
    operational_status: Literal["pending_human_verification"]
