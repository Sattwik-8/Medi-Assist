import pandas as pd
import pickle
import os
from sklearn.svm import SVC

print("Loading training data...")
df = pd.read_csv('datasets/Training.csv')

X = df.drop('prognosis', axis=1)
y = df['prognosis']

print("Training model... (this takes 1-2 minutes)")
svc = SVC(kernel='linear', probability=True)
svc.fit(X, y)

os.makedirs('model', exist_ok=True)
pickle.dump(svc, open('model/svc.pkl', 'wb'))
print("Done! Model saved to model/svc.pkl")