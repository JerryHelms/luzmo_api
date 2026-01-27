# Claude API Billing

## Billing Console

**URL**: [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing)

## How It Works

- Claude API uses **prepaid credits** (not a subscription)
- Credits cover API calls, Workbench, and Claude Code
- Failed requests are not charged
- You can set up **auto-reload** when balance gets low

## Managing Payments

1. Go to **Settings > Billing** in the Anthropic Console
2. Click "Buy credits" to add funds
3. Click the pencil icon to update payment method
4. Set up auto-reload to automatically purchase credits when balance falls below a limit

## Pricing (2026)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude Opus 4.5 | $5 | $25 |
| Claude Sonnet 4.5 | $3 | $15 |
| Claude Haiku 4.5 | $1 | $5 |
| Claude Opus 4.1 | $15 | $75 |

## Cost Optimization

- **Prompt caching** and **batch processing** can reduce costs by up to 90%
- No monthly subscription fee or minimum commitment

## Important Notes

- A Claude Pro/Max subscription is **separate** from API usage - they're billed independently
- Your API key won't function until billing is activated
- If you run out of credits, API access stops until more are purchased

## Resources

- [How do I pay for my Claude API usage?](https://support.claude.com/en/articles/8977456-how-do-i-pay-for-my-claude-api-usage)
- [How will I be billed?](https://support.anthropic.com/en/articles/8114526-how-will-i-be-billed)
- [Why separate billing for API vs subscription?](https://support.anthropic.com/en/articles/9876003-i-subscribe-to-a-paid-claude-ai-plan-why-do-i-have-to-pay-separately-for-api-usage-on-console)
