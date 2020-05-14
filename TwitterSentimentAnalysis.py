import re

import sparknlp
from pyspark.sql import SparkSession
import pandas as pd
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from sparknlp.pretrained import PretrainedPipeline
from pymongo import MongoClient
from datetime import datetime
import pytz
from pyspark.sql.functions import udf, to_date, to_utc_timestamp


spark = SparkSession.builder \
    .appName("Spark NLP")\
    .master("local[4]")\
    .config("spark.driver.memory","16G")\
    .config("spark.driver.maxResultSize", "2G") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.11:2.2.0")\
    .config("spark.kryoserializer.buffer.max", "1000M")\
    .config('spark.mongodb.input.uri', 'mongodb://127.0.0.1:27017/covid.covid.coll')\
    .config('spark.mongodb.output.uri', 'mongodb://127.0.0.1:27017/covid.coivid.coll')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.2.0')\
    .config('spark.jars.packages','com.johnsnowlabs.nlp:spark-nlp_2.11:2.4.5')\
    .getOrCreate()

##read from mongodb into pyspark dataframe
twitter_df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("database","covid").option("collection", "covid").load()
print(twitter_df.show(n=2))


#input=twitter_df.select('id','text').toDF("id","tweet_text")
#print("imput")
#input.show()

##preprocess data - remove hashtags, punctutations , hyperlinks, @symbols,

def cleantext(text):
    text = re.sub('@[A-Za-z0–9]+', '', text)  # Removing @mentions
    text = re.sub('#', '', text)  # Removing '#' hash tag
    text = re.sub('RT[\s]+', '', text)  # Removing RT
    text = re.sub('https?:\/\/\S+', '', text)  # Removing hyperlink
    text = re.sub(':', '', text) #remove colon
    text=re.sub('(\.|\!|\?|\,)', '', text) #remove punctutations
    return text

udf_fun = udf(lambda text:cleantext(text),StringType())
preprocessed_text = twitter_df.select('id',udf_fun('text').alias('text'), 'user', 'created_at')

preprocessed_text.show()

#use pipeline
pipeline = PretrainedPipeline("analyze_sentiment")
result = pipeline.annotate(preprocessed_text,column='text')
#result.select("sentiment.result").show()

#write result to mongodb

cols = ['id','text','sentiment.result', 'user', 'created_at']
output = result.select(cols)
#output.show()

## Converting date string format
def getDate(x):
    if x is not None:
        return str(datetime.strptime(x,'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC).strftime("%Y-%m-%d"))
    else:
        return None

## UDF declaration
date_fn = udf(getDate, StringType())

## Converting datatype in spark dataframe
output = output.withColumn("created_at", to_utc_timestamp(date_fn("created_at"),"UTC"))

#output = output.withColumn("date_only", func.to_date(func.col("created_at")))

# dfNew.write\
#     .format("com.mongodb.spark.sql.DefaultSource") \
#     .mode("append") \
#     .option("collection", "sentiment_predicted") \
#     .save()

output.show()