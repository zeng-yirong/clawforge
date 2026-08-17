from __future__ import annotations

from copy import deepcopy
from typing import Any


SOURCE_TYPE_REPORT = "report"
SOURCE_TYPE_PRESENTATION = "presentation"
SOURCE_TYPE_MEDIA_SAMPLE = "media_sample"


def build_report_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": report["report_id"],
        "source_type": SOURCE_TYPE_REPORT,
        "title": report["title"],
        "sector": report["sector"],
        "published_at": report["published_at"],
        "tags": report.get("tags", []),
        "summary": report["summary"],
    }


def build_presentation_summary(presentation: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": presentation["presentation_id"],
        "source_type": SOURCE_TYPE_PRESENTATION,
        "title": presentation["title"],
        "owner": presentation["owner"],
        "updated_at": presentation["updated_at"],
        "tags": presentation.get("tags", []),
        "summary": presentation["summary"],
    }


def build_media_sample_summary(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": sample["sample_id"],
        "source_type": SOURCE_TYPE_MEDIA_SAMPLE,
        "title": sample["title"],
        "channel": sample["channel"],
        "captured_at": sample["captured_at"],
        "tags": sample.get("tags", []),
        "summary": sample["summary"],
    }


def list_reports(
    session: dict[str, Any],
    *,
    query: str = "",
    sector: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    sector_lower = sector.strip().lower() if sector else None
    results: list[dict[str, Any]] = []
    for report in session["reports"]:
        if sector_lower and str(report["sector"]).lower() != sector_lower:
            continue
        searchable = " ".join(
            [
                report["title"],
                report["summary"],
                report.get("content", ""),
                " ".join(report.get("tags", [])),
                " ".join(report.get("solution_aliases", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        results.append(build_report_summary(report))
    results.sort(key=lambda item: (str(item["published_at"]), str(item["document_id"])), reverse=True)
    return results[:limit] if limit is not None else results


def list_presentations(
    session: dict[str, Any],
    *,
    query: str = "",
    owner: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    owner_lower = owner.strip().lower() if owner else None
    results: list[dict[str, Any]] = []
    for presentation in session["presentations"]:
        if owner_lower and str(presentation["owner"]).lower() != owner_lower:
            continue
        searchable = " ".join(
            [
                presentation["title"],
                presentation["summary"],
                presentation.get("deck_notes", ""),
                " ".join(presentation.get("tags", [])),
                " ".join(presentation.get("solution_aliases", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        results.append(build_presentation_summary(presentation))
    results.sort(key=lambda item: (str(item["updated_at"]), str(item["document_id"])), reverse=True)
    return results[:limit] if limit is not None else results


def list_media_samples(
    session: dict[str, Any],
    *,
    query: str = "",
    channel: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    channel_lower = channel.strip().lower() if channel else None
    results: list[dict[str, Any]] = []
    for sample in session["media_samples"]:
        if channel_lower and str(sample["channel"]).lower() != channel_lower:
            continue
        searchable = " ".join(
            [
                sample["title"],
                sample["summary"],
                sample.get("content", ""),
                " ".join(sample.get("tags", [])),
                " ".join(sample.get("solution_aliases", [])),
            ]
        ).lower()
        if query_lower and query_lower not in searchable:
            continue
        results.append(build_media_sample_summary(sample))
    results.sort(key=lambda item: (str(item["captured_at"]), str(item["document_id"])), reverse=True)
    return results[:limit] if limit is not None else results


def get_report(session: dict[str, Any], report_id: str) -> dict[str, Any]:
    for report in session["reports"]:
        if report["report_id"] == report_id:
            payload = deepcopy(report)
            payload["document_id"] = payload["report_id"]
            payload["source_type"] = SOURCE_TYPE_REPORT
            return payload
    raise KeyError(f"Report not found: {report_id}")


def get_presentation(session: dict[str, Any], presentation_id: str) -> dict[str, Any]:
    for presentation in session["presentations"]:
        if presentation["presentation_id"] == presentation_id:
            payload = deepcopy(presentation)
            payload["document_id"] = payload["presentation_id"]
            payload["source_type"] = SOURCE_TYPE_PRESENTATION
            return payload
    raise KeyError(f"Presentation not found: {presentation_id}")


def get_media_sample(session: dict[str, Any], sample_id: str) -> dict[str, Any]:
    for sample in session["media_samples"]:
        if sample["sample_id"] == sample_id:
            payload = deepcopy(sample)
            payload["document_id"] = payload["sample_id"]
            payload["source_type"] = SOURCE_TYPE_MEDIA_SAMPLE
            return payload
    raise KeyError(f"Media sample not found: {sample_id}")


def _iter_documents(session: dict[str, Any]) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for report in session["reports"]:
        documents.append(
            {
                "document_id": report["report_id"],
                "source_type": SOURCE_TYPE_REPORT,
                "title": report["title"],
                "summary": report["summary"],
                "body": report.get("content", ""),
                "tags": report.get("tags", []),
                "aliases": report.get("solution_aliases", []),
                "published_at": report["published_at"],
            }
        )
    for presentation in session["presentations"]:
        documents.append(
            {
                "document_id": presentation["presentation_id"],
                "source_type": SOURCE_TYPE_PRESENTATION,
                "title": presentation["title"],
                "summary": presentation["summary"],
                "body": presentation.get("deck_notes", ""),
                "tags": presentation.get("tags", []),
                "aliases": presentation.get("solution_aliases", []),
                "published_at": presentation["updated_at"],
            }
        )
    for sample in session["media_samples"]:
        documents.append(
            {
                "document_id": sample["sample_id"],
                "source_type": SOURCE_TYPE_MEDIA_SAMPLE,
                "title": sample["title"],
                "summary": sample["summary"],
                "body": sample.get("content", ""),
                "tags": sample.get("tags", []),
                "aliases": sample.get("solution_aliases", []),
                "published_at": sample["captured_at"],
            }
        )
    return documents


def _snippet(document: dict[str, Any], query: str) -> str:
    haystack = f"{document['summary']} {document['body']}"
    query_lower = query.lower()
    start = haystack.lower().find(query_lower)
    if start < 0:
        return haystack[:180]
    prefix = max(0, start - 50)
    suffix = min(len(haystack), start + len(query) + 110)
    return haystack[prefix:suffix]


def search_library(
    session: dict[str, Any],
    *,
    query: str,
    source_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query_lower = query.strip().lower()
    source_type_lower = source_type.strip().lower() if source_type else None
    tokens = [item for item in query_lower.split() if item]
    results: list[dict[str, Any]] = []

    for document in _iter_documents(session):
        if source_type_lower and document["source_type"] != source_type_lower:
            continue
        fields = [
            document["title"],
            document["summary"],
            document["body"],
            " ".join(document["tags"]),
            " ".join(document["aliases"]),
        ]
        searchable = " ".join(fields).lower()
        if query_lower and query_lower not in searchable and not all(token in searchable for token in tokens):
            continue
        score = sum(searchable.count(token) for token in tokens) if tokens else searchable.count(query_lower)
        matched_fields: list[str] = []
        if query_lower in document["title"].lower():
            matched_fields.append("title")
        if query_lower in document["summary"].lower():
            matched_fields.append("summary")
        if query_lower in document["body"].lower():
            matched_fields.append("body")
        if any(query_lower in tag.lower() for tag in document["tags"]):
            matched_fields.append("tags")
        if any(query_lower in alias.lower() for alias in document["aliases"]):
            matched_fields.append("aliases")
        results.append(
            {
                "document_id": document["document_id"],
                "source_type": document["source_type"],
                "title": document["title"],
                "published_at": document["published_at"],
                "score": score,
                "matched_fields": sorted(set(matched_fields)),
                "snippet": _snippet(document, query),
            }
        )

    results.sort(key=lambda item: (-int(item["score"]), str(item["published_at"]), str(item["document_id"])), reverse=False)
    return results[:limit] if limit is not None else results
