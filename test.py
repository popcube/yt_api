import os, sys, requests, json
import pandas as pd

api_key = os.environ.get("API_KEY")
ch_query_part = [
  # "auditDetails",
  # "brandingSettings",
  # "contentDetails",
  # "contentOwnerDetails",
  "id",
  # "localizations",
  # "snippet",
  "statistics",
  # "status",
  # "topicDetails",
]
if not api_key:
  with open("./local/google api key.txt", "r") as f:
    api_key = f.read()

# print(api_key)

ch_base_url = "https://www.googleapis.com/youtube/v3/channels"
srch_base_url = "https://www.googleapis.com/youtube/v3/search"
vid_base_url = "https://www.googleapis.com/youtube/v3/videos"
ch_queries = {
  "key": api_key,
  "forHandle": "@pj_sekai_colorfulstage",
  "part": ",".join(ch_query_part)
}
# res = requests.get(ch_base_url, params=ch_queries)
# print(res.text)

# sys.exit()
# ch_id = json.loads(res.text)["items"][0]["id"]
ch_id = "UCdMGYXL38w6htx6Yf9YJa-w"
# print(ch_id)
srch_queries = {
  "key": api_key,
  "channelId": ch_id,
  "part": "snippet",
  # "type": "video",
  # "order": "date",
  "order": "viewCount",
  "maxResults": 25
}
# res = requests.get(srch_base_url, params=srch_queries)
# with open("./local/temp.txt", "w", errors="ignore", encoding="utf-8") as f:
#   f.write(res.text)
  
# sys.exit(9)

with open("./local/temp.txt", "r", errors="ignore", encoding="utf-8") as f:
  temp_text = f.read()
  
# res_dict = json.loads(res.text)
res_dict = json.loads(temp_text)
res_items = [
  [
    res_item["snippet"]["publishedAt"],
    res_item["snippet"]["title"],
    res_item["id"].get("videoId")
  ] for res_item in res_dict["items"]
]
# print(res_items)
res_df = pd.DataFrame(res_items, columns=["date", "title", "id"])
res_df["date"] = pd.to_datetime(res_df["date"])
res_df.set_index("date", inplace=True)
print(res_df["id"].to_list())

# sys.exit(0)
# res_df = res_df.to_timestamp()
print(res_df)
vid_query_part = [
  # "contentDetails",
  # "fileDetails",
  # "id",
  "liveStreamingDetails",
  # "localizations",
  # "player",
  # "processingDetails",
  # "recordingDetails",
  # "snippet",
  "statistics",
  # "status",
  # "suggestions",
  # "topicDetails",
]
vid_queries = {
  "key": api_key,
  "part": ",".join(vid_query_part),
  # "id": "Vx25rib86pc,SKfNzeuWtNg"
  "id": ",".join(res_df["id"].dropna().to_list() + ["lMXlOPGjwUI", "zw0JHV7nrUg"])
}

res = requests.get(vid_base_url, params=vid_queries)
with open("./local/temp2.txt", "w", errors="ignore", encoding="utf-8") as f:
  f.write(res.text)