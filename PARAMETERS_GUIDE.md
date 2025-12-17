# Multi-Tenant Parameter Support Guide

## Current Situation

Your Luzmo dashboards use parameter tokens for multi-tenant data filtering. Example from "Arkansas Work Order Details":

```json
{
  "parameter": "metadata.accountId",
  "type": "hierarchy",
  "value": "a1796777-a003-4ee8-8964-b8e251da30a5"
}
```

## What Works Now

✓ **Dashboard Metadata Analysis** - No parameter issues
  - Dashboard structure
  - Chart types and configuration
  - Filter definitions
  - Layout and views
  - Parameter definitions themselves

## What Needs Parameters

✗ **Actual Data Queries** - Requires parameter values
  - Chart data values
  - Metrics and KPIs
  - Trend data
  - Aggregations

## How Luzmo Parameters Work

When you embed a Luzmo dashboard or query data via API, you need to provide parameter values that match your multi-tenant setup:

```javascript
// Example: Luzmo Embedding
Luzmo.on('ready', function() {
  Luzmo.setTokens({
    'metadata.accountId': 'specific-account-id'
  });
});
```

## Implementation Options

### Option 1: Structure-Only Analysis (Current)

**What you get:**
- Dashboard inventory and organization
- Chart types and configurations
- Filter and parameter definitions
- Dashboard layout analysis

**What you DON'T get:**
- Actual data values
- Trends and metrics
- Data-driven insights

**Best for:**
- Dashboard catalog/inventory
- Understanding dashboard structure
- Documentation generation
- Template analysis

### Option 2: Add Parameter Support (Recommended)

**Required Changes:**

1. **Update LuzmoClient to accept parameters**
   ```python
   def get_chart_data(self, chart_id: str, parameters: Dict[str, str] = None):
       # Pass parameters in data query
   ```

2. **Update DashboardAnalyzer to pass parameters**
   ```python
   def get_full_dashboard_data(self, dashboard_id: str, parameters: Dict[str, str] = None):
       # Use parameters when fetching chart data
   ```

3. **Update Pipeline to accept tenant context**
   ```python
   pipeline.generate_summary(
       dashboard_id="...",
       parameters={"metadata.accountId": "specific-account-id"}
   )
   ```

### Option 3: Multi-Tenant Batch Analysis

Analyze dashboards across multiple tenants:

```python
tenants = [
    {"id": "tenant-1", "accountId": "uuid-1"},
    {"id": "tenant-2", "accountId": "uuid-2"}
]

for tenant in tenants:
    pipeline.generate_summary(
        dashboard_id=dashboard_id,
        parameters={"metadata.accountId": tenant["accountId"]},
        output_prefix=f"{tenant['id']}_"
    )
```

## Recommendation

**For your use case (multi-tenant SaaS):**

1. **Start with Option 1** (current implementation)
   - Use it to understand dashboard structure
   - Build a catalog of all dashboards
   - Document what each dashboard shows

2. **Upgrade to Option 2** when you need:
   - Actual data analysis
   - Tenant-specific insights
   - Data-driven summaries
   - Comparative analysis across tenants

## Next Steps

If you want to implement Option 2, we need to:

1. Research Luzmo's data query API to understand how to pass parameters
2. Update the `LuzmoClient` methods that fetch chart data
3. Add parameter support throughout the pipeline
4. Test with a specific tenant's accountId

Would you like me to implement parameter support, or is the current structure-only analysis sufficient for your needs?
