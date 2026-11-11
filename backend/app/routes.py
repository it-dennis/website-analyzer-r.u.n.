import asyncio
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from .schemas import AnalysisRequest, AnalysisResult, SEOResult, PerformanceResult, SecurityResult, ContentResult
from .rate_limit import rate_limit
from .safe_url import assert_safe_url, UnsafeURLError
from .analyzer import seo, performance, security, content

router = APIRouter(prefix="/api")


def _overall_score(s: SEOResult, p: PerformanceResult, sec: SecurityResult, c: ContentResult) -> int:
    perf_score = p.score if p.score is not None else 50
    return round(
        s.score * 0.35
        + perf_score * 0.35
        + sec.score * 0.20
        + c.score * 0.10
    )


@router.post("/analyze", response_model=AnalysisResult, dependencies=[Depends(rate_limit)])
async def analyze_url(request: AnalysisRequest):
    url = request.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        await asyncio.get_running_loop().run_in_executor(None, assert_safe_url, url)
    except UnsafeURLError as e:
        raise HTTPException(status_code=400, detail=str(e))

    t0 = time.monotonic()
    results = await asyncio.gather(
        seo.analyze(url),
        performance.analyze(url),
        security.analyze(url),
        content.analyze(url),
        return_exceptions=True,
    )

    seo_r = results[0] if not isinstance(results[0], Exception) else SEOResult(score=0, checks=[], error=str(results[0]))
    perf_r = results[1] if not isinstance(results[1], Exception) else PerformanceResult(score=None, metrics=[], strategy="mobile", error=str(results[1]))
    sec_r = results[2] if not isinstance(results[2], Exception) else SecurityResult(score=0, checks=[], error=str(results[2]))
    cont_r = results[3] if not isinstance(results[3], Exception) else ContentResult(score=0, checks=[], error=str(results[3]))

    response_ms = round((time.monotonic() - t0) * 1000)

    return AnalysisResult(
        url=url,
        overall_score=_overall_score(seo_r, perf_r, sec_r, cont_r),
        seo=seo_r,
        performance=perf_r,
        security=sec_r,
        content=cont_r,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
        response_time_ms=response_ms,
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
