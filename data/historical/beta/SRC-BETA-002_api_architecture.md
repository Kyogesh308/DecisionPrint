# API Gateway Architecture — GraphQL Evaluation
**Date:** 2024-08-05
**Type:** architecture_doc
**Author:** James Morrison

## Overview
We evaluated GraphQL as a potential technology for our new API Gateway in Project Beta.

## Evaluation
**Constraints:**
- **client_count=3**: We currently only have 3 known internal clients consuming our APIs (Web App, Mobile App, internal admin tool).
- **client_diversity=internal_only**: All clients are developed in-house. We do not expose public APIs.
- **schema_complexity=low**: Our data models are relatively flat and straightforward.

## Decision
We have decided to stick with a RESTful architecture for the API Gateway and reject GraphQL.

## Rationale
1. **Low Client Count:** With only 3 internal clients, the over-fetching/under-fetching problem GraphQL solves is not a significant pain point for us. We can easily tailor REST endpoints to specific client needs.
2. **Simplicity:** REST is simpler for our needs and integrates well with our existing infrastructure.
3. **Lack of Expertise:** The team has no prior experience operating a GraphQL server in production. 

Given `schema_complexity=low` and `client_diversity=internal_only`, the complexity cost of introducing GraphQL outweighs the benefits.
