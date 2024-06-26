import os
import sys
from dataclasses import dataclass
from matplotlib.pyplot import step
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.exception import CustomException
from src.logger import logging

from src.utils import save_obj

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts',"preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()
    
    def get_data_transformer_obj(self):                                          # This is the data transformation function
        try:
            numerical_columns = ["writing_score", "reading_score"]
            categorical_columns = ["gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course"]
            
            num_pipeline = Pipeline(
               steps= [("imputer",SimpleImputer(strategy = 'median')),
                       ("scaler", StandardScaler())
                       ]
           )
            
            categorical_pipeline = Pipeline(
                steps = [("imputer", SimpleImputer(strategy = 'most_frequent')),  # for treating missing values
                         ("one_hot_encoder", OneHotEncoder()),                    # encoding the categorical values into numerical values
                         ("scaler",StandardScaler(with_mean=False))                              # StandardScaler is used to standardize the input data in a way that ensures that the data points have a balanced scale

                ]
            )

            logging.info(f"Numerical columns: {numerical_columns}")
            logging.info(f"Categorical columns: {categorical_columns}")

            preprocessor = ColumnTransformer([
                ('num_pipeline',num_pipeline,numerical_columns),
                ('categorical_pipeline',categorical_pipeline,categorical_columns)
            ])
            return preprocessor
        
        except Exception as e:
            raise CustomException(e,sys)
    
    def initiate_data_transformation(self,train_path,test_path):
        try:
            train_df = pd.read_csv(train_path)
            # logging.info(f" train data {train_df}")
            test_df = pd.read_csv(test_path)

            logging.info("Read train and test data completed")
            logging.info("Obtaining preprocessing object")

            preprocessing_obj = self.get_data_transformer_obj()

            target_column = "math_score"
            numerical_columns = ["writing_score", "reading_score"]

            input_feature_train_df = train_df.drop(columns=[target_column],axis=1)
            target_feature_train_df = train_df[target_column]
            logging.info(f"{input_feature_train_df}")

            input_feature_test_df = test_df.drop(columns=[target_column],axis=1)
            target_feature_test_df = test_df[target_column]

            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe."
            )

            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            logging.info(f"{input_feature_train_arr}")
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[input_feature_train_arr,np.array(target_feature_train_df)]  # np.c_[] concatenates arrays along second axis.
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info(f"Saved preprocessing object.")

            save_obj(

            file_path=self.data_transformation_config.preprocessor_obj_file_path,
            obj=preprocessing_obj

        )

            return (
            train_arr,
            test_arr,
            self.data_transformation_config.preprocessor_obj_file_path,
        )


        except Exception as e:
            raise CustomException(e,sys)
    

