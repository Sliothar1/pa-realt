# PA Réalt · "Deep answer · Freagra domhain": plan for a paid AI tier

*Draft for Garry Lohan. Written 9 October 2026 (Europe/Dublin).*

**Status:** design only. The site shows a disabled **"Deep answer · Coming soon"** button in each Ask panel. No payment is taken, no accounts or API keys have been created, and no AI runs on the site. The free **Ask PA Réalt** answers are built in the browser from the site's own data and contain no AI.

This is a planning document, not legal or tax advice. Check the VAT and consumer-law points with an accountant or solicitor before launch.

## 1. What the user gets

A paid "deep answer" is a longer analysis of one monument, for example:
- "Compare this wedge tomb with the others in Co. Clare."
- "What would the midwinter sunset look like from here on the real horizon?"
- "Summarise what the SMR record says, in plain English and in Irish."

Each answer:
- uses only a **grounding pack** assembled by the server (§2.3);
- cites every claim with a link;
- says "not known" when the pack is silent.

## 2. Architecture

```
Browser (static site on GitHub Pages)
  │  1. "Buy 10 deep answers"  → Stripe Checkout (hosted page; card data never touches us)
  │  2. Stripe webhook → serverless: credit 10 answers to an anonymous token (signed, httpOnly cookie)
  │  3. "Deep answer" on a monument → POST /api/deep {smrs, question}  (token in cookie)
  ▼
Serverless function (Vercel Pro or Cloudflare Workers)
  ├─ verify token + remaining credits (KV/Redis); rate-limit (per token, per IP)
  ├─ build grounding pack from the repo's own JSON (site/data/*, notes, RESEARCH.md excerpts)
  ├─ call LLM API (key in server env only) with a strict "answer only from the pack, cite [n]" prompt
  ├─ post-check: every [n] must map to a pack item; reject or regenerate otherwise
  ├─ decrement credit only on success; log {time, smrs, tokens, cost}, no personal data
  └─ return answer + citations
```

### 2.1 Components

