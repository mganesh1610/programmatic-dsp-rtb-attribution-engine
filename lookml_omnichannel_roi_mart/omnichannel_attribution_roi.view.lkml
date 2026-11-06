view: omnichannel_attribution_roi {
  sql_table_name: `marketing_analytics.fact_omnichannel_attribution_cohorts` ;;
  drill_fields: [channel, campaign_id, attributed_conversions, shapley_weight, markov_removal_effect, attributed_cac, incremental_roas]

  dimension: channel {
    type: string
    sql: ${TABLE}.channel ;;
    description: "Omni-channel marketing touchpoint (Paid Search, Display, Paid Social, Video, Email, Affiliate)"
  }

  dimension: campaign_id {
    type: string
    sql: ${TABLE}.campaign_id ;;
  }

  dimension: experiment_arm {
    type: string
    sql: ${TABLE}.experiment_arm ;;
    description: "Randomized holdout assignment (Treatment vs. Control)"
  }

  measure: total_spend {
    type: sum
    sql: ${TABLE}.spend_usd ;;
    value_format_name: usd
  }

  measure: attributed_orders {
    type: sum
    sql: ${TABLE}.retained_orders ;;
    value_format_name: decimal_1
  }

  measure: attributed_cac {
    type: number
    sql: SAFE_DIVIDE(${total_spend}, NULLIF(${attributed_orders}, 0)) ;;
    value_format_name: usd
    description: "Shapley- and Markov-blended Customer Acquisition Cost (CAC) per retained order"
  }

  measure: replay_cpc_savings_pct {
    type: average
    sql: ${TABLE}.cpc_reduction_pct ;;
    value_format_name: percent_2
  }
}
