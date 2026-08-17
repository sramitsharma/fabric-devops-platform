"""Event Hubs (Kafka endpoint) -> S3 replicator. Effectively-once:
checkpointed offsets + deterministic file commits. Config comes from env
vars injected by the SparkApplication (which ArgoCD renders per tenant
from tenants.yaml). Auth: Entra Workload Identity, no connection strings."""
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, to_date

TENANT = os.environ["TENANT_ID"]
EH_NS = os.environ["EH_NAMESPACE"]
EH_NAME = os.environ["EH_NAME"]
S3_PATH = f"s3a://{os.environ['S3_BUCKET']}/{TENANT}/bronze/{EH_NAME}"
CKPT = os.environ["CHECKPOINT_PATH"]

spark = (SparkSession.builder.appName(f"eh2s3-{TENANT}-{EH_NAME}")
    .config("spark.hadoop.fs.s3a.endpoint", os.environ["S3_ENDPOINT"])
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.EnvironmentVariableCredentialsProvider")
    .getOrCreate())

raw = (spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", f"{EH_NS}:9093")
    .option("subscribe", EH_NAME)
    .option("kafka.security.protocol", "SASL_SSL")
    .option("kafka.sasl.mechanism", "OAUTHBEARER")
    .option("kafka.sasl.login.callback.handler.class",
            "com.microsoft.azure.eventhubs.kafka.OAuthBearerTokenCallbackHandler")
    .option("startingOffsets", "earliest")
    .option("maxOffsetsPerTrigger", int(os.environ.get("MAX_OFFSETS", 50000)))
    .option("failOnDataLoss", "true")
    .load())

bronze = raw.select(
    col("key").cast("string"),
    col("value").cast("string").alias("payload"),
    col("partition"), col("offset"),
    col("timestamp").alias("event_ts"),
    current_timestamp().alias("ingest_ts"),
).withColumn("dt", to_date(col("event_ts")))

(bronze.writeStream
    .format("parquet")
    .option("checkpointLocation", CKPT)
    .partitionBy("dt", "partition")
    .trigger(processingTime=os.environ.get("TRIGGER", "30 seconds"))
    .outputMode("append")
    .start(S3_PATH)
    .awaitTermination())
