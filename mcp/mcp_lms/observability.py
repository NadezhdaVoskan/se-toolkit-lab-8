"""Helpers for VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import os

import httpx


def _logs_base_url() -> str:
    return os.environ.get("NANOBOT_VICTORIA_LOGS_URL", "http://victorialogs:9428").rstrip("/")


def _traces_base_url() -> str:
    return os.environ.get("NANOBOT_VICTORIA_TRACES_URL", "http://victoriatraces:10428").rstrip("/")


async def logs_search(query: str, limit: int = 20) -> str:
    q = query.strip() or "db_query"
    async with httpx.AsyncClient(timeout=15.0) as c:
        r = await c.get(
            f"{_logs_base_url()}/select/logsql/query",
            params={"query": q, "limit": limit},
        )
        r.raise_for_status()
        return r.text


async def logs_error_count(hours: int = 1, limit: int = 200) -> dict:
    queries = [
        'db_query',
        'auth_failure',
        'unhandled_exception',
        'request_completed',
    ]

    all_lines: list[str] = []

    async with httpx.AsyncClient(timeout=15.0) as c:
        for query in queries:
            r = await c.get(
                f"{_logs_base_url()}/select/logsql/query",
                params={"query": query, "limit": limit},
            )
            r.raise_for_status()
            all_lines.extend([line for line in r.text.splitlines() if line.strip()])

    error_lines = [
        line for line in all_lines
        if (" ERROR " in line)
        or ('"level":"error"' in line.lower())
        or ('connection is closed' in line.lower())
        or ('connection refused' in line.lower())
        or (' 500' in line)
        or (' 404' in line and 'Items not found' in line)
    ]

    # убираем дубликаты, сохраняя порядок
    seen = set()
    unique_errors = []
    for line in error_lines:
        if line not in seen:
            seen.add(line)
            unique_errors.append(line)

    return {
        "service": "Learning Management Service",
        "hours": hours,
        "logs_checked": len(all_lines),
        "error_count": len(unique_errors),
        "sample_errors": unique_errors[:5],
    }

async def traces_list(service: str = "Learning Management Service", limit: int = 10) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as c:
        r = await c.get(
            f"{_traces_base_url()}/select/jaeger/api/traces",
            params={"service": service, "limit": limit},
        )
        r.raise_for_status()
        return r.json()


async def traces_get(trace_id: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as c:
        r = await c.get(f"{_traces_base_url()}/select/jaeger/api/traces/{trace_id}")
        r.raise_for_status()
        return r.json()
