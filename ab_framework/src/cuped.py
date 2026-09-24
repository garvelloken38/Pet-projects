import pandas as pd
import numpy as np
from src.analysis import analyze_experiment      



def apply_cuped(df: pd.DataFrame, metric_col: str = "post_metric", covariate_col: str = "pre_metric") -> pd.DataFrame:
    
    df = df.copy()
    
    y = df[metric_col]
    x = df[covariate_col]
    
    theta = np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1)
    
    x_mean = x.mean()
    df[f"{metric_col}_cuped"] = y - theta * (x - x_mean)
    
    df.attrs["cuped_theta"] = float(theta)
    
    return df


def analyze_with_cuped(df: pd.DataFrame, metric_col: str = "post_metric", covariate_col: str = "pre_metric", group_col: str = "group", 
                       control_name: str = "control", treatment_name: str = "treatment", alpha: float = 0.0 ) -> dict:
    
    result_raw = analyze_experiment( df, metric_col=metric_col, group_col=group_col, control_name=control_name, 
                                    treatment_name=treatment_name, alpha=alpha)
    
    df_cuped = apply_cuped(df, metric_col=metric_col, covariate_col=covariate_col)
    
    result_cuped = analyze_experiment(df_cuped, metric_col=f"{metric_col}_cuped", group_col=group_col, control_name=control_name, 
                                      treatment_name=treatment_name, alpha=alpha)
    
    theta = df_cuped.attrs.get("cuped_theta", None)
    
    var_reduction = 1 - (result_cuped["std_control"]**2 / result_raw["std_control"]**2)
    
    corr = df[metric_col].corr(df[covariate_col])
    
    result = {
        "theta": theta,
        "correlation_pre_post": float(corr),
        "variance_reduction_approx": float(var_reduction),
        
        "raw": result_raw,
        "cuped": result_cuped,
        
        "p_value_raw": result_raw["p_value"],
        "p_value_cuped": result_cuped["p_value"],
        "abs_uplift_raw": result_raw["abs_uplift"],
        "abs_uplift_cuped": result_cuped["abs_uplift"],
        "ci_raw": (result_raw["ci_left"], result_raw["ci_right"]),
        "ci_cuped": (result_cuped["ci_left"], result_cuped["ci_right"]),
    }
    
    return result


def print_cuped_report(result: dict) -> None:
    
    print("CUPED Analysis Report")
    
    print(f"theta:                    {result['theta']:.4f}")
    print(f"Корреляция pre - post:        {result['correlation_pre_post']:.3f}")
    print(f"Приближённое снижение дисперсии:  {result['variance_reduction_approx']:.1%}")
    
    print(f"{'Метрика':<25} {'Обычный':>12} {'CUPED':>12}")
    print(f"{'Absolute uplift':<25} {result['abs_uplift_raw']:>12.4f} {result['abs_uplift_cuped']:>12.4f}")
    print(f"{'p-value':<25} {result['p_value_raw']:>12.6f} {result['p_value_cuped']:>12.6f}")
    
    ci_raw = result["ci_raw"]
    ci_cuped = result["ci_cuped"]
    print(f"{'95% CI left':<25} {ci_raw[0]:>12.4f} {ci_cuped[0]:>12.4f}")
    print(f"{'95% CI right':<25} {ci_raw[1]:>12.4f} {ci_cuped[1]:>12.4f}")
    
    width_raw = ci_raw[1] - ci_raw[0]
    width_cuped = ci_cuped[1] - ci_cuped[0]
    print(f"{'Ширина CI':<25} {width_raw:>12.4f} {width_cuped:>12.4f}")
    
    improvement = (width_raw - width_cuped) / width_raw if width_raw != 0 else 0
    print(f"CI стал уже на:               {improvement:.1%}")
