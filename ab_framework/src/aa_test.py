import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Dict

from .analysis import analyze_experiment
from .srm import check_srm
from .split import BucketSplitter


def run_aa_tests(df: pd.DataFrame, n_iterations: int = 500, metric_col: str = "post_metric", user_id_col: str = "user_id",
    groups: Optional[Dict[str, float]] = None, alpha: float = 0.05, srm_alpha: float = 0.001, salt_prefix: str = "aa_test") -> dict:
  
    
    if groups is None:
        groups = {"control": 0.5, "treatment": 0.5}
    
    p_values = []
    srm_flags = []
    abs_uplifts = []
    
    iterator = range(n_iterations)
    
    for i in iterator:
        # Каждый раз новый сплит
        splitter = BucketSplitter(salt=f"{salt_prefix}_{i}", n_buckets=1000)
        
        df_split = splitter.split(df, user_id_col=user_id_col, groups=groups)
        
        # SRM
        srm_result = check_srm(df_split, group_col="group", expected_ratios=groups, alpha=srm_alpha)
        srm_flags.append(srm_result["is_srm"])
        
        # Анализ
        analysis = analyze_experiment(df_split, metric_col=metric_col, group_col="group", control_name="control", 
                                      treatment_name="treatment", alpha=alpha)
        
        p_values.append(analysis["p_value"])
        abs_uplifts.append(analysis["abs_uplift"])
    
  
    result = {
        "n_iterations": n_iterations,
        "p_values": p_values,
        "abs_uplifts": abs_uplifts,
        "srm_flags": srm_flags,
        "alpha": alpha
    }
    
    return result


def plot_aa_pvalues(result: dict, bins: int = 20, figsize: tuple = (12, 5)):
   
    p_values = np.asarray(result["p_values"])
    alpha = result.get("alpha", 0.05)
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    plt.suptitle("Распределение p-value")
    
    ax1 = axes[0]

    ax1.hist(p_values, bins=bins, density=True, alpha=0.7, edgecolor="black", label="Фактическое")
    ax1.axhline(1.0, color="red", linestyle="--", linewidth=2, label="Ожидаемое")
    
    ax1.set_xlabel("p-value")
    ax1.set_ylabel("Плотность")
    ax1.legend()
    ax1.set_xlim(0, 1)
    
    ax2 = axes[1]
    
    sorted_p = np.sort(p_values)
    l = np.arange(1, len(sorted_p) + 1) / len(sorted_p)
    
    ax2.plot(sorted_p, l, label="Фактическое", linewidth=2)
    ax2.plot([0, 1], [0, 1], color="red", linestyle="--", linewidth=1, alpha = 0.7, label="Ожидаемое")
        
    ax2.set_xlabel("p-value")
    ax2.set_ylabel("Доля наблюдений <= p")
    ax2.legend()
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_aspect("equal")
    
    plt.tight_layout()
    plt.show()
    
    
    

    
