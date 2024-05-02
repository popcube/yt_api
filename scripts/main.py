import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

def main():
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('yt_main')
  
  last_items_dict = table.query(
    KeyConditionExpression=Key("account").eq("pj_sekai"),
    ScanIndexForward=False,
    Limit=120,
    # ExpressionAttributeNames={"#yr": "year"},
    FilterExpression=(
        Attr("view_25.videos[0].date").exists() &
        Attr("view_25.videos[0].title").exists() 
      ),
    ReturnConsumedCapacity="INDEXES"
    )
  
  print(last_items_dict)

if __name__ == "__main__":
  main()