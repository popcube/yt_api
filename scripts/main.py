import pandas as pd
from matplotlib import pyplot as plt
import sys, os

from dyn_api import main as scan_data
from make_timeline import make_timeline

def main(local):
  if local:
    agg_df = pd.read_csv("./agg_df")
    agg_diff_df = pd.read_csv("./agg_diff_df")
  
  else:    
    scanned_data = scan_data()
    
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
    agg_df["date"] = pd.to_datetime(agg_df["date"])
    agg_df.set_index("date", inplace=True)
    agg_diff_df = pd.concat([
      agg_df["view_25_views"].diff(),
      agg_df["date_25_views"].diff(),
    ], axis="columns").dropna(how="any")
    
    agg_df.to_csv("./agg_df.csv")
    agg_diff_df.to_csv("./agg_diff_df.csv")
  
  make_timeline(agg_df.index, agg_df["view_25_views"], figname="view_25_views")
  make_timeline(agg_diff_df.index, agg_diff_df["view_25_views"], figname="view_25_views_diff")
  make_timeline(agg_df.index, agg_df["date_25_views"], figname="date_25_views")
  make_timeline(agg_diff_df.index, agg_diff_df["date_25_views"], figname="date_25_views_diff")

if __name__ == "__main__":
  if os.environ.get("AWS_ACCESS_KEY_ID"):
    main()
  else:
    main("local")
