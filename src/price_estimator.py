import os
import time as t
import logging as log
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import OneHotEncoder 
from pyspark.ml.feature import StringIndexer 
from pyspark.ml.feature import Normalizer
from pyspark.ml.regression import LinearRegression

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

log_directory = "logs-car"  # Sostituisci con il percorso della cartella desiderata
os.makedirs(log_directory, exist_ok=True)
log_filename = os.path.join(log_directory, f"car_prediction_LR_{timestamp}.log")

log.basicConfig(
    level=log.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=log_filename,
    filemode='w'
)

# Creazione della sessione Spark
spark = SparkSession.builder \
    .appName("Car Prediction Linear Regression") \
    .config("spark.locality.wait.node", "0").getOrCreate()

# Caricamento del dataset
file_path = "hdfs:/input/true_car_listings.csv" 
df = spark.read.csv(file_path, header=True, inferSchema=True)

# Campionamento del dataset
#df = df.sample(withReplacement=False, fraction=0.33, seed=t.time())
#df = df.sample(withReplacement=False, fraction=0.66, seed=t.time())

df = df.drop('Vin')

# Dummizzazione delle variabili categoriche
indexer = StringIndexer(inputCols=['City','State','Make','Model'], outputCols=['City_id','State_id','Make_id','Model_id'])
df_indexed = indexer.fit(df).transform(df)

df_indexed = df_indexed.drop(*['City','State','Make','Model'])

encoder = OneHotEncoder(inputCols=['City_id','State_id','Make_id','Model_id'], outputCols=['City_vec','State_vec','Make_vec','Model_vec'])
df_dummies = encoder.fit(df_indexed).transform(df_indexed)

df_dummies = df_dummies.drop(*['City_id','State_id','Make_id','Model_id'])

# Preparazione dei dati per la regressione lineare
feature_columns = df_dummies.columns
feature_columns.remove("Price")

assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
df_features = assembler.transform(df_dummies).select("features", "Price")

normalizer = Normalizer(inputCol='features', outputCol='normFeatures', p=2.0)
df_features = normalizer.transform(df_features)

df_features.show(10)

# Suddivisione del dataset in training e test set
train_data, test_data = df_features.randomSplit([0.8, 0.2], seed=42)

# Addestramento del modello di regressione lineare
lr = LinearRegression(featuresCol="features", labelCol="Price")

start_time = t.time()
log.info(f'Training started')
print(f"Training started")

lr_model = lr.fit(train_data)

end_time = t.time()
log.info(f"Training completed")
print(f"Training completed")

training_time = end_time - start_time
log.info(f"Training Time: {training_time} seconds")
print(f"Training Time: {training_time} seconds")

# Valutazione del modello
test_results = lr_model.evaluate(test_data)

print(f"RMSE: {test_results.rootMeanSquaredError}")
print(f"R2: {test_results.r2}")
print(f"Coefficients: {lr_model.coefficients}")
print(f"Intercept: {lr_model.intercept}")

model_path = "hdfs:/output/car_prediction_model"
lr_model.save(model_path)

# Chiusura della sessione Spark
spark.stop()
