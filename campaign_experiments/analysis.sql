SELECT segment, COUNT(*) AS assigned, SUM(conversion) AS conversions,
       SUM(visit) AS visits, SUM(spend) AS total_spend,
       AVG(conversion) AS conversion_rate, AVG(spend) AS spend_per_assigned
FROM assigned_outcomes
GROUP BY segment
ORDER BY segment;
