#!/bin/bash 

rm -r $SPARK_HOME/output-car
$HADOOP_HOME/bin/hdfs dfsadmin -safemode leave
$HADOOP_HOME/bin/hdfs dfs -rm -r /output
$HADOOP_HOME/bin/hdfs dfs -rm -r /input
$HADOOP_HOME/bin/hdfs dfs -put $SPARK_HOME/input-car /input
$SPARK_HOME/bin/spark-submit --master yarn --archives $HOME/pyspark_venv.tar.gz  --deploy-mode client  --driver-memory 2g  --executor-memory 4g  --executor-cores 4 --num-executors 3 --queue default $SPARK_HOME/price_estimator.py /input /output
$HADOOP_HOME/bin/hdfs dfs -get /output $SPARK_HOME/output-car