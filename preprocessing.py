import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class CustomBinner(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.bins = {}

    def fit(self, X, y=None):
        X = X.copy()
        self.bins = {
            'annual_inc': [-np.inf, 30000, 60000, 90000, 120000, np.inf],
            'int_rate': [-np.inf, 10, 13, 16, 20, np.inf],
            'total_rev_hi_lim': [-np.inf, 10000, 25000, 50000, 100000, np.inf],
            'months_since_credit_line': [-np.inf, 36, 60, 84, 120, np.inf],
            'total_acc': [-np.inf, 10, 20, 30, 50, np.inf],
            'inq_last_6mths': [-1, 0, 2, 4, 6, np.inf],
            'emp_length': [-1, 0, 2, 5, 10, np.inf],
            'open_acc': [-np.inf, 5, 10, 15, 20, np.inf],
            'delinq_2yrs': [-1, 0, 1, 3, 5, np.inf],
            'pub_rec': [-1, 0, 1, 2, 3, np.inf],
            'acc_now_delinq': [-1, 0, 1, 2, np.inf],
            'dti': [-np.inf, 10, 20, 30, 40, np.inf],
            'term': ['36 months', '60 months'],  # already categorical
        }
        return self

    def transform(self, X):
        X = X.copy()
        for col, bin_edges in self.bins.items():
            if col not in X.columns:
                continue
            if isinstance(bin_edges[0], (int, float)):
                X[col] = pd.cut(X[col], bins=bin_edges, labels=False, include_lowest=True)
            else:
                X[col] = X[col].astype(str)
        return X


class WOETransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.woe_dict = {}

    def fit(self, X, y):
        X = X.copy()
        y = y.copy()
        total_good = (y == 0).sum()
        total_bad = (y == 1).sum()

        for col in X.columns:
            self.woe_dict[col] = {}
            values = X[col].unique()
            for val in values:
                mask = X[col] == val
                good = ((y == 0) & mask).sum()
                bad = ((y == 1) & mask).sum()

                # Add Laplace correction to avoid divide by zero
                good = good if good != 0 else 0.5
                bad = bad if bad != 0 else 0.5

                dist_good = good / total_good
                dist_bad = bad / total_bad
                self.woe_dict[col][val] = np.log(dist_good / dist_bad)
        return self

    def transform(self, X):
        X_copy = X.copy()
        woe_transformed_data = {}

        for col, mapping in self.woe_dict.items():
            # Apply the mapping to create the WoE column data
            # Ensure 'mapping' correctly handles categories not seen during fit (e.g., fillna with a default WoE or 0)
            woe_transformed_data[col + "_woe"] = X_copy[col].map(mapping).fillna(0) # or a specific default WoE

        # Create a DataFrame from the collected WoE columns
        woe_df_to_add = pd.DataFrame(woe_transformed_data, index=X_copy.index)

        # Concatenate all new WoE columns to the original DataFrame in one go
        # This is much more efficient than adding columns one by one
        X_result = pd.concat([X_copy, woe_df_to_add], axis=1)

        return X_result

