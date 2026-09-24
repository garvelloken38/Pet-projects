import pandas as pd
import numpy as np
from scipy.stats import chisquare
from typing import Dict, Optional


def check_srm(df: pd.DataFrame, group_col: str = "group", expected_ratios: Optional[Dict[str, float]] = None, alpha: float = 0.001) -> dict:
   
    # Фактические количества
    observed_counts = df[group_col].value_counts().sort_index()
    total = observed_counts.sum()
    
    groups = observed_counts.index.tolist()
    observed = observed_counts.values.astype(float)
    
    # Ожидаемые доли
    if expected_ratios is None:
        # По умолчанию — равные доли
        n_groups = len(groups)
        expected_ratios = {g: 1.0 / n_groups for g in groups}
    else:
        # Нормализуем на всякий случай
        total_ratio = sum(expected_ratios.values())
        expected_ratios = {k: v / total_ratio for k, v in expected_ratios.items()}
    
    # Проверяем, что все группы из данных есть в expected_ratios
    missing = set(groups) - set(expected_ratios.keys())
    if missing:
        raise ValueError(f"Для групп {missing} не заданы ожидаемые доли")
    
    # Ожидаемые количества
    expected = np.array([expected_ratios[g] * total for g in groups])
    
    # Хи - квадрат
    chi2_stat, p_value = chisquare(f_obs=observed, f_exp=expected)
    
    # Фактические доли
    observed_ratios = {g: count / total for g, count in zip(groups, observed)}
    
    # Вывод
    is_srm = int(p_value < alpha)
    
    result = {
        "is_srm": is_srm,
        "p_value": float(p_value),
        "alpha": alpha,
        "observed_counts": dict(zip(groups, observed.astype(int))),
        "expected_counts": dict(zip(groups, expected.round(1))),
        "observed_ratios": {g: round(r, 4) for g, r in observed_ratios.items()},
        "expected_ratios": {g: round(expected_ratios[g], 4) for g in groups},
        "total_users": int(total),
        "verdict": "SRM detected" if is_srm else "OK — no SRM"
    }
    
    return result


def print_srm_report(result: dict):
    
    print(f"SRM Check Report: {result['verdict']}")
    print(f"p-value:          {result['p_value']:.6f}")
    print(f"alpha:            {result['alpha']}")
    print(f"Всего пользователей: {result['total_users']:,}")
    print("\n\nДоли групп:")
    
    for group in result["observed_ratios"]:
        obs = result["observed_ratios"][group]
        exp = result["expected_ratios"][group]
        obs_count = result["observed_counts"][group]
        exp_count = result["expected_counts"][group]
        
        print(f"{group:12} | факт: {obs:.2%} ({obs_count:,})  |  ожидалось: {exp:.2%} ({exp_count:,.0f})")
    
