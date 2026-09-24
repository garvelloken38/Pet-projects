import hashlib
from typing import Union, Optional, List, Dict
import pandas as pd


class BucketSplitter:

    def __init__(self, salt: str = "default_experiment", n_buckets: int = 1000, hash_func: str = "md5"):
        self.salt = salt
        self.n_buckets = n_buckets
        self.hash_func = hash_func

        if hash_func not in ("md5", "sha256"):
            raise ValueError("hash_func must be 'md5' or 'sha256'")



    def get_bucket(self, user_id: Union[str, int]) -> int:

        # Склеиваю id и соль
        key = f"{user_id}_{self.salt}".encode("utf-8")

        if self.hash_func == "md5":
            hash_hex = hashlib.md5(key).hexdigest()
        else:
            hash_hex = hashlib.sha256(key).hexdigest()

        # Получаю номер бакета от 0 до n-1
        return int(hash_hex, 16) % self.n_buckets



    def assign_group(self, user_id: Union[str, int], groups: Optional[Dict[str, float]] = None) -> str:

        if groups is None:
            groups = {"control": 0.5, "treatment": 0.5}

        total = sum(groups.values())
        groups = {k: v / total for k, v in groups.items()}

        bucket = self.get_bucket(user_id)
        cumulative = 0.0
        # Делю бакеты на отрезки пропорционально долям групп

        for group_name, share in groups.items():
            cumulative += share
            if bucket < cumulative * self.n_buckets:
                return group_name

        return list(groups.keys())[-1]



    def split(self, df: pd.DataFrame, user_id_col: str = "user_id", groups: Optional[Dict[str, float]] = None, 
              stratify_by: Optional[Union[str, List[str]]] = None, add_bucket_col: bool = True) -> pd.DataFrame:

        df_split = df.copy()

        if stratify_by is None:

            df_split["group"] = df_split[user_id_col].apply(lambda x: self.assign_group(x, groups=groups))

            if add_bucket_col:
                df_split["bucket"] = df_split[user_id_col].apply(self.get_bucket)
                
        else:

            if isinstance(stratify_by, str):
                stratify_by = [stratify_by]


            def stratified_assign(group_df):

                # Своя соль для каждой страты
                strata_key = "_".join(str(v) for v in group_df.name)
                local_splitter = BucketSplitter(salt=f"{self.salt}_{strata_key}", n_buckets=self.n_buckets, hash_func=self.hash_func)

                group_df = group_df.copy()

                group_df["group"] = group_df[user_id_col].apply(lambda x: local_splitter.assign_group(x, groups=groups))
                
                if add_bucket_col:
                    group_df["bucket"] = group_df[user_id_col].apply(local_splitter.get_bucket)
                return group_df

            # Независимый сплит внутри каждой страты
            df_split = df.groupby(stratify_by, group_keys=False).apply(stratified_assign)
            df_split = pd.merge(df[ ["user_id",] + stratify_by], df_split, on='user_id', how='inner')
            
        return df_split

