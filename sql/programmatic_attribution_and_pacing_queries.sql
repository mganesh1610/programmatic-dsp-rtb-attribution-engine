-- =============================================================================
-- Programmatic DSP Bid Shading, Pacing Diagnostics & Multi-Touch Attribution SQL
-- Dialect: Standard SQL / BigQuery / Snowflake (Uses SQL Joins & CTEs)
-- =============================================================================

-- 1. Intraday Campaign Pacing, Bid Shading Win-Rate & eCPM Floor Diagnostics
WITH campaign_daily_targets AS (
    SELECT
        c.campaign_id,
        c.trading_desk_id,
        c.vertical,
        c.deal_type,
        c.daily_budget_usd,
        c.target_cpa_usd,
        c.floor_cpm_usd
    FROM programmatic_analytics.dim_campaigns AS c
    WHERE c.status = 'ACTIVE'
),
auction_delivery_agg AS (
    SELECT
        a.campaign_id,
        a.event_date,
        COUNT(*) AS bid_requests,
        SUM(CASE WHEN a.is_won = 1 THEN 1 ELSE 0 END) AS impressions_won,
        SUM(CASE WHEN a.is_won = 1 THEN a.clearing_cpm_usd / 1000.0 ELSE 0.0 END) AS spend_usd,
        AVG(CASE WHEN a.is_won = 1 THEN a.unshaded_bid_cpm_usd END) AS avg_unshaded_bid_cpm,
        AVG(CASE WHEN a.is_won = 1 THEN a.shaded_bid_cpm_usd END) AS avg_shaded_win_cpm,
        SUM(a.clicks) AS clicks,
        SUM(a.conversions) AS conversions
    FROM programmatic_analytics.fct_rtb_auctions AS a
    GROUP BY a.campaign_id, a.event_date
),
verification_qa_agg AS (
    SELECT
        v.campaign_id,
        v.event_date,
        AVG(v.viewability_rate) AS viewability_rate,
        AVG(v.ivt_rate) AS ivt_rate,
        AVG(v.video_completion_rate) AS vcr_rate
    FROM programmatic_analytics.fct_ad_verification AS v
    GROUP BY v.campaign_id, v.event_date
)
SELECT
    t.campaign_id,
    t.trading_desk_id,
    t.vertical,
    t.deal_type,
    d.event_date,
    d.impressions_won,
    ROUND(d.spend_usd, 2) AS actual_spend_usd,
    t.daily_budget_usd,
    ROUND((t.daily_budget_usd - d.spend_usd) / NULLIF(t.daily_budget_usd, 0) * 100.0, 2) AS pacing_underdelivery_pct,
    ROUND(d.avg_shaded_win_cpm, 2) AS realized_ecpm_usd,
    ROUND((d.avg_unshaded_bid_cpm - d.avg_shaded_win_cpm) / NULLIF(d.avg_unshaded_bid_cpm, 0) * 100.0, 2) AS bid_shading_savings_pct,
    ROUND(d.spend_usd / NULLIF(d.conversions, 0), 2) AS realized_cpa_usd,
    ROUND(q.viewability_rate * 100.0, 2) AS viewability_pct,
    ROUND(q.ivt_rate * 100.0, 2) AS ivt_pct,
    ROUND(q.vcr_rate * 100.0, 2) AS vcr_pct
FROM campaign_daily_targets AS t
INNER JOIN auction_delivery_agg AS d
    ON t.campaign_id = d.campaign_id
LEFT JOIN verification_qa_agg AS q
    ON t.campaign_id = q.campaign_id
   AND d.event_date = q.event_date
ORDER BY d.event_date DESC, actual_spend_usd DESC;

-- 2. Omnichannel Marketplace Spend-to-Sales & Retained Order CAC Reconciliation
SELECT
    channel,
    SUM(spend) AS spend_usd,
    SUM(retained_orders) AS retained_orders,
    SUM(contribution) AS contribution_usd,
    ROUND(SUM(spend) / NULLIF(SUM(retained_orders), 0), 2) AS attributed_cac_usd
FROM marketplace_analytics.marketing_monthly
WHERE month_start = DATE '2026-09-01'
GROUP BY channel
ORDER BY attributed_cac_usd ASC;
