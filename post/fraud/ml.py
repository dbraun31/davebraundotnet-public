from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
        classification_report, 
        confusion_matrix,
        roc_auc_score)
import numpy as np
import pandas as pd


# 0.1% frauds
d = pd.read_csv('creditcard.csv')

features = [x for x in d.columns if x not in ['Time', 'Class']]

X = d[features].to_numpy()
y = d['Class'].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, random_state=42
)

# Undersample majority class
idx_legit = np.where(y_train==0)[0]
idx_fraud = np.where(y_train==1)[0]

idx_legit_sampled = np.random.choice(idx_legit, size=len(idx_fraud),
                                     replace=False)


idx = np.concat([idx_legit_sampled, idx_fraud])
np.random.shuffle(idx)

X_train_down = X_train[idx]
y_train_down = y_train[idx]

# Fit model

rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42
)

rf.fit(X_train_down, y_train_down)

# Predict
pred = rf.predict(X_test)
prob = rf.predict_proba(X_test)[:,1]

# Evaluate
print(confusion_matrix(pred, y_test))
print(classification_report(pred, y_test))
print(roc_auc_score(y_test, prob))

d = pd.DataFrame(np.concat([y_test.reshape(-1, 1), prob.reshape(-1, 1)], axis=1),
                 columns = ['y_test', 'y_prob'])
d.to_csv('preds.csv', index=False)


# CV

param_grid = {
        'max_depth': [5, 10, 20, None],
        'min_samples_leaf': [1, 5, 10],
        'max_features': ['sqrt', 'log2'],
        'class_weight': [None, 'balanced']
}


grid = GridSearchCV(RandomForestClassifier(n_estimators=300),
                    param_grid,
                    scoring='roc_auc',
                    cv=5)

grid.fit(X_train_down, y_train_down)


y_proba = grid.predict_proba(X_test)[:, 1]

print(roc_auc_score(y_test, y_proba))

d = pd.DataFrame(np.concat([y_test.reshape(-1,1), y_proba.reshape(-1, 1)], axis=1),
                 columns = ['y_test', 'y_proba'])

d.to_csv('preds_cv.csv', index=False)

