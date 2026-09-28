# Nova Kickoff — Event Architecture Planning
**Date:** 2026-02-03
**Type:** meeting_transcript
**Attendees:** Elena Vasquez (chair), Raj Patel, David Kim, Lisa Nguyen, Priya Sharma

**Elena Vasquez:** Okay, let's get started. This is the initial architecture sync for Project Nova. Lisa, do you want to quickly summarize the product requirements?

**Lisa Nguyen:** Sure. Nova is all about visibility and auditing. Our enterprise B2B customers need absolute tracking of every logistics event. The biggest new requirement is a verifiable audit trail for compliance purposes. Every state change in the system must be recorded and replayable. 

**Raj Patel:** Okay, that changes things fundamentally. The landscape has completely changed since Alpha. If we need an audit trail, we're talking `replay_required=true`. RabbitMQ is not built for that. 

**Elena Vasquez:** Right. And what about scale?

**Lisa Nguyen:** We're projecting a massive increase in volume as we onboard the new tier-1 clients. Expecting around 5000 events/sec peak.

**Priya Sharma:** That's `traffic_volume=high`. Are we sure our current messaging infrastructure can handle that?

**Raj Patel:** Absolutely not. With the new microservices planned for Nova, our `consumer_count` is jumping to at least 15. Plus, `async_workflows=true` is now a core pattern, not an exception. We have 14 distinct async workflows identified already. RabbitMQ will fall over. We need to move to Kafka.

**David Kim:** Let's talk about ops. In Alpha, we rejected Kafka because my team couldn't handle it. But things are different now. We now have 8 SREs, and two of them actually have extensive Kafka experience from their previous roles. Kafka is manageable now. I'm comfortable upgrading our `ops_capacity` constraint to `medium`.

**Elena Vasquez:** That's great news, David. So, to summarize the new constraints for Nova: consumer_count=15, replay_required=true, traffic_volume=high, ops_capacity=medium, async_workflows=true. 

**Raj Patel:** I'll draft the technical requirements document based on these constraints. It's a clear mandate for an event streaming platform, and Kafka is the obvious choice.

**Action Items:**
- Raj: Draft Nova Event Platform Technical Requirements.
- David: Start preliminary sizing for a Kafka cluster.
