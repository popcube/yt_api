import pandas as pd
from matplotlib import pyplot as plt
import sys, os

from dyn_api import main as scan_data
from make_timeline import make_timeline

def detect_video_id_change(scanned_data):
  change_flag_df = pd.DataFrame([[False]*2]*len(scanned_data), columns=["view_25_changed", "date_25_changed"])
  for i in range(1, len(scanned_data)):
    if set(videos["id"] for videos in scanned_data[i]["view_25"]["videos"]) \
        != set(videos["id"] for videos in scanned_data[i-1]["view_25"]["videos"]):
      change_flag_df.loc[i, "view_25_changed"] = True
    if set(videos["id"] for videos in scanned_data[i]["date_25"]["videos"]) \
        != set(videos["id"] for videos in scanned_data[i-1]["date_25"]["videos"]):
      change_flag_df.loc[i, "date_25_changed"] = True
  return change_flag_df

def agg_calc(scanned_data, local=False):
  if local:
    agg_df = pd.read_csv("./agg_df.csv")
    # agg_diff_df = pd.read_csv("./agg_diff_df.csv", index_col="date", parse_dates=["date"])
    agg_df["date"] = pd.to_datetime(agg_df["date"]) + pd.Timedelta(hours=9)
  
  else:    
    agg_list = [
      [
        i["fetch_time"],
        i["view_25"]["views"],
        i["view_25"]["likes"],
        i["view_25"]["comments"],
        i["date_25"]["views"],
        i["date_25"]["likes"],
        i["date_25"]["comments"],
      ]
      for i in scanned_data
    ]
    agg_df = pd.DataFrame(agg_list, columns=["date", "view_25_views", "view_25_likes", "view_25_comments", "date_25_views", "date_25_likes", "date_25_comments"])
  
  
  # agg_df["date"] = pd.to_datetime(agg_df["date"]) + pd.Timedelta(hours=9)
  agg_df.set_index("date", inplace=True)
  
  ## This conversion is to avoid matplotlib.ticker error in GHAction
  ## Note that DynamoDB responds in Decimal.decimal type
  agg_df = agg_df.map(int)

  change_flag_df = detect_video_id_change(scanned_data)
  change_flag_df.set_index(agg_df.index, inplace=True)
  change_flag_view_25 = change_flag_df["view_25_changed"][change_flag_df["view_25_changed"] == True]
  change_flag_date_25 = change_flag_df["date_25_changed"][change_flag_df["date_25_changed"] == True]
  print()
  print("##### change flag df #####")
  print(change_flag_df)
  print()
  print("##### True point in change flag df #####")
  print(change_flag_view_25)
  print(change_flag_date_25)

  agg_df_view_25_diff = agg_df["view_25_views"].diff()
  agg_df_date_25_diff = agg_df["date_25_views"].diff()

  agg_df_view_25_diff.loc[change_flag_view_25] = float('nan')
  agg_df_date_25_diff.loc[change_flag_date_25] = float('nan')
  
  agg_diff_df = pd.concat([
    agg_df_view_25_diff,
    agg_df_date_25_diff
  ], axis="columns")
  
  agg_df.to_csv("./agg_df.csv")
  agg_diff_df.to_csv("./agg_diff_df.csv")
  
  make_timeline(agg_df.index, agg_df["view_25_views"], figname="view_25_views")
  make_timeline(agg_diff_df.index, agg_diff_df["view_25_views"], figname="view_25_views_diff")
  make_timeline(agg_df.index, agg_df["date_25_views"], figname="date_25_views")
  make_timeline(agg_diff_df.index, agg_diff_df["date_25_views"], figname="date_25_views_diff")
  
  yesterday_ts = pd.Timestamp.now() + pd.Timedelta(days=-1)
  yesterday_str = yesterday_ts.strftime("%Y-%m-%d")
  for hour in set(agg_df.loc[yesterday_str].index.hour):
    make_timeline(
      agg_df.loc[f"{yesterday_str} {hour:02}"].index[1:],
      agg_df.loc[f"{yesterday_str} {hour:02}"]["date_25_views"][1:],
      figname=f"date_25_views_{yesterday_str}_{hour}")
    make_timeline(
      agg_diff_df.loc[f"{yesterday_str} {hour:02}"].index[1:],
      agg_diff_df.loc[f"{yesterday_str} {hour:02}"]["date_25_views"][1:],
      figname=f"date_25_views_diff_{yesterday_str}_{hour}")

def each_calc(scanned_data):
  id_set = set()
  for i in scanned_data:
    if "title" in i["date_25"]["videos"][0].keys():
      for ii in i["date_25"]["videos"]:
        id_set.add(ii["id"])
  print(id_set)
  
  test_id = list(id_set)[0]
  test_id_df = pd.DataFrame(columns=["views", "likes", "comments"])
  
  test_id_info = []
  for i in scanned_data:
    data_ids = [ii["id"] for ii in i["date_25"]["videos"]]
    if test_id in data_ids:
      test_id_idx = data_ids.index(test_id)
      test_id_df.loc[i["fetch_time"]] = i["date_25"]["videos"][test_id_idx]
      if len(test_id_info) == 0 and i["date_25"]["videos"][test_id_idx].get("title"):
        test_id_info = [i["date_25"]["videos"][test_id_idx]["title"],
                         i["date_25"]["videos"][test_id_idx]["date"],
                         test_id]
  
  print(test_id_df)
  test_id_df = test_id_df.map(int)
  test_id_df.to_csv("./test_output.csv")
  
  make_timeline(test_id_df.index, test_id_df["views"], "test_output_views")
  make_timeline(test_id_df.index, test_id_df["likes"], "test_output_likes")
  make_timeline(test_id_df.index, test_id_df["comments"], "test_output_comments")
  

if __name__ == "__main__":
  if os.environ.get("AWS_ACCESS_KEY_ID"):
    scanned_data = scan_data()
    
    ## convert fetch_time from UST to JST
    for idx in range(len(scanned_data)):
      scanned_data[idx]["fetch_time"] = pd.to_datetime(scanned_data[idx]["fetch_time"]) + pd.Timedelta(hours=9)    
    
    each_calc(scanned_data)
    agg_calc(scanned_data)
  else:
    agg_calc([], local=True)
