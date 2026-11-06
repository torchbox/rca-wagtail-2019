# Cloudflare Worker

`caching-worker.mjs` contains the reviewed Worker source. The new caching policy
applies only to `www.rca.ac.uk`; other hostnames retain the existing policy.
Deployment is separate from application deployment.

See the [cache design, local checks and rollout instructions](../../docs/cloudflare-caching.md).
