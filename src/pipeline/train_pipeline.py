import sys
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.exception import CustomException
from src.logger import logger

class TrainPipeline:
    def __init__(self):
        pass

    def run_pipeline(self):
        try:
            logger.info("Starting training pipeline execution...")
            data_ingestion = DataIngestion()
            train_data_path, test_data_path = data_ingestion.initiate_data_ingestion()

            data_transformation = DataTransformation()
            train_arr, test_arr, _ = data_transformation.initiate_data_transformation(
                train_data_path, test_data_path
            )

            model_trainer = ModelTrainer()
            r2_square = model_trainer.initiate_model_trainer(train_arr, test_arr)

            logger.info(f"Training pipeline completed successfully with R2 score: {r2_square}")
            return r2_square

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    pipeline = TrainPipeline()
    r2_score = pipeline.run_pipeline()
    print(f"Model Training completed. Final R2 Score: {r2_score}")
