# Sprint Planning — March 10, 2026

**Sprint:** March 10 - March 24
**Capacity:** Riley Patel out Mar 12-13 (conference). Full capacity otherwise.

## Sprint Goals
1. Ship version history MVP — users can snapshot and restore previous generations
2. Launch credit usage dashboard for Pro/Team tier users
3. Custom domain linking — unblock beta partners waiting on branded deploy URLs

## Proposed Scope

### Must-have (P0)
| Ticket | Description | Owner | Estimate |
|--------|-------------|-------|----------|
| EXAMPLE_PRODUCT-1071 | Version history: snapshot on generation | Morgan Wu | 3d |
| EXAMPLE_PRODUCT-1072 | Version history: diff view between snapshots | Morgan Wu | 2d |
| EXAMPLE_PRODUCT-1085 | Credit usage dashboard: aggregate usage API | Sam Chen | 3d |
| EXAMPLE_PRODUCT-1086 | Credit usage dashboard: frontend charts + breakdown table | Taylor Brooks / Jordan Kim | 4d |
| EXAMPLE_PRODUCT-1090 | Custom domains: DNS verification flow | Riley Patel | 3d |

### Should-have (P1)
| Ticket | Description | Owner | Estimate |
|--------|-------------|-------|----------|
| EXAMPLE_PRODUCT-1093 | Credit usage: export to CSV | Jordan Kim | 1d |
| EXAMPLE_PRODUCT-1095 | Version history: bulk delete old snapshots | Morgan Wu | 1d |
| EXAMPLE_PRODUCT-1098 | Analytics event tracking for credit dashboard interactions | Casey Nguyen | 2d |

## Carry-over from Last Sprint
| Ticket | Description | Why carried | Remaining |
|--------|-------------|-------------|-----------|
| EXAMPLE_PRODUCT-1042 | Prototype sharing: password-protected links | Blocked on auth service deploy; unblocked now | 1d |
| EXAMPLE_PRODUCT-1060 | Fix prompt editor autosave race condition | Discovered edge case late in sprint | 0.5d |

## Risks & Dependencies
- **Credit usage API** depends on the billing service team (Platform) shipping the new usage endpoint by Mar 12. Sam has confirmed they're on track but no staging environment yet.
- **Custom domains** requires DevOps to provision wildcard TLS certs. Ticket filed (INFRA-412) but not yet prioritized on their board.

## Questions to Resolve
- Do we scope version history to only AI-generated outputs, or include manual edits too? Need product call on this before Morgan starts.
- Credit dashboard: do we show real-time usage or batch-updated (hourly)? Real-time adds ~2d of work.
