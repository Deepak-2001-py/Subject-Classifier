from pathlib import Path
# import mlflow
# import mlflow.keras
from src.SubjectClassifier import logger
import numpy as np
import joblib
# from urllib.parse import urlparse
from src.SubjectClassifier.entity.config_entity  import (EvaluationConfig)
from src.SubjectClassifier.utils.common import save_json
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, f1_score, recall_score
from sklearn.model_selection import cross_val_score, cross_val_predict
import os
import pandas as pd
import time
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
class Evaluation:
    def __init__(self,config:EvaluationConfig):
        self.config=config
        self.best_model = None
        self.grid_search = None




    def evaluation(self):
        # Load the trained model
        ec = joblib.load(self.config.trained_model_path)
        logger.info("Loaded the trained model successfully")
        
        # Load the data
        x_train_tfidf = pd.read_csv(os.path.join(self.config.train_data, "X_traintfidf_data.csv"), index_col=0, header=0)
        x_test_tfidf = pd.read_csv(os.path.join(self.config.eval_data, "X_testtfidf_data.csv"), index_col=0, header=0)
        y_train = pd.read_csv(os.path.join(self.config.train_data, "y_train_data.csv"), index_col=0, header=0)
        y_test = pd.read_csv(os.path.join(self.config.eval_data, "y_test_data.csv"), index_col=0, header=0)

        # Reset the index of data frames
        x_train_tfidf = x_train_tfidf.reset_index(drop=True)
        x_test_tfidf = x_test_tfidf.reset_index(drop=True)
        y_train = y_train.reset_index(drop=True)
        y_test = y_test.reset_index(drop=True)

        # Convert y_train and y_test to 1D arrays
        y_train = y_train.values.ravel()  # or np.squeeze(y_train.values)
        y_test = y_test.values.ravel()  # or np.squeeze(y_test.values)
        

        
        logger.info("Loaded all the train and test files successfully")
        x=time.time()
        # Make predictions
        
        y_pred = ec.predict(x_test_tfidf)
        # print(y_pred)
        # print(y_test)
        # print(type(y_pred),type(y_test))
        y=time.time()
        logger.info(f"time taken for predection:{y-x}")
        
        # Calculate scores
        logger.info(f"calculating matrics ")
        self.accuracy = accuracy_score(y_test, y_pred)
        # self.classification_report = classification_report(y_test, y_pred)
        # self.confusion_matrix = confusion_matrix(y_test, y_pred)
        self.precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        self.f1_score = f1_score(y_test, y_pred, average='weighted')
        self.recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Cross-validation
        self.scores = cross_val_score(ec, x_train_tfidf, y_train, cv=5)
        z=time.time()
        logger.info(f"time taken for cross evalutaion:{z-y}")
        
        # Print results
        logger.info(f"Accuracy: {self.accuracy}\n")
        # logger.info("Classification Report:\n", self.classification_report)
        # logger.info(f"Confusion Matrix:\n{self.confusion_matrix}\n")
        logger.info(f"Precision: {self.precision}\n")
        logger.info(f"F1 Score: {self.f1_score}\n")
        logger.info(f"Recall: {self.recall}\n")
        logger.info(f"Cross-validated scores: {self.scores}")

    def save_score(self):
        scores = {
            "accuracy": self.accuracy,
            # "classification_report": self.classification_report,
            # "confusion_matrix": self.confusion_matrix.tolist(),
            "precision": self.precision,
            "f1_score": self.f1_score,
            "recall": self.recall,
            "cross_val_score_mean": self.scores.mean(),
            "cross_val_score_std": self.scores.std()
        }
        if self.grid_search:
            scores["best_params"] = self.grid_search.best_params_
            scores["best_score"] = self.grid_search.best_score_
        
        path = Path("scores.json")
        save_json(path, data=scores)
        logger.info(f"Saved scores at {path}")
        return scores


            
