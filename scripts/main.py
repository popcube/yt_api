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

def agg_calc(scanned_data):
  # if local:
  #   agg_df = pd.read_csv("./agg_df.csv")
  #   # agg_diff_df = pd.read_csv("./agg_diff_df.csv", index_col="date", parse_dates=["date"])
  #   agg_df["date"] = pd.to_datetime(agg_df["date"]) + pd.Timedelta(hours=9)
  
  # else:    
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
  change_flag_view_25 = change_flag_df["view_25_changed"]
  change_flag_date_25 = change_flag_df["date_25_changed"]
  print()
  print("##### change flag df #####")
  print(change_flag_df)
  print()
  print("##### True point in change flag df #####")
  print(change_flag_view_25[change_flag_df["view_25_changed"] == True])
  print(change_flag_date_25[change_flag_df["date_25_changed"] == True], flush=True)

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
  
  agg_diff_view_25_views_df = agg_diff_df["view_25_views"].dropna()
  agg_diff_date_25_views_df = agg_diff_df["date_25_views"].dropna()
  
  make_timeline(agg_df.index, agg_df["view_25_views"], figname="view_25_views")
  make_timeline(agg_diff_view_25_views_df.index, agg_diff_view_25_views_df, figname="view_25_views_diff")
  make_timeline(agg_df.index, agg_df["date_25_views"], figname="date_25_views")
  make_timeline(agg_diff_date_25_views_df.index, agg_diff_date_25_views_df, figname="date_25_views_diff")
  
  # yesterday_ts = pd.Timestamp.now() + pd.Timedelta(days=-1)
  # yesterday_str = yesterday_ts.strftime("%Y-%m-%d")
  # for hour in set(agg_df.loc[yesterday_str].index.hour):
  #   make_timeline(
  #     agg_df.loc[f"{yesterday_str} {hour:02}"].index,
  #     agg_df.loc[f"{yesterday_str} {hour:02}"]["date_25_views"],
  #     figname=f"date_25_views_{yesterday_str}_{hour}")
  #   make_timeline(
  #     agg_diff_date_25_views_df.loc[f"{yesterday_str} {hour:02}"].index,
  #     agg_diff_date_25_views_df.loc[f"{yesterday_str} {hour:02}"],
  #     figname=f"date_25_views_diff_{yesterday_str}_{hour}")
    
def show_progress(idx, target_len):
  milestone_list = range(0, target_len, int(target_len / 10))
  if idx == 0:
    print()
    print("##### Processing start #####")
  elif idx in milestone_list:
    print(f"{milestone_list.index(idx) * 10}% ...", flush=True)  

def each_calc(scanned_data, category_key="date_25"):
  master_dict = dict()
  for i in scanned_data:
    ## for every element in scanned_data, title can be included for all or excluded for all
    ## one sample of vid suffices to say that the element has title for all vids or not
    if "title" in i[category_key]["videos"][0].keys():
      for ii in i[category_key]["videos"]:
        master_dict[ii["id"]] = {
          "title": ii["title"],
          "date": ii["date"],
          # "data": pd.DataFrame(columns=["views", "likes", "comments"])
        }
  # print(id_set, flush=True)
  print()
  print(f"##### category: {category_key} #####")
  print(f"number of videos found: {len(master_dict)}", flush=True)
  
  master_views_df = pd.DataFrame(columns=master_dict.keys())
  master_likes_df = pd.DataFrame(columns=master_dict.keys())
  master_comments_df = pd.DataFrame(columns=master_dict.keys())
    
  for scanned_data_idx, data in enumerate(scanned_data):
    show_progress(scanned_data_idx, len(scanned_data))
    for video_data_point in data[category_key]["videos"]:
      master_views_df.loc[data["fetch_time"], video_data_point["id"]] = int(video_data_point["views"])
      master_likes_df.loc[data["fetch_time"], video_data_point["id"]] = int(video_data_point["likes"])
      master_comments_df.loc[data["fetch_time"], video_data_point["id"]] = int(video_data_point["comments"])
  
  for df_suffix, df in zip(["_views", "_likes", "_comments"], [master_views_df, master_likes_df, master_comments_df]):
    for id in df.columns:
      fig_title = master_dict[id]["title"] + "_" + category_key + df_suffix
      fig_name = category_key + df_suffix + "_" + id
      video_sr = df[id].dropna()
      try:
        make_timeline(video_sr.index, video_sr, figname=fig_name, plt_title=fig_title)
      except Exception as e:
        print(e)
        print(f"ERROR at make_timeline for {id}, {category_key}")
        video_sr.to_csv(fig_name + ".csv")
      
if __name__ == "__main__":
  if os.environ.get("AWS_ACCESS_KEY_ID"):
    scanned_data = scan_data()
    
    ## convert fetch_time from string to pd.Timestamp
    ## and from UST to JST
    for idx in range(len(scanned_data)):
      scanned_data[idx]["fetch_time"] = pd.to_datetime(scanned_data[idx]["fetch_time"]) + pd.Timedelta(hours=9)    
    
    each_calc(scanned_data, "date_25")
    each_calc(scanned_data, "view_25")
    agg_calc(scanned_data)
  # else:
  #   agg_calc([], local=True)
