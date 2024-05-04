import os, requests, sys, json
import pandas as pd

api_key = os.environ["YT_API_KEY"]

ch_base_url = "https://www.googleapis.com/youtube/v3/channels"
srch_base_url = "https://www.googleapis.com/youtube/v3/search"
vid_base_url = "https://www.googleapis.com/youtube/v3/videos"
ch_id = "UCdMGYXL38w6htx6Yf9YJa-w"


  
def query_25(srch_queries):
    
  res = requests.get(srch_base_url, params=srch_queries)
  
  if not res.ok:
    print("ERROR: query_25 request failed")
    print(res.status_code)
    print(res.content)
    sys.exit(1)
    
  res_dict = json.loads(res.text)    
  res_items = [
    [
      res_item["id"]["videoId"],
      res_item["snippet"]["publishedAt"],
      res_item["snippet"]["title"],
    ] for res_item in res_dict["items"]
  ]
  # print(res_items)
  res_df = pd.DataFrame(res_items, columns=["id", "date", "title"])
  res_df["date"] = pd.to_datetime(res_df["date"], utc=True)
  # res_df.set_index("date", inplace=True)
  return res_df

def date_25():
  srch_queries = {
    "key": api_key,
    "channelId": ch_id,
    "part": "snippet",
    # "type": "video",
    "order": "date",
    # "order": "viewCount",
    "maxResults": 25
  }
  return query_25(srch_queries)

def view_25():
  srch_queries = {
    "key": api_key,
    "channelId": ch_id,
    "part": "snippet",
    # "type": "video",
    # "order": "date",
    "order": "viewCount",
    "maxResults": 25
  }
  return query_25(srch_queries)

def parse_yt_date(item):
  if "liveStreamingDetails" in item.keys():
    if "actualStartTime" in item["liveStreamingDetails"]:
      return item["liveStreamingDetails"]["actualStartTime"]
    elif "scheduledStartTime" in item["liveStreamingDetails"]:
      return item["liveStreamingDetails"]["scheduledStartTime"]
  
  return ""

def videos_50(ids):
  srch_queries = {
  "key": api_key,
  "part": "liveStreamingDetails,statistics",
  # "id": "Vx25rib86pc,SKfNzeuWtNg"
  "id": ",".join(ids)
  }
  
  res = requests.get(vid_base_url, params=srch_queries)

  if not res.ok:
    print("ERROR: video_25 request failed")
    print(res.status_code)
    print(res.content)
    sys.exit(1)
    
  # with open("./local/video_50_data.txt", "w") as f:
  #   f.write(res.text)
    
  res_dict = json.loads(res.text)    
  res_items = [
    [
      res_item["id"],
      int(res_item["statistics"]["viewCount"]),
      int(res_item["statistics"]["likeCount"]),
      int(res_item["statistics"]["commentCount"]),
      parse_yt_date(res_item)
    ] for res_item in res_dict["items"]
  ]
  # print(res_items)
  res_df = pd.DataFrame(res_items, columns=["id", "views", "likes", "comments", "liveDate"])
  ### coerce option enables "" to be interpretted as pd.NaT
  res_df["liveDate"] = pd.to_datetime(res_df["liveDate"], errors="coerce", utc=True)
  
  return res_df
  
def parse_25_data_to_dict(df_25):
  df_corrupt = df_25[df_25["found"] != "both"]
  if len(df_corrupt) > 0:
    print("WARNING some videos cannot be extracted!")
    print(df_corrupt)
  
  if "date" in df_25.columns:
    ### consolidate date and liveDate fields to date
    ### Timestamp object aware of tzinfo needs to be truncated 6 chars more
    df_25["date"] = df_25[["date", "liveDate"]].max(axis="columns").apply(
      lambda x: x.isoformat(timespec='microseconds', )[:-10])
  df_25.drop(["liveDate", "found"], axis="columns", inplace=True)
  
  ### get total values
  ### convert type from np.int64 to int
  df_25_views = int(df_25["views"].sum())
  df_25_likes = int(df_25["likes"].sum())
  df_25_comments = int(df_25["comments"].sum())
  
  return {
    "views": df_25_views,
    "likes": df_25_likes,
    "comments": df_25_comments,
    "videos": list(df_25.to_dict(orient="index").values())
  }

def main(view_ids=[], date_ids=[]):
  # date_25_data = pd.DataFrame()
  # view_25_data = pd.DataFrame()
  # id_50 = pd.Series()
  
  if len(view_ids):
    date_25_data = pd.DataFrame(date_ids, columns=["id"])
  else:
    date_25_data = date_25()
  
  if len(date_ids) > 0:
    view_25_data = pd.DataFrame(view_ids, columns=["id"])
  else:
    view_25_data = view_25()
  
  id_50 = pd.concat([date_25_data["id"], view_25_data["id"]], axis="index", ignore_index=True)    
  id_50.drop_duplicates(inplace=True)
  # print(id_50)
  # sys.exit(0)
  
  video_50_data = videos_50(id_50)
  print(f'{len(video_50_data)} videos are found!')
  print("now processing...")
  date_25_data = date_25_data.merge(video_50_data, how="left", on="id", indicator="found")
  view_25_data = view_25_data.merge(video_50_data, how="left", on="id", indicator="found")
  
  date_25_dict = parse_25_data_to_dict(date_25_data)
  view_25_dict = parse_25_data_to_dict(view_25_data)
  # print(date_25_dict)
  # print(view_25_dict)
  # date_25_data.to_csv("./local/date_data.csv", errors="ignore")
  # view_25_data.to_csv("./local/videw_data.csv", errors="ignore")
  
  return {
    "date_25": date_25_dict,
    "view_25": view_25_dict
  }
  
  
if __name__ == "__main__":
  res_dict = main()
  with open("./local/res.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(res_dict, indent=2, ensure_ascii=False, default=int))