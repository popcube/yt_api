import pandas as pd
from matplotlib import pyplot as plt
import sys, os
import csv

from dyn_api import main as scan_data
from make_timeline import make_timeline

## JST on UTC system
now = pd.Timestamp.now() + pd.Timedelta(hours=9)

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
  print("##### Trues in change flag df #####")
  print(change_flag_view_25[change_flag_df["view_25_changed"] == True])
  print(change_flag_date_25[change_flag_df["date_25_changed"] == True], flush=True)
  
  agg_df_index_diff = agg_df.index.to_series().diff().apply(lambda x: x.total_seconds())
  agg_df_view_25_diff = agg_df["view_25_views"].diff() / agg_df_index_diff
  agg_df_date_25_diff = agg_df["date_25_views"].diff() / agg_df_index_diff

  agg_df_view_25_diff.loc[change_flag_view_25] = float('nan')
  agg_df_date_25_diff.loc[change_flag_date_25] = float('nan')
  
  agg_diff_df = pd.concat([
    agg_df_view_25_diff,
    agg_df_date_25_diff
  ], axis="columns").rename(columns={0: "view_25_views", 1: "date_25_views"})
  
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
    print("##### Processing start #####", flush=True)
  elif idx in milestone_list:
    print(f"{milestone_list.index(idx) * 10}% ...", flush=True)  

