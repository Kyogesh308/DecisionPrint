# Authentication Architecture — OAuth2/OIDC
**Date:** 2024-07-15
**Type:** architecture_doc
**Author:** Tom Bradley

## Decision
We will standardize on OAuth2 with OpenID Connect (OIDC) for all internal and external authentication flows.

## Rationale
Moving away from custom JWT implementations to a standardized protocol improves security and allows easier integration with third-party identity providers in the future.
