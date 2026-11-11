from pydantic import BaseModel
from typing import Optional, List


class AnalysisRequest(BaseModel):
    url: str


class Check(BaseModel):
    name: str
    status: str  # "pass" | "warning" | "fail" | "info"
    value: Optional[str] = None
    recommendation: Optional[str] = None


class SEOResult(BaseModel):
    score: int
    title: Optional[str] = None
    description: Optional[str] = None
    checks: List[Check] = []
    error: Optional[str] = None


class PerformanceScores(BaseModel):
    performance: Optional[int] = None
    accessibility: Optional[int] = None
    best_practices: Optional[int] = None
    seo: Optional[int] = None


class PerformanceMetric(BaseModel):
    name: str
    value: str
    status: str  # "good" | "needs-improvement" | "poor" | "info"


class PerformanceResult(BaseModel):
    score: Optional[int] = None
    scores: Optional[PerformanceScores] = None
    metrics: List[PerformanceMetric] = []
    strategy: str = "mobile"
    error: Optional[str] = None


class SecurityResult(BaseModel):
    score: int
    is_https: bool = False
    ssl_valid: Optional[bool] = None
    ssl_expiry_days: Optional[int] = None
    ssl_issuer: Optional[str] = None
    checks: List[Check] = []
    error: Optional[str] = None


class ContentResult(BaseModel):
    score: int
    word_count: Optional[int] = None
    reading_time_minutes: Optional[float] = None
    internal_links: Optional[int] = None
    external_links: Optional[int] = None
    total_images: Optional[int] = None
    images_missing_alt: Optional[int] = None
    checks: List[Check] = []
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    url: str
    overall_score: int
    seo: SEOResult
    performance: PerformanceResult
    security: SecurityResult
    content: ContentResult
    analyzed_at: str
    response_time_ms: Optional[int] = None
    http_status: Optional[int] = None