## note that data of master_dict can change in the caller's side when changed in the called function
def each_calc(scanned_data, category_key="date_25"):
  master_dict = dict()
  
  for i in scanned_data:
    ## for every element in scanned_data, title can be included for all or excluded for all
    ## one sample of vid suffices to say that the element has title for all vids or not
    if "title" in i[category_key]["videos"][0].keys():
      for ii in i[category_key]["videos"]:
        master_dict[ii["id"]] = {
          "title": ii["title"],
          "date": pd.to_datetime(ii["date"]) + pd.Timedelta(hours=9),
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
      
  ## unofficial way to name DataFrame
  master_views_df.name = "views"
  master_likes_df.name = "likes"
  master_comments_df.name = "comments"
      
  return master_views_df, master_likes_df, master_comments_df, master_dict

###### Function Description ######
## input parameters:
## view_df index: pd.Timestamp, columns: id
## start_sr: index: id, values: pd.Timestamp
## end_offset: int [days]
## returns pd.Series
def get_speed(view_df, start_sr, end_offset):
  ## valid time window is 1 hour when the offset is shorter than 7 days
  ## for longer period, 1 day
  valid_time_window = 60 if end_offset < 7 else 60*24 # [min]
  valid_time_offset = valid_time_window / 2
  
  res_sr = pd.Series(index=view_df.columns)
  end_sr = start_sr + pd.Timedelta(days=end_offset)
  end_sr_min = end_sr - pd.Timedelta(minutes=valid_time_offset)
  end_sr_max = end_sr + pd.Timedelta(minutes=valid_time_offset)
  
  for id in view_df.columns:
    end_view_sr = view_df[id][(end_sr_min[id] <= view_df[id].index) & (view_df[id].index <= end_sr_max[id])]
    end_view_sr.dropna(inplace=True)
    if len(end_view_sr) > 0:
      past_days = (end_view_sr.index[-1] - start_sr[id]).total_seconds() / (60*60*24)
      res_sr[id] = end_view_sr.iloc[-1] / past_days
      
  return res_sr

###### Function Description #####
## input parameters:
## view_df index: pd.Timestamp, columns: id
## end_offset: int [days]
## returns pd.Series
def get_now_speed(view_df, end_offset):
  ## valid time window is 1 hour when the offset is shorter than 7 days
  ## for longer period, 1 day
  valid_time_window = 60 if end_offset < 7 else 60*24 # [min]
  res_sr = pd.Series(index=view_df.columns)
  start = now
  start_min = now - pd.Timedelta(minutes=valid_time_window)
  end = start - pd.Timedelta(days=end_offset)
  end_min = end - pd.Timedelta(minutes=valid_time_window)
  
  for id in view_df.columns:
    start_view_sr = view_df[id][(start_min <= view_df[id].index) & (view_df[id].index <= start)]
    end_view_sr = view_df[id][(end_min <= view_df[id].index) & (view_df[id].index <= end)]
    start_view_sr.dropna(inplace=True)
    end_view_sr.dropna(inplace=True)
    if len(start_view_sr) > 0 and len(end_view_sr) > 0:
      past_days = (start_view_sr.index[-1] - end_view_sr.index[-1]).total_seconds() / (60*60*24)
      res_sr[id] = (start_view_sr.iloc[-1] - end_view_sr.iloc[-1]) / past_days
      
  return res_sr
  

###### scheme of input df ######
## columns = list of video ids
## index = timestamp
def merge_data_and_make_graphs(df_date_views, df_date_likes, df_date_comments, df_view_views, df_view_likes, df_view_comments, date_master_dict, view_master_dict):
  
  ## merge the video date when duplicated in date and view dfs
  # for df_date, df_view in zip([df_date_views, df_date_likes, df_date_comments], [df_view_views, df_view_likes, df_view_comments]):
  #   dupe_cols = []
  #   for date_column in df_date.columns:
  #     if date_column in df_view.columns:
  #       dupe_cols.append(date_column)
  #       # merge the Series with the first values for the dupe index
  #       df_view[date_column] = pd.concat([df_date[date_column], df_view[date_column]]).groupby(level=0).first()
  #   df_date.drop(columns=dupe_cols, inplace=True)

  ## merge the video data when duplicated in date and view master_dicts
  ## delete the dupe data from date master_dict and dfs
  dupe_cols = list(set(date_master_dict.keys()) & set(view_master_dict.keys()))
  for df_date, df_view in zip([df_date_views, df_date_likes, df_date_comments], [df_view_views, df_view_likes, df_view_comments]):
    df_view[dupe_cols] = pd.concat([df_date[dupe_cols], df_view[dupe_cols]]).groupby(level=0).first()
    df_date.drop(columns=dupe_cols, inplace=True)
    
  ## from here onwards, only one master_dict
  master_dict = date_master_dict | view_master_dict
  
  df_date_25_info = pd.DataFrame(df_date_views.columns, columns=["id"])
  df_date_25_info["date"] = df_date_25_info["id"].apply(lambda id: master_dict[id]["date"])
  df_date_25_info.sort_values("date", ascending=False, inplace=True)
  df_date_25_info["title"] = df_date_25_info["id"].apply(lambda id: master_dict[id]["title"])
  df_date_25_info["view"] = df_date_25_info["id"].map(df_date_views.max())
  df_date_25_info.set_index("id", inplace=True)
  for df_date_temp in [df_date_views, df_date_likes, df_date_comments]:
    for period_day in [1, 7, 30, 90]:
      df_date_25_info[f"day{period_day}_{df_date_temp.name}_speed[/day]"] = get_speed(
        df_date_temp, start_sr=df_date_25_info["date"], end_offset=period_day)
      # df_date_25_info["day3_view_speed[/day]"] = get_speed(df_date_views, start_sr=df_date_25_info["date"], end_offset=3)
      # df_date_25_info["day7_view_speed[/day]"] = get_speed(df_date_views, start_sr=df_date_25_info["date"], end_offset=7)
      # df_date_25_info["day30_view_speed[/day]"] = get_speed(df_date_views, start_sr=df_date_25_info["date"], end_offset=30)
      df_date_25_info[f"now{period_day}_{df_date_temp.name}_speed[/day]"] = get_now_speed(
        df_date_temp, end_offset=period_day)
      # df_date_25_info["now3_view_speed[/day]"] = get_now_speed(df_date_views, end_offset=3)
      # df_date_25_info["now7_view_speed[/day]"] = get_now_speed(df_date_views, end_offset=7)
      # df_date_25_info["now30_view_speed[/day]"] = get_now_speed(df_date_views, end_offset=30)
  
  df_view_25_info = pd.DataFrame(df_view_views.columns, columns=["id"])
  df_view_25_info["view"] = df_view_25_info["id"].map(df_view_views.max())
  df_view_25_info.sort_values("view", ascending=False, inplace=True)
  df_view_25_info["title"] = df_view_25_info["id"].apply(lambda id: master_dict[id]["title"])
  df_view_25_info["date"] = df_view_25_info["id"].apply(lambda id: master_dict[id]["date"])
  df_view_25_info.set_index("id", inplace=True)
  for df_view_temp in [df_view_views, df_view_likes, df_view_comments]:
    for period_day in [1, 7, 30, 90]:
      df_view_25_info[f"now{period_day}_{df_view_temp.name}_speed[/day]"] = get_now_speed(
        df_view_temp, end_offset=period_day)
      # df_view_25_info["now3_view_speed[/day]"] = get_now_speed(df_view_views, end_offset=3)
      # df_view_25_info["now7_view_speed[/day]"] = get_now_speed(df_view_views, end_offset=7)
      # df_view_25_info["now30_view_speed[/day]"] = get_now_speed(df_view_views, end_offset=30)
      
  df_date_25_info.to_csv("summary_list.csv", index=True, encoding='utf-8', float_format='%.1f')
  df_view_25_info.to_csv("summary_list.csv", index=True, encoding='utf-8', float_format='%.1f', mode='a')
        
  for category_key, master_views_df, master_likes_df, master_comments_df in [
    ["[date_25]", df_date_views, df_date_likes, df_date_comments],
    ["[view_25]", df_view_views, df_view_likes, df_view_comments]
  ]:
    for df_prefix, df in zip(["[views]", "[likes]", "[comments]"], [master_views_df, master_likes_df, master_comments_df]):
      for id in df.columns:
        fig_title = df_prefix + " " + master_dict[id]["title"]
        fig_name = category_key + id + df_prefix
        video_sr = df[id].dropna()
        try:
          make_timeline(video_sr.index, video_sr, figname=fig_name, plt_title=fig_title)
        except Exception as e:
          print(e)
          print(f"ERROR at make_timeline for {id}, {df_prefix}")
          video_sr.to_csv(fig_name + ".csv")
      
if __name__ == "__main__":
  if os.environ.get("AWS_ACCESS_KEY_ID"):
    scanned_data = scan_data()
    
    ## convert fetch_time from string to pd.Timestamp
    ## and from UST to JST
    for idx in range(len(scanned_data)):
      scanned_data[idx]["fetch_time"] = pd.to_datetime(scanned_data[idx]["fetch_time"]) + pd.Timedelta(hours=9)    
    
    df_date_views, df_date_likes, df_date_comments, date_master_dict = each_calc(scanned_data, category_key="date_25")
    df_view_views, df_view_likes, df_view_comments, view_master_dict = each_calc(scanned_data, category_key="view_25")
    merge_data_and_make_graphs(df_date_views, df_date_likes, df_date_comments, df_view_views, df_view_likes, df_view_comments, date_master_dict, view_master_dict)
    agg_calc(scanned_data)
  # else:
  #   agg_calc([], local=True)
