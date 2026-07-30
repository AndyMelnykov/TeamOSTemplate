# Bi-Weekly Product Review - Transcript Excerpt
**Date:** March 4, 2026

---

**Alex Chen:** Alright, let's get started. Jordan, want to kick us off with the deploy update?

**Jordan Reeves:** Sure. So deploy infra is live on staging. Vercel and Netlify integrations are both working. The preview UI in the editor is functional - the team has been using it internally for the last week and it feels pretty good. The main gap right now is the custom domain configuration flow. DNS propagation handling has some edge cases that are taking longer than expected.

**Alex:** What's the impact on the March 24 beta target?

**Jordan:** It's tight but I think we can make it. The custom domain piece isn't a blocker for the initial beta - we can launch with example_product-managed subdomains first and add custom domains in a fast follow. The bigger concern is error handling. Sam, where are we on that?

**Sam Torres:** We've got the happy path covered. Where we need more work is graceful handling of build failures, timeout scenarios, and the retry flow. I'd estimate about a week of focused work.

**Alex:** OK, let's make sure that's prioritized this sprint. Priya, can you give us the latency update?

**Priya Patel:** Yeah, so the good news is example_product-gen-3.2 quality scores are up 12% across our eval suite. The bad news is P95 latency went from 7.5 seconds to 11 seconds. The model is just heavier. Streaming helps with perceived performance but the raw numbers need to come down.

**Alex:** What are our options?

**Priya:** Three paths. One, roll back to 3.1 for latency-sensitive flows. Two, optimize the inference pipeline - I think there's room to get 30-40% improvement with batching and caching changes. Three, accept the tradeoff and lean on streaming.

**Grace Lin:** From a metrics perspective, I'd push for option two. Our data shows generation time is the number one complaint in recent NPS feedback. Going backwards on that would be rough.

**Alex:** Agreed. Priya, let's do the optimization sprint. Give us a plan by Friday. If we're not under 8 seconds by the 18th, we'll do the model toggle as a fallback.

**Priya:** Sounds good. I'll have the plan by Friday.

---

*[Transcript truncated for brevity]*
