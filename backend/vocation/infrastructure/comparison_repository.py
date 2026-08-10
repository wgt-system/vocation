from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from vocation.application.comparison import (
    ComparisonCriterion,
    ComparisonExternalAssessment,
    ComparisonGroup,
    ComparisonObservation,
    ComparisonOpportunity,
    ComparisonPersonalAssessment,
    ComparisonWorkLocation,
)
from vocation.domain.availability import AvailabilityCheckResult, AvailabilityObservation
from vocation.infrastructure.models import (
    AssessmentCriterionModel,
    AvailabilityObservationModel,
    ExternalAssessmentModel,
    ObservationModel,
    OpportunityGroupMembershipModel,
    OpportunityGroupModel,
    OpportunityModel,
    PersonalAssessmentModel,
    PostingModel,
    WorkLocationModel,
)


class SqlAlchemyComparisonRepository:
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def get_many(self, opportunity_ids: Sequence[str]) -> list[ComparisonOpportunity]:
        with self.session_factory() as session:
            opportunities = session.scalars(select(OpportunityModel).where(OpportunityModel.id.in_(opportunity_ids))).all()
            if not opportunities:
                return []
            ids = [item.id for item in opportunities]
            postings = session.scalars(select(PostingModel).where(PostingModel.opportunity_id.in_(ids))).all()
            posting_ids = [item.id for item in postings]
            observations = session.scalars(
                select(ObservationModel).where(
                    ((ObservationModel.subject_type == "opportunity") & ObservationModel.subject_id.in_(ids))
                    | ((ObservationModel.subject_type == "posting") & ObservationModel.subject_id.in_(posting_ids))
                )
            ).all()
            external = session.scalars(
                select(ExternalAssessmentModel).where(
                    ExternalAssessmentModel.subject_type == "opportunity",
                    ExternalAssessmentModel.subject_id.in_(ids),
                )
            ).all()
            personal = session.scalars(
                select(PersonalAssessmentModel)
                .where(PersonalAssessmentModel.opportunity_id.in_(ids))
                .order_by(PersonalAssessmentModel.revision_number)
            ).all()
            locations = session.scalars(select(WorkLocationModel).where(WorkLocationModel.opportunity_id.in_(ids))).all()
            memberships = session.execute(
                select(
                    OpportunityGroupMembershipModel.opportunity_id,
                    OpportunityGroupModel.id,
                    OpportunityGroupModel.name,
                    OpportunityGroupModel.group_type,
                )
                .join(OpportunityGroupModel, OpportunityGroupModel.id == OpportunityGroupMembershipModel.group_id)
                .where(OpportunityGroupMembershipModel.opportunity_id.in_(ids))
                .order_by(OpportunityGroupMembershipModel.opportunity_id, OpportunityGroupMembershipModel.position)
            ).all()
            availability = session.scalars(
                select(AvailabilityObservationModel)
                .where(AvailabilityObservationModel.posting_id.in_(posting_ids))
                .order_by(
                    AvailabilityObservationModel.observed_at,
                    AvailabilityObservationModel.recorded_at,
                    AvailabilityObservationModel.id,
                )
            ).all()

            by_observation: dict[str, list[ComparisonObservation]] = {subject_id: [] for subject_id in ids + posting_ids}
            for item in observations:
                if item.observation_type not in {
                    "technology_requirement",
                    "task",
                    "seniority",
                    "experience_requirement",
                    "work_model",
                    "salary",
                }:
                    continue
                by_observation.setdefault(item.subject_id, []).append(
                    ComparisonObservation(
                        item.id,
                        item.subject_type,  # type: ignore[arg-type]
                        item.subject_id,
                        item.observation_type,  # type: ignore[arg-type]
                        json.loads(item.value_json),
                        item.observed_at,
                        item.evidence_summary,
                    )
                )
            current_personal: dict[tuple[str, str], PersonalAssessmentModel] = {}
            for personal_item in personal:
                current_personal[(personal_item.opportunity_id, personal_item.criterion_id)] = personal_item
            grouped_availability: dict[str, list[AvailabilityObservation]] = {posting_id: [] for posting_id in posting_ids}
            for availability_item in availability:
                assert availability_item.evidence_summary is not None
                grouped_availability[availability_item.posting_id].append(
                    AvailabilityObservation(
                        availability_item.id,
                        availability_item.posting_id,
                        cast(AvailabilityCheckResult, availability_item.result),
                        availability_item.observed_at,
                        availability_item.recorded_at,
                        availability_item.evidence_summary,
                    )
                )
            grouped_groups: dict[str, list[ComparisonGroup]] = {opportunity_id: [] for opportunity_id in ids}
            for row in memberships:
                grouped_groups[row.opportunity_id].append(ComparisonGroup(row.id, row.name, row.group_type))
            grouped_locations: dict[str, list[ComparisonWorkLocation]] = {opportunity_id: [] for opportunity_id in ids}
            for location in locations:
                grouped_locations[location.opportunity_id].append(ComparisonWorkLocation(location.label, location.precision))
            grouped_postings: dict[str, list[PostingModel]] = {opportunity_id: [] for opportunity_id in ids}
            for posting in postings:
                grouped_postings[posting.opportunity_id].append(posting)
            grouped_external: dict[str, list[ComparisonExternalAssessment]] = {opportunity_id: [] for opportunity_id in ids}
            for external_item in external:
                grouped_external[external_item.subject_id].append(
                    ComparisonExternalAssessment(
                        external_item.id,
                        external_item.criterion_id,
                        json.loads(external_item.value_json),
                        external_item.reasoning,
                        external_item.created_at,
                    )
                )
            result: list[ComparisonOpportunity] = []
            for opportunity in opportunities:
                item_postings = grouped_postings[opportunity.id]
                personal_items = [
                    assessment for (opportunity_id, _), assessment in current_personal.items() if opportunity_id == opportunity.id
                ]
                result.append(
                    ComparisonOpportunity(
                        opportunity.id,
                        opportunity.canonical_title,
                        opportunity.company_id,
                        opportunity.company.canonical_name,
                        tuple(grouped_locations[opportunity.id]),
                        opportunity.tracking_status,
                        tuple(grouped_groups[opportunity.id]),
                        tuple(posting.id for posting in item_postings),
                        tuple(
                            observation
                            for subject_id in [opportunity.id, *[posting.id for posting in item_postings]]
                            for observation in by_observation[subject_id]
                        ),
                        tuple(tuple(grouped_availability[posting.id]) for posting in item_postings),
                        tuple(
                            ComparisonPersonalAssessment(
                                assessment.criterion_id,
                                json.loads(assessment.value_json),
                                assessment.reasoning,
                                assessment.created_at,
                            )
                            for assessment in personal_items
                        ),
                        tuple(sorted(grouped_external[opportunity.id], key=lambda entry: (entry.created_at, entry.id), reverse=True)),
                    )
                )
            return result

    def criteria(self, criterion_ids: Sequence[str]) -> list[ComparisonCriterion]:
        if not criterion_ids:
            return []
        with self.session_factory() as session:
            rows = session.scalars(select(AssessmentCriterionModel).where(AssessmentCriterionModel.criterion_id.in_(criterion_ids))).all()
            return [ComparisonCriterion(row.criterion_id, row.display_name, row.display_order) for row in rows]
