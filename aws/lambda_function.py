import boto3
from boto3.dynamodb.conditions import Attr
from datetime import datetime

from yt_main import main as yt_main
from yt_main import query_test

def lambda_handler(event, context):
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('yt_main_5min')

  now_str = datetime.now().isoformat(timespec='microseconds')[:-4]
  
  view_ids = []
  date_ids = []
  # print(event)
  # sys.exit(0)
  if not event.get("event"):
    last_items_dict = table.query(
      KeyConditionExpression=boto3.dynamodb.conditions.Key("account").eq("pj_sekai"),
      ScanIndexForward=False,
      Limit=1,
      # FilterExpression=(
      #   Attr("view_25.videos[0].date").exists() &
      #   Attr("view_25.videos[0].title").exists() 
      # ),
      # ReturnConsumedCapacity="INDEXES"
    )
    last_item_dict = last_items_dict["Items"][0]
    # print(last_item_dict)
    view_ids = [last_item["id"] for last_item in last_item_dict["view_25"]["videos"]]
    date_ids = [last_item["id"] for last_item in last_item_dict["date_25"]["videos"]]
    
  elif event.get("event") == "hourly_update":
    print("This is the hourly update!")
    
  else:
    print("this is the testing mode")
    srch_queries = {
      # "key": api_key,
      # "channelId": ch_id,
      "part": "snippet",
      # "type": "video",
      # "order": "date",
      "order": "viewCount",
      # "maxResults": 25
    }
    view_25_data = query_test(srch_queries)
    print("type video")
    print(view_25_data["id"].to_list())
    
    srch_queries = {
      # "key": api_key,
      # "channelId": ch_id,
      "part": "snippet",
      "type": "video",
      # "order": "date",
      "order": "viewCount",
      # "maxResults": 25
    }
    # del srch_queries["type"]
    view_25_data = query_test(srch_queries)
    print("no type video")
    print(view_25_data["id"].to_list())
    
    
  yt_dict = yt_main(view_ids=view_ids, date_ids=date_ids)
  try:
    table.put_item(
      Item = {
        "account": "pj_sekai",
        "fetch_time": now_str,
        **yt_dict
      }
    )
  except Exception as e:
    print("ERROR at putting result in dynamoDB table!!")
    print(e)
    print(yt_dict)

  return {
    'statusCode': 200
  }
