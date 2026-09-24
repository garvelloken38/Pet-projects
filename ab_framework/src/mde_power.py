import numpy as np
from scipy import stats
from typing import Optional


def calculate_mde(n_control: int, n_treatment: int, std_control: float, std_treatment: Optional[float] = None, alpha: float = 0.05, power: float = 0.8) -> dict:
    
    if std_treatment is None:
        std_treatment = std_control
    
    # Критические значения
    z_alpha = stats.norm.ppf(1 - alpha / 2)      # двусторонний тест
    z_beta = stats.norm.ppf(power)
    
    # Стандартная ошибка разницы
    se = np.sqrt(std_control**2 / n_control + std_treatment**2 / n_treatment)
    
    # MDE
    mde = (z_alpha + z_beta) * se
    
    return {
        "mde_abs": float(mde),
        "alpha": alpha,
        "power": power,
        "n_control": n_control,
        "n_treatment": n_treatment,
        "se": float(se)
    }


def calculate_power(effect_size: float, n_control: int, n_treatment: int, std_control: float, std_treatment: Optional[float] = None, alpha: float = 0.05) -> dict:
    
    if std_treatment is None:
        std_treatment = std_control
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    se = np.sqrt(std_control**2 / n_control + std_treatment**2 / n_treatment)
    
    # Non-centrality parameter
    z = effect_size / se
    
    # Мощность
    power = 1 - stats.norm.cdf(z_alpha - z) + stats.norm.cdf(-z_alpha - z)
    
    return {
        "power": float(power),
        "effect_size": effect_size,
        "alpha": alpha,
        "n_control": n_control,
        "n_treatment": n_treatment,
        "se": float(se)
    }


def calculate_sample_size(
    mde: float,
    std_control: float,
    std_treatment: Optional[float] = None,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0
) -> dict:
    """
    Считает необходимый размер выборки для детектирования заданного MDE.
    
    ratio = n_treatment / n_control (по умолчанию 1.0 = 50/50)
    """
    if std_treatment is None:
        std_treatment = std_control
    
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    # Формула для n_control
    n_control = ((z_alpha + z_beta) ** 2 * (std_control**2 + std_treatment**2 / ratio)) / (mde ** 2)
    n_treatment = n_control * ratio
    
    return {
        "n_control": int(np.ceil(n_control)),
        "n_treatment": int(np.ceil(n_treatment)),
        "n_total": int(np.ceil(n_control + n_treatment)),
        "mde": mde,
        "alpha": alpha,
        "power": power,
        "ratio": ratio
    }


def print_mde_report(result: dict, mean_control: Optional[float] = None) -> None:
    """Красивый отчёт по MDE"""
    
    print("=" * 50)
    print("MDE Report")
    print("=" * 50)
    print(f"MDE (абсолютный):     {result['mde_abs']:.4f}")
    
    if mean_control is not None and mean_control != 0:
        mde_rel = result['mde_abs'] / mean_control
        print(f"MDE (относительный):  {mde_rel:.2%}")
    
    print(f"alpha:                {result['alpha']}")
    print(f"power:                {result['power']}")
    print(f"n control:            {result['n_control']:,}")
    print(f"n treatment:          {result['n_treatment']:,}")
    print("=" * 50)


def print_power_report(result: dict) -> None:
    print("=" * 50)
    print("Power Report")
    print("=" * 50)
    print(f"Заданный эффект:      {result['effect_size']:.4f}")
    print(f"Мощность (power):     {result['power']:.2%}")
    print(f"alpha:                {result['alpha']}")
    print(f"n control:            {result['n_control']:,}")
    print(f"n treatment:          {result['n_treatment']:,}")
    print("=" * 50)


def print_sample_size_report(result: dict) -> None:
    print("=" * 50)
    print("Sample Size Report")
    print("=" * 50)
    print(f"Целевой MDE:          {result['mde']:.4f}")
    print(f"Нужно control:        {result['n_control']:,}")
    print(f"Нужно treatment:      {result['n_treatment']:,}")
    print(f"Всего:                {result['n_total']:,}")
    print(f"alpha:                {result['alpha']}")
    print(f"power:                {result['power']}")
    print("=" * 50)