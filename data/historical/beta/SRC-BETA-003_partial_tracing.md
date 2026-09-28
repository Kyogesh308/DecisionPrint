# API Gateway Tracing — Implementation Note
**Date:** 2024-12-10
**Type:** implementation_note
**Author:** David Kim

## Context
As the number of services has grown during Project Beta, our `logs_only` observability strategy is showing cracks.

- **debugging_frequency=daily**: We're spending too much time debugging cross-service issues in the API gateway. Following correlation IDs through thousands of log lines across different services is becoming tedious.

## Update
We are updating our strategy to **observability_maturity=partial_tracing**. 

We have instrumented the API Gateway and the two most critical backend services (Order and Auth) with OpenTelemetry, exporting to AWS X-Ray. This will give us a visual waterfall of request latency and failure points for our most complex workflows, without requiring a massive project to instrument every single microservice.
