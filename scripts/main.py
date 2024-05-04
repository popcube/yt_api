import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from time import sleep
import sys

def get_last_hourly_update():
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
    ReturnConsumedCapacity="TOTAL"
    )
  
  print(last_items_dict["ConsumedCapacity"]["CapacityUnits"])
  print()
  print(len(last_items_dict["Items"]))
  print(last_items_dict["Items"][0]["view_25"])
  print(last_items_dict["Items"][0]["date_25"])
  
def main():
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('yt_main')
  scan_param = dict(
    ReturnConsumedCapacity="TOTAL",
    Limit=20
  )
  scanned_raw = []
  
  while True:
    scanned_raw_dict = table.scan(**scan_param)
    # print(len(scanned_raw_dict["Items"]))
    # print(scanned_raw_dict["LastEvaluatedKey"])
    # print()
    
    # scanned_raw_dict.pop("Items")
    # print(scanned_raw_dict)
    # sys.exit(1)
    
    if scanned_raw_dict["ResponseMetadata"]["HTTPStatusCode"] == 200:
      scanned_raw += scanned_raw_dict["Items"]
      if (scanned_raw_dict.get("LastEvaluatedKey", False)):
        print(f"data succcessfully scanned. count: {scanned_raw_dict["Count"]}, paginating...", flush=True)
      else:        
        print(f"data succcessfully scanned. count: {scanned_raw_dict["Count"]}, done!", flush=True)
        break
    else:
      print("ERROR at scan")
      scanned_raw_dict.pop("Items")
      print(scanned_raw_dict)
      raise ValueError("ERROR at scan")
    scan_param["ExclusiveStartKey"] = scanned_raw_dict["LastEvaluatedKey"]
    sleep(1) # wait 1 sec
  
  print(len(scanned_raw))
  print(scanned_raw[-1])
  print(scanned_raw[-1]["fetch_time"])

if __name__ == "__main__":
  main()