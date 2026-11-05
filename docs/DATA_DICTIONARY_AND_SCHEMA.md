# Data Dictionary & Schema Reference

## 1. Primary Public Datasets & Benchmarks
1. **Criteo Attribution Dataset for Online Advertising (`criteo_attribution_dataset`)**
   - **URL:** `https://ailab.criteo.com/criteo-attribution-modeling-bidding-dataset/` (Hugging Face mirror: `https://huggingface.co/datasets/criteo/criteo-attribution-dataset`)
   - **Scale:** `16.4M+` impression events (`250,000+` stratified programmatic auction & conversion journey sample used in local validation)
   - **Key Columns:** `timestamp`, `uid`, `campaign`, `conversion`, `conversion_timestamp`, `conversion_id`, `attribution`, `click`, `click_pos`, `click_nb`, `cost`, `cpo`, `time_since_last_click`, `cat1..cat9`
2. **iPinYou Real-Time Bidding (RTB) DSP Auction Dataset**
   - **URL:** `https://www.kaggle.com/datasets/lastsummer/ipinyou`
   - **Scale:** `19.5M+` bid requests, `14.7K` clicks, clearing prices, and bid floor logs across multiple advertiser verticals (`E-Commerce & Retail`, `Automotive`, `Entertainment`, `Consumer Tech`)
   - **Key Columns:** `BidID`, `Timestamp`, `LogType`, `iPinYouID`, `UserAgent`, `IP`, `Region`, `City`, `AdExchange`, `Domain`, `AdSlotID`, `AdSlotWidth`, `AdSlotHeight`, `AdSlotVisibility`, `AdSlotFormat`, `AdSlotFloorPrice`, `CreativeID`, `BiddingPrice`, `PayingPrice`, `AdvertiserID`, `UserProfileIDs`
3. **GA4 Public BigQuery E-Commerce Event Export (`bigquery-public-data.ga4_obfuscated_sample_ecommerce`)**
   - **URL:** `https://console.cloud.google.com/marketplace/product/obfuscated-ga360-data/obfuscated-ga4`
   - **Scale:** Multi-table nested event stream (`event_name`, `user_pseudo_id`, `traffic_source.medium`, `traffic_source.source`, `ecommerce.purchase_revenue_in_usd`, `device.category`, `geo.country`)

## 2. Core Analytical Tables
- `dim_campaigns`: `campaign_id`, `trading_desk_id`, `vertical`, `deal_type` (`Open Exchange`, `PMP`, `PG`), `daily_budget_usd`, `target_cpa_usd`, `floor_cpm_usd`, `status`
- `fct_rtb_auctions`: `auction_id`, `campaign_id`, `event_date`, `floor_cpm_usd`, `unshaded_bid_cpm_usd`, `shaded_bid_cpm_usd`, `clearing_cpm_usd`, `shading_factor`, `is_won`, `clicks`, `conversions`
- `fct_ad_verification`: `campaign_id`, `event_date`, `verification_vendor` (`IAS`, `DoubleVerify`, `MOAT`), `viewability_rate`, `ivt_rate`, `video_completion_rate`, `vast_error_rate`
- `marketing_monthly`: `month_start`, `channel` (`Display`, `Paid Search`, `Paid Social`, `Affiliate`, `Email`), `spend`, `retained_orders`, `contribution`, `attributed_cac`
