# Q3 2025 Infrastructure Retrospective
**Date:** 2025-10-01
**Type:** retro
**Author:** Tom Bradley

## Review
This quarter was dominated by the fallout from the July 22 database incident. The primary lesson learned was the critical importance of reliable, tested backups. 

While the cost optimization initiative in Q2 (DEC-DELTA-001) was well-intentioned given the business climate, it ultimately cost us more in engineering time and customer trust than it saved in AWS bills. We have since reinstated automated backups and implemented regular disaster recovery drills.

Moving forward, any proposed cost-cutting measures that affect infrastructure redundancy or data durability must go through a formal risk assessment review board.
