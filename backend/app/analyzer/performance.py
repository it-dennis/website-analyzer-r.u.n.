import httpx
import os
from typing import Optional
from ..schemas import PerformanceResult, PerformanceScores, PerformanceMetric

PAGESPEED_BASE = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
TIMEOUT = 30.0


def _metric_status(value_ms: Optional[int], good: int, poor: int) -> str:
    if value_ms is None:
        return "info"
    if value_ms <= good:
        return "good"
    if value_ms <= poor:
        return "needs-improvement"
    return "poor"


async def analyze(url: str) -> PerformanceResult:
    api_key = os.getenv("PAGESPEED_API_KEY", "")
    params: dict = {"url": url, "strategy": "mobile"}
    if api_key:
        params["key"] = api_key

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(PAGESPEED_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        cats = data.get("lighthouseResult", {}).get("categories", {})
        audits = data.get("lighthouseResult", {}).get("audits", {})

        scores = PerformanceScores(
            performance=round((cats.get("performance", {}).get("score") or 0) * 100),
            accessibility=round((cats.get("accessibility", {}).get("score") or 0) * 100),
            best_practices=round((cats.get("best-practices", {}).get("score") or 0) * 100),
            seo=round((cats.get("seo", {}).get("score") or 0) * 100),
        )

        def get_audit(key: str) -> Optional[str]:
            return audits.get(key, {}).get("displayValue")

        def get_audit_ms(key: str) -> Optional[int]:
            val = audits.get(key, {}).get("numericValue")
            return round(val) if val is not None else None

        fcp_ms = get_audit_ms("first-contentful-paint")
        lcp_ms = get_audit_ms("largest-contentful-paint")
        tbt_ms = get_audit_ms("total-blocking-time")
        cls_val = audits.get("cumulative-layout-shift", {}).get("numericValue")

        metrics = [
            PerformanceMetric(
                name="First Contentful Paint (FCP)",
                value=get_audit("first-contentful-paint") or "–",
                status=_metric_status(fcp_ms, 1800, 3000),
            ),
            PerformanceMetric(
                name="Largest Contentful Paint (LCP)",
                value=get_audit("largest-contentful-paint") or "–",
                status=_metric_status(lcp_ms, 2500, 4000),
            ),
            PerformanceMetric(
                name="Total Blocking Time (TBT)",
                value=get_audit("total-blocking-time") or "–",
                status=_metric_status(tbt_ms, 200, 600),
            ),
            PerformanceMetric(
                name="Cumulative Layout Shift (CLS)",
                value=get_audit("cumulative-layout-shift") or "–",
                status="good" if cls_val is not None and cls_val <= 0.1 else "needs-improvement" if cls_val is not None and cls_val <= 0.25 else "poor" if cls_val is not None else "info",
            ),
            PerformanceMetric(
                name="Speed Index",
                value=get_audit("speed-index") or "–",
                status="info",
            ),
        ]

        return PerformanceResult(
            score=scores.performance,
            scores=scores,
            metrics=metrics,
            strategy="mobile",
        )

    except httpx.HTTPStatusError as e:
        return PerformanceResult(
            score=None,
            metrics=[],
            strategy="mobile",
            error=f"PageSpeed API Fehler: {e.response.status_code}. Prüfe deinen API-Key.",
        )
    except Exception as e:
        return PerformanceResult(
            score=None,
            metrics=[],
            strategy="mobile",
            error=f"Performance-Analyse nicht verfügbar: {str(e)}",
        )
