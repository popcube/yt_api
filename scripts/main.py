import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

def main():
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('yt_main')
  
  last_items_dict = table.query(
    # KeyConditionExpression=Key("account").eq("pj_sekai"),
    ScanIndexForward=True,
    Limit=1,
    ProjectionExpression="view_25, date_25",
    # ExpressionAttributeNames={"#yr": "year"},
    KeyConditionExpression=(
        Key("account").eq("pj_sekai") &
        Key("view_25.videos[0].date").exists() &
        Key("view_25.videos[0].title").exists()
      ),
    ReturnConsumedCapacity="INDEXES"
    )
  
  print(last_items_dict)

if __name__ == "__main__":
  main()