import boto3
from datetime import datetime

def main():
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('yt_main')
  
  last_items_dict = table.query(
    KeyConditionExpression=boto3.dynamodb.conditions.Key("account").eq("pj_sekai"),
    ScanIndexForward=True,
    Limit=1,
    # ReturnConsumedCapacity="INDEXES"
  )

if __name__ == "__main__":
  main()