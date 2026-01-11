"""
A/B Test Manager - Runs statistically rigorous A/B tests
CRITICAL: Enforces sample size calculation and minimum test duration
"""

import math
import json
from datetime import datetime, timedelta
from scipy import stats

def calculate_required_sample_size(baseline_rate, min_detectable_effect, alpha=0.05, power=0.80):
    """
    Calculate required sample size for A/B test
    
    Args:
        baseline_rate: Current conversion rate (e.g., 0.10 for 10%)
        min_detectable_effect: Minimum improvement to detect (e.g., 0.02 for 2%)
        alpha: Significance level (default 0.05 for 95% confidence)
        power: Statistical power (default 0.80)
    
    Returns:
        Required sample size per variant
    """
    # Z-scores for alpha and power
    z_alpha = stats.norm.ppf(1 - alpha/2)  # Two-tailed test
    z_beta = stats.norm.ppf(power)
    
    p1 = baseline_rate
    p2 = baseline_rate + min_detectable_effect
    p_pooled = (p1 + p2) / 2
    
    # Sample size formula for proportions
    n = (2 * p_pooled * (1 - p_pooled) * (z_alpha + z_beta)**2) / (p2 - p1)**2
    
    return math.ceil(n)

def bonferroni_correction(alpha, num_tests):
    """Apply Bonferroni correction for multiple testing"""
    return alpha / num_tests

class ABTest:
    def __init__(self, test_name, variant_a, variant_b, baseline_rate=0.10):
        self.test_name = test_name
        self.variant_a = variant_a
        self.variant_b = variant_b
        self.baseline_rate = baseline_rate
        self.start_date = datetime.now()
        self.min_duration_days = 7  # CRITICAL: Minimum 7 days
        
        # Calculate required sample size
        self.required_sample_size = calculate_required_sample_size(
            baseline_rate=baseline_rate,
            min_detectable_effect=0.02,  # Detect 2% improvement
            alpha=0.05,
            power=0.80
        )
        
        # Initialize results
        self.results = {
            "variant_a": {"impressions": 0, "conversions": 0},
            "variant_b": {"impressions": 0, "conversions": 0}
        }
        
        # Data provenance
        self.provenance = {
            "source": "ab_test_system",
            "created_at": self.start_date.isoformat(),
            "validated_by": "statistical_framework",
            "test_parameters": {
                "baseline_rate": baseline_rate,
                "min_detectable_effect": 0.02,
                "alpha": 0.05,
                "power": 0.80,
                "required_sample_size": self.required_sample_size,
                "min_duration_days": self.min_duration_days
            }
        }
    
    def record_result(self, variant, converted):
        """Record a test result"""
        if variant not in ["a", "b"]:
            raise ValueError("Variant must be 'a' or 'b'")
        
        variant_key = f"variant_{variant}"
        self.results[variant_key]["impressions"] += 1
        if converted:
            self.results[variant_key]["conversions"] += 1
    
    def get_conversion_rates(self):
        """Calculate current conversion rates"""
        rate_a = (self.results["variant_a"]["conversions"] / 
                 self.results["variant_a"]["impressions"] 
                 if self.results["variant_a"]["impressions"] > 0 else 0)
        
        rate_b = (self.results["variant_b"]["conversions"] / 
                 self.results["variant_b"]["impressions"] 
                 if self.results["variant_b"]["impressions"] > 0 else 0)
        
        return rate_a, rate_b
    
    def is_statistically_significant(self, alpha=0.05):
        """Check if results are statistically significant"""
        n_a = self.results["variant_a"]["impressions"]
        n_b = self.results["variant_b"]["impressions"]
        x_a = self.results["variant_a"]["conversions"]
        x_b = self.results["variant_b"]["conversions"]
        
        if n_a == 0 or n_b == 0:
            return False, 1.0
        
        # Two-proportion z-test
        p_a = x_a / n_a
        p_b = x_b / n_b
        p_pooled = (x_a + x_b) / (n_a + n_b)
        
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_a + 1/n_b))
        
        if se == 0:
            return False, 1.0
        
        z_score = (p_b - p_a) / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed
        
        return p_value < alpha, p_value
    
    def can_declare_winner(self):
        """
        CRITICAL: Check if test can be concluded
        Requires BOTH sufficient sample size AND minimum duration
        """
        # Check 1: Minimum duration (7 days)
        days_running = (datetime.now() - self.start_date).days
        if days_running < self.min_duration_days:
            return False, f"Test running for {days_running} days (need {self.min_duration_days})"
        
        # Check 2: Sufficient sample size
        min_sample = min(
            self.results["variant_a"]["impressions"],
            self.results["variant_b"]["impressions"]
        )
        
        if min_sample < self.required_sample_size:
            return False, f"Sample size {min_sample} (need {self.required_sample_size})"
        
        # Check 3: Statistical significance
        is_sig, p_value = self.is_statistically_significant()
        if not is_sig:
            return False, f"Not statistically significant (p={p_value:.4f})"
        
        return True, "All criteria met"
    
    def get_winner(self):
        """Determine winner with practical significance check"""
        can_declare, reason = self.can_declare_winner()
        
        if not can_declare:
            return None, reason
        
        rate_a, rate_b = self.get_conversion_rates()
        improvement = (rate_b - rate_a) / rate_a if rate_a > 0 else 0
        
        # CRITICAL: Check practical significance (20% improvement threshold)
        if abs(improvement) < 0.20:
            return None, f"Improvement {improvement:.1%} below 20% threshold (marginal)"
        
        winner = "b" if rate_b > rate_a else "a"
        
        return winner, {
            "winner": winner,
            "improvement": improvement,
            "rate_a": rate_a,
            "rate_b": rate_b,
            "statistical_significance": True,
            "practical_significance": abs(improvement) >= 0.20,
            "days_running": (datetime.now() - self.start_date).days,
            "sample_size_a": self.results["variant_a"]["impressions"],
            "sample_size_b": self.results["variant_b"]["impressions"]
        }
    
    def save_results(self):
        """Save test results with provenance"""
        results_file = f"ab_test_{self.test_name}_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(results_file, "w") as f:
            json.dump({
                "test_name": self.test_name,
                "start_date": self.start_date.isoformat(),
                "results": self.results,
                "provenance": self.provenance,
                "winner": self.get_winner()
            }, f, indent=2)
        
        return results_file

# Example usage
if __name__ == "__main__":
    # Create test
    test = ABTest(
        test_name="gatekeeper_script_v2",
        variant_a="current_script",
        variant_b="new_gatekeeper_handling",
        baseline_rate=0.10
    )
    
    print(f"A/B Test: {test.test_name}")
    print(f"Required sample size: {test.required_sample_size} per variant")
    print(f"Minimum duration: {test.min_duration_days} days")
    print(f"\nTest will conclude when BOTH criteria are met.")
