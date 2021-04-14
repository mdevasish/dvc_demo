# load train and test
# train algo
# save the metrics and parameters

import os
import warnings
import sys
import pandas as pd
import numpy as np 
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from urllib.parse import urlparse
from get_data import read_params
import argparse
import joblib
import json
import logging
from datetime import datetime

'''
DEBUG

Detailed information, typically of interest only when diagnosing problems.

INFO

Confirmation that things are working as expected.

WARNING

An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.

ERROR

Due to a more serious problem, the software has not been able to perform some function.

CRITICAL

A serious error, indicating that the program itself may be unable to continue running.
'''

def eval_metrics(actual,pred):
    rmse = np.sqrt(mean_squared_error(actual,pred))
    mae = mean_absolute_error(actual,pred)
    r2 = r2_score(actual,pred)
    return rmse,mae,r2

def train_and_evaluate(config_path):
    config = read_params(config_path)
    train_data_path = config["split_data"]["train_path"]
    test_data_path = config["split_data"]["test_path"]
    random_state = config["base"]["random_state"]
    model_dir = config["model_dir"]
    

    alpha = config["estimators"]["ElasticNet"]["params"]["alpha"]
    l1_ratio = config["estimators"]["ElasticNet"]["params"]["l1_ratio"]

    target = [config["base"]["target_col"]]

    train = pd.read_csv(train_data_path,sep = ",")
    test = pd.read_csv(test_data_path,sep = ",")

    train_y = train[target] 
    test_y = test[target]

    train_X = train.drop(target,axis = 1)
    test_X = test.drop(target,axis = 1)

    lr = ElasticNet(
                    alpha = alpha,
                     l1_ratio = l1_ratio,
                     random_state = random_state)
    lr.fit(train_X,train_y)
    
    pred = lr.predict(test_X)
    rmse,mae,r2 = eval_metrics(test_y,pred)

    logging.info("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
    logging.info("  RMSE: %s" % rmse)
    logging.info("  MAE: %s" % mae)
    logging.info("  R2: %s" % r2)

#####################################################
    scores_file = config["reports"]["scores"]
    params_file = config["reports"]["params"]

    with open(scores_file, "w") as f:
        scores = {
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }
        json.dump(scores, f, indent=4)

    with open(params_file, "w") as f:
        params = {
            "alpha": alpha,
            "l1_ratio": l1_ratio,
        }
        json.dump(params, f, indent=4)

#####################################################
    model_path = os.path.join(model_dir, "elasticnet.joblib")
    joblib.dump(lr, model_path)





if __name__ == "__main__":
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    fmt = 'run_'+ dt_string + '.log'
    log_path = os.path.join("logs",fmt)
    #print("./logs/"+fmt)
    logging.basicConfig(filename = log_path,level = logging.DEBUG,format='%(levelname)s:%(message)s')

    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    train_and_evaluate(config_path=parsed_args.config)
