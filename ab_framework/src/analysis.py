import pandas as pd
import numpy as np
from scipy import stats


def analyze_experiment(df: pd.DataFrame, metric_col: str = "post_metric", group_col: str = "group", control_name: str = "control", treatment_name: str = "treatment",
    alpha: float = 0.05) -> dict:
    
    control = df[df[group_col] == control_name][metric_col].dropna()
    treatment = df[df[group_col] == treatment_name][metric_col].dropna()
    
    n_control = len(control)
    n_treatment = len(treatment)
    
    mean_control = control.mean()
    mean_treatment = treatment.mean()
    
    std_control = control.std(ddof=1)
    std_treatment = treatment.std(ddof=1)
    
    # === Uplift ===
    abs_uplift = mean_treatment - mean_control
    rel_uplift = abs_uplift / mean_control if mean_control != 0 else np.nan
    
    # не предполагаем равные дисперсии
    t_stat, p_value = stats.ttest_ind(treatment,control, equal_var=False, alternative="two-sided")
    
    # Доверительный интервал
    # df по Уэлчу
    se = np.sqrt(std_control**2 / n_control + std_treatment**2 / n_treatment)
    
    df_welch = (std_control**2 / n_control + std_treatment**2 / n_treatment)**2 / (
        (std_control**2 / n_control)**2 / (n_control - 1) +
        (std_treatment**2 / n_treatment)**2 / (n_treatment - 1)
    )
    
    t_crit = stats.t.ppf(1 - alpha / 2, df_welch)
    
    ci_left = abs_uplift - t_crit * se
    ci_right = abs_uplift + t_crit * se
    
    # Вывод
    is_significant = p_value < alpha
    
    if is_significant:
        direction = "положительный" if abs_uplift > 0 else "отрицательный"
        verdict = f"Есть статистически значимый {direction} эффект"
    else:
        verdict = "Статистически значимого эффекта нет"
    
    result = {
        "mean_control": float(mean_control),
        "mean_treatment": float(mean_treatment),
        "abs_uplift": float(abs_uplift),
        "rel_uplift": float(rel_uplift),
        "p_value": float(p_value),
        "ci_left": float(ci_left),
        "ci_right": float(ci_right),
        "alpha": alpha,
        "n_control": n_control,
        "n_treatment": n_treatment,
        "std_control": float(std_control),
        "std_treatment": float(std_treatment),
        "verdict": verdict
    }
    
    return result


def print_analysis_report(result: dict):
    
    print(f"A/B Test Analysis Report: {result['verdict']}")
    
    print(f"Control mean:       {result['mean_control']:.4f}")
    print(f"\nTreatment mean:     {result['mean_treatment']:.4f}")
    print(f"Absolute uplift:    {result['abs_uplift']:.4f}")
    print(f"\nRelative uplift:    {result['rel_uplift']:.2%}")
    print(f"p-value:            {result['p_value']:.6f}")
    print(f"\n{(1-result['alpha'])*100:.0f}% CI:            [{result['ci_left']:.4f}, {result['ci_right']:.4f}]")
    print(f"n control:          {result['n_control']:,}")
    print(f"n treatment:        {result['n_treatment']:,}")
    
   