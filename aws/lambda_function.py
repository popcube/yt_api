import boto3
from datetime import datetime

from yt_main import main as yt_main

def lambda_handler(event, context):
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('yt_main')

  now_str = datetime.now().isoformat(timespec='microseconds')[:-4]
  
  view_ids = []
  date_ids = []
  # print(event)
  # sys.exit(0)
  if event.get("event") != "hourly_update":
    last_items_dict = table.query(
      KeyConditionExpression=boto3.dynamodb.conditions.Key("account").eq("pj_sekai"),
      ScanIndexForward=False,
      Limit=1,
      # ReturnConsumedCapacity="INDEXES"
    )
    last_item_dict = last_items_dict["Items"][0]
    # print(last_item_dict)
    view_ids = [last_item["id"] for last_item in last_item_dict["view_25"]["videos"]]
    date_ids = [last_item["id"] for last_item in last_item_dict["date_25"]["videos"]]

  yt_dict = yt_main(view_ids=view_ids, date_ids=date_ids)
  table.put_item(
    Item = {
      "account": "pj_sekai",
      "fetch_time": now_str,
      **yt_dict
    }
  )


  return {
    'statusCode': 200
  }
