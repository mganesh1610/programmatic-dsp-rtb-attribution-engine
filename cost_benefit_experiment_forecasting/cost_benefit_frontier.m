% ==============================================================================
% Marginal ROAS Cost-Benefit Frontier & Hill Response Optimization in MATLAB
% ==============================================================================
function [opt_spend, expected_rev] = cost_benefit_frontier(alpha_max, k_half, hill_slope, total_budget)
    n_ch = numel(alpha_max);
    grid = linspace(0.05, 0.60, 200) * total_budget;
    opt_spend = ones(n_ch, 1) * (total_budget / n_ch);
    for iter = 1:50
        grad = (alpha_max .* hill_slope .* (k_half .^ hill_slope) .* (opt_spend .^ (hill_slope - 1))) ./ ...
               ((k_half .^ hill_slope + opt_spend .^ hill_slope) .^ 2);
        opt_spend = total_budget * (grad / sum(grad));
    end
    expected_rev = sum(alpha_max .* (opt_spend .^ hill_slope) ./ (k_half .^ hill_slope + opt_spend .^ hill_slope));
end
