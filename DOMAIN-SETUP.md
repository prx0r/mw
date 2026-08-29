# Domain Setup Notes — 2026-08-29

## Status: NOT YET DONE

## What We Know

### Porkbun (where moltwork.com is registered)
- API: `https://porkbun.com/api/json/v3`
- Auth: `apikey` + `secretapikey` in POST body
- Client code exists in `prx0r/tomzoho/src/client/porkbun.ts`
- No API credentials found in any repo (all .env.example only)

### Cloudflare (where we want to host)
- Account ID: `REDACTED`
- API Token: `REDACTED — see .env`
- Already deployed: `oracle.tradesprior.workers.dev`

### What Needs to Happen
1. Get Porkbun API key + secret from user
2. Either:
   a. Transfer moltwork.com nameservers to Cloudflare, OR
   b. Add Cloudflare nameservers as custom nameservers in Porkbun
3. Add DNS records in Cloudflare for `oracle.moltwork.com`
4. Point to our worker

### Repos Found
- `prx0r/tomzoho` — Zoho mail/domain management (has Porkbun client)
- `prx0r/finalbuildsdomain` — Domain automation (has .env.example)

### Blocked On
- Need Porkbun API credentials from user
- Need user to confirm they own moltwork.com on Porkbun
