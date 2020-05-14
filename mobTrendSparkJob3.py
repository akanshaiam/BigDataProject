from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession\
    .builder\
    .appName("myApp")\
    .config('spark.mongodb.input.uri', 'mongodb://127.0.0.1:27017/covid.mobility_trends.coll')\
    .config('spark.mongodb.output.uri', 'mongodb://127.0.0.1:27017/covid.job_collections.coll')\
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.2.0')\
    .getOrCreate()

df = spark.read\
    .format("com.mongodb.spark.sql.DefaultSource")\
    .option("database","covid")\
    .option("collection", "mobility_trends")\
    .load()

df.createOrReplaceTempView("mob")

stateOutputByDay = spark.sql("select sub_region_1, DAYOFWEEK(date) as day_of_week, avg(retail_and_recreation_percent_change_from_baseline) as avg_retail_and_recreation_percent_change,\
  avg(grocery_and_pharmacy_percent_change_from_baseline) as avg_grocery_and_pharmacy_percent_change, \
  avg(parks_percent_change_from_baseline) as avg_parks_percent_change,\
  avg(transit_stations_percent_change_from_baseline) as avg_transit_stations_percent_change,\
  avg(workplaces_percent_change_from_baseline) as avg_workplaces_percent_change, \
  avg(residential_percent_change_from_baseline) as avg_residential_percent_change\
       from mob where country_region_code = \"US\" group by sub_region_1,  DAYOFWEEK(date)")\
      .sort(col("day_of_week"))
#finalStateOutputByDay.show()
stateOutputByDay.createOrReplaceTempView("stateOutputByDay")
finalStateOutputByDay = spark.sql("select day_of_week, avg_retail_and_recreation_percent_change, avg_grocery_and_pharmacy_percent_change, avg_parks_percent_change, avg_transit_stations_percent_change, avg_workplaces_percent_change, avg_residential_percent_change from stateOutputByDay where sub_region_1 = \"New York\"")


cityOutputByDay = spark.sql("select sub_region_2, DAYOFWEEK(date) as day_of_week, retail_and_recreation_percent_change_from_baseline\
    grocery_and_pharmacy_percent_change_from_baseline,  parks_percent_change_from_baseline\
    transit_stations_percent_change_from_baseline,  workplaces_percent_change_from_baseline\
    residential_percent_change_from_baseline from mob where country_region_code = \"US\"").sort(col("day_of_week"))
#cityOutputByDay.createOrReplaceTempView("cityOutputByDay")
#finalCityOutputByDay.show()
finalCityOutputByDay = spark.sql("select DAYOFWEEK(date) as day_of_week, retail_and_recreation_percent_change_from_baseline, grocery_and_pharmacy_percent_change_from_baseline,  parks_percent_change_from_baseline, transit_stations_percent_change_from_baseline,  workplaces_percent_change_from_baseline, residential_percent_change_from_baseline from mob where country_region_code = \"US\" and sub_region_2 = \"Kings County\"")

stateOutputByDay.write\
    .format("com.mongodb.spark.sql.DefaultSource") \
    .mode("append") \
    .option("collection", "state_by_day") \
    .save()

cityOutputByDay.write\
    .format("com.mongodb.spark.sql.DefaultSource") \
    .mode("append") \
    .option("collection", "city_by_day") \
    .save()

finalStateOutputByDay.write.format('com.databricks.spark.csv').save('C:/Users/Akansha/BidDataRepo/BigDataProject/mycsv.csv', header='true')

finalCityOutputByDay.write.format('com.databricks.spark.csv').save('C:/Users/Akansha/BidDataRepo/BigDataProject/citydata', header='true')