- **Static site:** stays on GitHub Pages and is unchanged.
- **Function host:** one of the two options below.
  - **Vercel Pro**, $20/month. The Hobby plan is for personal, non-commercial use only, and taking payments counts as commercial use. Sources: [Vercel Hobby](https://vercel.com/docs/plans/hobby), [Fair use](https://vercel.com/docs/limits/fair-use-guidelines), [Pro](https://vercel.com/docs/plans/pro-plan).
  - **Cloudflare Workers**: the free plan allows 100,000 requests/day; the paid plan is from $5/month ([pricing](https://developers.cloudflare.com/workers/platform/pricing/)). Cheapest at this scale.
- **Payments:** Stripe Checkout, using **credit packs** rather than per-question charges (see §4 for why). A Stripe webhook adds the credits.
- **State:** a small key-value store (Workers KV, or Upstash Redis on Vercel). It holds `token → credits` and the rate-limit counters, and nothing else.

### 2.2 Security and abuse

- **No keys in the browser.** The LLM and Stripe secret keys live only in the function's environment variables. The browser only ever sees the Stripe publishable key, and the Checkout redirect URL.
- **Rate limits** (a sketch):
  - 5 deep answers per minute per token, and 30 per day.
  - Unauthenticated calls: 20 per hour per IP. They get HTTP 402 or 429.
  - A global daily spend cap on the LLM account, with a hard stop and an alert to Garry's email.
- **Abuse controls:**
  - Input is limited to a monument id plus one of about 10 question templates and an optional 200-character free-text field.
  - The grounding pack is server-built, so a user can't inject a pack.
  - The prompt-injection risk is low, but the system prompt still forbids following instructions found inside the pack.
- **Privacy (GDPR):** no accounts. The token is random, and Stripe holds the payment data. The privacy notice must list Stripe and the LLM provider as processors. Choose a provider that doesn't use API data for training.

### 2.3 Grounding pack (the anti-hallucination core)

For monument X, the server assembles:
- the site's record for X: class, county, townland in Irish and English, coordinates;
- the full SMR description (CC BY 4.0) or NI SMR fields (OGL);
- the NMS scope note for its class;
- computed event azimuths and declinations, on a flat horizon, or on the DSM horizon where one exists;
- the relevant RESEARCH.md paragraphs and the verdict for its class;
- nearby monuments within 5 km, from our data;
- for featured sites, the hand-written answers and their sources.

Every item is numbered with its source URL. The model must cite `[n]` after each sentence.

A validator then checks two things:
1. All citations exist.
2. Any numbers (azimuths, dates, distances) appear in the pack.

If either check fails, the server regenerates once, then falls back to "I can't answer that from the data we hold".

## 3. Cost per query (current public API prices)

**Assumptions:** a typical query has about **8,000 input tokens** (the grounding pack plus instructions) and **3,000 output tokens** (answer plus reasoning). Prices are in USD per 1M tokens, standard tier and short context, as listed on 9 October 2026. Euro figures use about €0.86 per $1 (an assumption; check the current rate).

| Model (provider page) | Input $/1M | Output $/1M | Cost per query | ≈ € |
|---|---:|---:|---:|---:|
| [xAI grok-4.3](https://docs.x.ai/developers/pricing) | 1.25 | 2.50 | $0.0175 | €0.015 |
| [xAI grok-4.7](https://docs.x.ai/developers/models) | 2.00 | 6.00 | $0.034 | €0.029 |
| [Google Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/pricing), introductory until 31 Dec 2026 | 0.75 | 3.75 | $0.017 | €0.015 |
| Gemini 3.8 Flash, from 1 Jan 2027 | 1.50 | 7.50 | $0.035 | €0.030 |
| [OpenAI gpt-6.1-sol](https://developers.openai.com/api/docs/pricing) | 2.00 | 10.00 | $0.046 | €0.040 |
| [OpenAI gpt-6-luna](https://developers.openai.com/api/docs/pricing) (small model) | 0.10 | 0.50 | $0.0023 | €0.002 |

- **Caching:** the instruction block and the RESEARCH excerpts are the same across queries, so prompt caching cuts the input cost by a further 75–95% on most providers.
- **Planning figure:** **€0.03–€0.05 per query** for a strong model, including one regeneration in about 1 in 5 queries.
- **Hosting:** €0 (Workers free plan) or about €17/month (Vercel Pro), plus a negligible KV store at this scale.

## 4. Pricing and margins

**Payment fees decide the pricing model.** Stripe in Ireland charges **1.5% + €0.25** per standard EEA card, 2.8% + €0.25 for premium EEA cards, and 3.15% + €0.25 for international cards ([stripe.com/ie/pricing](https://stripe.com/ie/pricing)). Irish VAT at 23% is charged on Stripe's fee, and it can only be reclaimed if you are VAT-registered.

**A single €0.50 charge loses about half to Stripe's fixed fee:** €0.2575, or €0.32 including VAT. So sell credit packs:

| Pack | Price (incl. VAT if registered) | Stripe fee (EEA std, +23% VAT) | LLM cost (€0.04 each) | Net before tax |
|---|---:|---:|---:|---:|
| 5 deep answers | €3 | €0.36 | €0.20 | **€2.44** (81%) |
| 12 deep answers | €6 | €0.42 | €0.48 | **€5.10** (85%) |
| 30 deep answers | €12 | €0.53 | €1.20 | **€10.27** (86%) |

These work out at about **€0.40–€0.60 per answer**, which is in Garry's suggested €0.50–€1 range.
- If Garry is VAT-registered, 23% of the price is output VAT. For example, €6 incl. VAT is €4.88 + €1.12 VAT. That cuts the net, but the VAT on Stripe and API fees becomes reclaimable.
- At €0.04 per query, compute is about 7–10% of revenue. Fees and VAT are the bigger slice.

**Break-even on Vercel Pro (€17/month):** about 4 packs of €6 a month. On Workers it is about 1 pack.

**Free alternative:** donations or "buy me a coffee" avoid most of the consumer-law and VAT work, but give no per-use control.

## 5. Irish tax: sole-trader notes

- **Registration:**
  - Selling deep answers is trading income, so Garry registers as a **sole trader** for income tax (Form TR1 via ROS / myAccount).
  - He files an annual **Form 11** with **preliminary tax**.
  - As a PAYE employee (ATU), side income may already require a Form 11 above small thresholds.
  - Keep records of income, Stripe fees, API bills and hosting.
- **VAT** ([Revenue thresholds](https://www.revenue.ie/en/vat/vat-registration/who-should-register-for-vat/vat-thresholds.aspx)):
  - Registration is obligatory above **€42,500** annual turnover for services. Below that it is optional; registering lets you reclaim VAT on costs, but you then charge 23%.
  - Deep answers are **electronically supplied services**. For EU consumers outside Ireland, Irish VAT applies while total cross-border B2C sales of these services stay under **€10,000** a year (current and preceding year).
  - Above €10,000, VAT is due at each customer's country rate. Use the **Union One-Stop Shop (OSS)** through ROS ([Revenue: electronically supplied services](https://www.revenue.ie/en/vat/vat-on-services/electronic-services/vat-and-electronically-supplied-services/index.aspx)).
  - Stripe Tax can calculate this. It costs extra; check the current fee.
  - UK, US and other non-EU customers follow different rules. Confirm with an accountant before selling outside the EU.
- **ATU:** check the employment contract and ATU policy on outside work and IP, since the site is personal research.

## 6. Consumer law and refunds (Ireland / EU)

- **Consumer Rights Act 2022:** this gives a **14-day right to withdraw** from distance contracts for digital content and services ([s.111](https://www.irishstatutebook.ie/eli/2022/act/37/section/111/enacted/en/html), [s.113](https://www.irishstatutebook.ie/eli/2022/act/37/section/113/enacted/en/html)).
  - For digital content supplied immediately, the right is lost only with the consumer's **prior express consent**, an **acknowledgement** that they lose the right, and the trader's **confirmation** on a durable medium ([CCPC guidance](https://www.ccpc.ie/information-for-businesses/selling-goods-and-services/selling-digital-content-or-services)).
  - Checkout therefore needs a tick-box: "Start my answers now; I understand I lose my 14-day right to withdraw once an answer is delivered." The receipt email confirms it.
  - **Unused credits** in a pack have not been supplied, so offer to refund them on request within 14 days. Garry may simply choose to refund unused credits at any time.
- **Pre-contract information:** Garry's name and contact address, price including VAT, what a "deep answer" is, its limits ("AI-generated from the cited data; may contain errors"), and the complaints route.
- **Conformity:** the service must match its description. If an answer fails validation, or is plainly wrong about our data, refund that credit automatically. Add a "report a problem with this answer" link.
- **Credits:** don't let credits expire quickly. State any expiry clearly, for example 2 years.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **Hallucination** (invented dates, alignments, Irish meanings) | Grounding pack only; every sentence cited; numeric validator; "not known" fallback; never answer townland meanings beyond the pack (link to logainm.ie); show the sources under every answer; label it clearly as AI-written |
| Misrepresenting official bodies | Keep the "not an official NMS/OPW product" disclaimer; quote NMS text with attribution; note the CC BY 4.0 / OGL attribution in each answer |
| Irish-language quality | Generate Irish only from sourced strings (statutory names, NMS terms); no machine-translated free Irish without review |
| Cost spikes / abuse | Prepaid credits only; rate limits; global spend cap; small model fallback |
| Provider price change (e.g. Gemini doubling on 1 Jan 2027) | Provider-agnostic function; review prices quarterly; packs priced with ~10× headroom over compute |
| Payment and legal admin burden | Start with an invite-only beta (free credits, no payments) to test quality, then launch paid packs |
| Heritage harm (encouraging trespass) | Answers always include the access caveat for private land |

## 8. Suggested next steps (not done)

1. Build the grounding-pack builder and validator offline, and test them on 100 monuments with a free or small model.
2. Run an invite-only beta with free credits and a feedback form.
3. Consult an accountant on income-tax/VAT registration and a solicitor on the terms and refund policy.
4. Then create the Stripe account, the function and the KV store, and switch the "Coming soon" button on.
