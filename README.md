# Analisi delle performance di un cluster Hadoop per l’addestramento di un algoritmo di regressione lineare tramite Apache Spark
Progetto di Data Intensive Application and Big Data

## Requisiti
- Java 8 
- Python 3
- [Apache Hadoop 3.3.4](https://hadoop.apache.org/docs/r3.3.4/)
- [Apache Spark 3.5.1](https://spark.apache.org/releases/spark-release-3-5-1.html)

## Setup Hadoop cluster
Per creare questo cluster sono state utilizzare tre macchine Ubuntu Server 2024 con 8 GB di RAM e 4 vCores ciascuna, collegate tra loro da uno switch.

E' consigliabile creare un nuovo utente all'interno del sistema operativo dedicato al cluster (es. hadoop).

### Setup della rete
Modificare il file  ```/etc/hosts``` ed inserire una riga per ogni node del cluster.
```bash
sudo nano /etc/hosts
```
```bash
xxx.xxx.xxx.xxx Master
xxx.xxx.xxx.xxx Node1
xxx.xxx.xxx.xxx Node2
```
Si procede ora a configurare un accesso remoto tramite SSH per far comunicare le macchine, va quindi creata una coppia di chiavi con i seguenti comandi
```bash
ssh-keygen -t rsa -P ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```
Si procede ora a copiare le chiavi
```bash
ssh-copy-id hadoopuser@Master
ssh-copy-id hadoopuser@Node1
ssh-copy-id hadoopuser@Node2
```

### Configurazioni variabili di Ambiente
Successivamente è necessario scaricare Java, Hadoop e Spark, ed aggiungere delle righe al file ```.bashrc``` tramite il comando:
```bash
nano .bashrc
```
Bisogna quindi aggiungere le seguenti variabili di ambiente
```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
export HADOOP_HOME=$HOME/hadoop-3.3.4
export SPARK_HOME=$HOME/spark-3.5.1
export PATH=$HADOOP_HOME/sbin:$HADOOP_HOME/bin:$PATH
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export LD_LIBRARY_PATH=$HADOOP_HOME/lib/native:$LD_LIBRARY_PATH
export PYSPARK_PYTHON=$HOME/pyspark_venv/bin/python3
```
Successivamente è necessario eseguire il seguente comando per far si che le modifiche siano applicate
```bash
source .bashrc
```

---
### Setup YARN e HDFS
Sul nodo *master* è necessario andare a modificare il seguenti file:

```hadoop-3.3.4/etc/hadoop/yarn_site.xml``` 
```xml
<?xml version="1.0"?>
<configuration>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>master</value>
    </property>
</configuration>
```
---
```hadoop-3.3.4/etc/hadoop/mapred-site.xml``` 

```xml
<?xml version="1.0"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
```
---
```hadoop-3.3.4/etc/hadoop/core-site.xml``` 

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://master:9000</value>
    </property>
</configuration>
```
---
```hadoop-3.3.4/etc/hadoop/core-site.xml``` 

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property>
        <name>dfs.name.dir</name>
        <value>${user.home}/bigdata/hd-data/nn</value>
    </property>
    <property>
        <name>dfs.replication</name>
        <value>2</value>
    </property>
</configuration>
```
---
Infine è necessario modificare  ```hadoop-3.3.4/etc/hadoop/workers``` e aggiungere i nodi worker:

```text
master
node1
node2
```
In questo caso il master svolgerà anche le funzioni da nodo worker.
Per concludere è necessario eseguire questo comando:
```bash
hdfs namenode -format
```
A questo punto, nella cartella ```hadoop-3.3.4/sbin``` è possibile eseguire i seguenti script
```bash
sh start-yarn.sh
sh start-dfs.sh
```
Per controllare il corretto avvio del cluster basta digitare il  comando ``` jps ```.

Tramite i seguenti indirizzi sarà possibile accedere alle interfacce web di YARN e HDFS

 -  YARN ```https://master:8088```
 - HDFS  ```https://master:9870``` 


## Esecuzione dello script
All'interno della cartella ```spark-3.5.1``` devono essere presenti ulteriori tre cartelle, chiamate `input-car` ,`logs-car` e `output-car`. Mentre nella prima andrà salvato il dataset, nella altre saranno salvati i log dell'applicazione e il modello addestrato.

A questo punto per lanciare l'esecuzione dell'applicazione basta avviare lo script  ```run-car-price-estimator.sh``` .

Inoltre, è presente un ulteriore script: `get-app-data.sh` che richiama le API di YARN e scarica i metadati dell'applicazione salvandoli nella cartella dei logs.
Per lanciare questo script è necessario passare come argomento il nome dell'applicazione (es. `sh get-app-data.sh application_XXXXXXX_XXXXXX`)
