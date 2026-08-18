# Vocation – Explainable Opportunity Fit

**Status:** implemented on `dev`; domain/read semantics accepted, current surrounding product UI still subject to manual acceptance redesign.

## Purpose

`OpportunityFit` is a Vocation-owned, non-persisted read model for explaining how one Opportunity relates to one exact Search Profile revision. It is a decision aid, not a replacement for Tracking Status, personal Decisions, Groups/Waves, or ApplicationCase state.

The evaluation is deterministic and uses only explicit Vocation criteria, Search Profile policy, and available assessment evidence. It does not use an opaque ML model and does not mutate Opportunities or Assessments.

## Score scale

`weighted_fit_score` is either `null` or a value on the closed **0–100** scale.

For every configured criterion policy with positive weight and usable evidence:

1. the criterion value is normalized explicitly to 0–100;
2. the normalized value is multiplied by the configured weight;
3. the final fit is the weighted mean over the positive weights for which a score could actually be calculated.

Normalization is explicit by criterion type:

- numeric criteria use the criterion's configured numeric range and the Search Profile's declared direction (`higher_is_better` or `lower_is_better`);
- categorical criteria use explicit value-to-score mappings from the Search Profile;
- boolean criteria use an explicit preferred value;
- text criteria are not silently converted into a numeric score.

A weight of `0` disables that criterion for both the weighted fit and evidence completeness.

## Missing evidence and completeness

Missing or unscorable evidence never receives a silent neutral score. It is excluded from the fit numerator and scored-weight denominator and is reported explicitly in `missing_evidence` and the per-criterion contribution.

`evidence_completeness` is a separate **0–100** percentage:

`scored positive weight / configured positive weight * 100`

This means a high fit with low completeness remains visibly different from a high fit backed by complete evidence.

## Hard constraints

Hard-constraint state is independent from the weighted score:

- `pass`: no configured hard constraint failed and none is unresolved;
- `fail`: at least one deterministically evaluable required threshold failed;
- `unknown`: no hard failure exists, but at least one required condition cannot currently be evaluated from available structured evidence.

Search Profile `must_haves` and `must_not_haves` remain separate from criterion weights. Free-text constraints are reported as `unknown` until a structured evidence path exists; they are never simulated through an extreme weight.

A hard failure does not rewrite or clamp the weighted fit. The UI therefore distinguishes low fit from hard-constraint failure rather than conflating them.

## Evidence precedence and provenance

For one criterion, the current Personal Assessment takes precedence over External Assessment evidence when both exist. The selected evidence origin remains visible in every contribution.

`candidate_profile_revision` is populated only when Candidate Profile facts actually contribute to the evaluation. The current evaluator does not derive criterion scores from Candidate Profile facts, so this field remains `null` for the present implementation rather than claiming unused provenance.

## Read surfaces

The internal API exposes the same evaluator through:

- `GET /api/opportunity-fit` for a set of Opportunities;
- `GET /api/opportunities/{opportunity_id}/fit` for one Opportunity.

If no explicit Search Profile ID is supplied, the configured default Search Profile is used. A missing default profile is an explicit error rather than an implicit scoring policy.

The Opportunity workspace/list shows weighted fit, evidence completeness and hard-constraint state; it can filter/sort with the same backend/domain semantics and open the contribution breakdown. Opportunity detail renders the same breakdown model. No independent frontend scoring implementation exists.

## Boundaries

Opportunity Fit remains inside the Vocation bounded context. It is not a generic scoring service and is not part of Orientation, Wiiii Got This, Conveyance, or any frozen Published Vocation contract.

The manual product pass does not invalidate the evaluator. #45/#47 redesign how Profile policy and Fit controls are presented; `18_MANUAL_PRODUCT_ACCEPTANCE.md` records the current release gate.
