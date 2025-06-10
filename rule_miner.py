# Rule mining for economic risk scenarios.
from typing import List

import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text


def learn_scenarios(X: pd.DataFrame, y: List[int]) -> List[str]:
    """Learn decision rules that trigger risk."""
    if X.empty or not y:
        return []

    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X, y)
    rules = export_text(clf, feature_names=list(X.columns))
    return rules.splitlines()
