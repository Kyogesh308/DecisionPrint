# Architecture Review Board — Messaging Decision
**Date:** 2024-05-10
**Type:** meeting_transcript
**Attendees:** Marcus Chen (chair), Raj Patel, David Kim, Elena Vasquez

**Marcus Chen:** Alright, let's move to the next item. Raj, ADR-007 on the message broker. You're proposing RabbitMQ over Kafka. Walk us through it.

**Raj Patel:** Yeah, so the architecture doc, SRC-ALPHA-001, goes into detail, but basically, Kafka is just way too heavy for what we need right now. We have exactly two consumers. The traffic is moderate. We don't need replay capabilities. 

**Elena Vasquez:** What about future proofing? I know Nova is a long way off, but if we start doing more async stuff...

**Raj Patel:** We can cross that bridge when we get to it. Right now, async_workflows is effectively false. We just need to decouple notifications.

**David Kim:** I want to strongly second Raj's proposal here. From an infrastructure perspective, we only have 3 SREs. Kafka needs at least a dedicated person to manage it properly, handle partitions, upgrades... it's a beast. I cannot commit my team to supporting Kafka right now. 

**Marcus Chen:** David, is RabbitMQ that much easier?

**David Kim:** Comparatively, yes. It's a standard deployment, fewer moving parts for a basic setup. We can manage it within our current ops_capacity=small constraint. If we tried Kafka, we'd be setting ourselves up for an outage.

**Elena Vasquez:** Okay, fair enough. As long as we document that this is a tactical decision for our current scale. 

**Raj Patel:** Exactly. I've noted in the ADR that if we ever need event sourcing or if the consumer count explodes, we'll have to migrate. But for Project Alpha, RabbitMQ is the only realistic option.

**Marcus Chen:** Makes sense. We follow the ponytail philosophy here — shortest working diff. Let's not build for a scale we don't have. I'm approving ADR-007.

**Action Items:**
- Raj: Finalize RabbitMQ deployment manifests.
- David: Provision staging RabbitMQ cluster.
