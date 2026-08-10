from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request

from vocation.api.schemas import (
    ComparisonAssessmentCriterionResponse,
    ComparisonDimensionCellResponse,
    ComparisonDimensionValueResponse,
    ComparisonExternalAssessmentResponse,
    ComparisonOpportunityResponse,
    ComparisonPersonalAssessmentResponse,
    ComparisonWorkLocationResponse,
    MapGroupMembershipResponse,
    OpportunityComparisonPayload,
    OpportunityComparisonResponse,
)
from vocation.application.comparison import ComparisonInputError, ComparisonOpportunityNotFound, OpportunityComparisonService

router = APIRouter(prefix="/api/comparison", tags=["comparison"])


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _required_iso(value: datetime) -> str:
    result = _iso(value)
    assert result is not None
    return result


def _response(comparison) -> OpportunityComparisonResponse:
    return OpportunityComparisonResponse(
        opportunities=[
            ComparisonOpportunityResponse(
                opportunity_id=item.opportunity_id,
                title=item.title,
                company_id=item.company_id,
                company_name=item.company_name,
                work_locations=[
                    ComparisonWorkLocationResponse(
                        label=location.label,
                        precision=location.precision,
                    )
                    for location in item.work_locations
                ],
                tracking_status=item.tracking_status,
                availability=item.availability,
                availability_last_checked_at=_iso(item.availability_last_checked_at),
                availability_age_days=item.availability_age_days,
                groups=[
                    MapGroupMembershipResponse(
                        group_id=group.group_id,
                        name=group.name,
                        group_type=group.group_type,
                    )
                    for group in item.groups
                ],
                research_dimensions={
                    dimension: ComparisonDimensionCellResponse(
                        state=cell.state,
                        values=[
                            ComparisonDimensionValueResponse(
                                value=value.value,
                                subject_type=value.subject_type,
                                subject_id=value.subject_id,
                                observed_at=_required_iso(value.observed_at),
                                evidence_summary=value.evidence_summary,
                            )
                            for value in cell.values
                        ],
                    )
                    for dimension, cell in item.research_dimensions.items()
                },
                personal_assessments=[
                    ComparisonPersonalAssessmentResponse(
                        criterion_id=assessment.criterion_id,
                        value=assessment.value,
                        reasoning=assessment.reasoning,
                        created_at=_required_iso(assessment.created_at),
                    )
                    for assessment in item.personal_assessments
                ],
                external_assessments=[
                    ComparisonExternalAssessmentResponse(
                        criterion_id=assessment.criterion_id,
                        value=assessment.value,
                        reasoning=assessment.reasoning,
                        created_at=_required_iso(assessment.created_at),
                    )
                    for assessment in item.external_assessments
                ],
            )
            for item in comparison.opportunities
        ],
        assessment_criteria=[
            ComparisonAssessmentCriterionResponse(
                criterion_id=criterion.criterion_id,
                display_name=criterion.display_name,
                display_order=criterion.display_order,
            )
            for criterion in comparison.assessment_criteria
        ],
    )


@router.post("/opportunities", response_model=OpportunityComparisonResponse)
def compare_opportunities(payload: OpportunityComparisonPayload, request: Request) -> OpportunityComparisonResponse:
    service: OpportunityComparisonService = request.app.state.comparison_service
    try:
        return _response(service.compare(payload.opportunity_ids))
    except ComparisonInputError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except ComparisonOpportunityNotFound as error:
        raise HTTPException(status_code=404, detail=f"Opportunity '{error.args[0]}' does not exist.") from error
