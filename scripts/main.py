import pandas as pd
from matplotlib import pyplot as plt
import sys, os

from dyn_api import main as scan_data
from make_timeline import make_timeline

def agg_calc(local=False):
  if local:
    agg_df = pd.read_csv("./agg_df.csv")
    # agg_diff_df = pd.read_csv("./agg_diff_df.csv", index_col="date", parse_dates=["date"])
  
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
  
  
  agg_df["date"] = pd.to_datetime(agg_df["date"]) + pd.Timedelta(hours=9)
  agg_df.set_index("date", inplace=True)
  
  ## This conversion is to avoid matplotlib.ticker error in GHAction
  ## Note that DynamoDB responds in Decimal.decimal type
  agg_df = agg_df.map(int)
  
  agg_diff_df = pd.concat([
    agg_df["view_25_views"].diff(),
    agg_df["date_25_views"].diff(),
  ], axis="columns").dropna(how="any")
  
  agg_df.to_csv("./agg_df.csv")
  agg_diff_df.to_csv("./agg_diff_df.csv")
  
  make_timeline(agg_df.index, agg_df["view_25_views"], figname="view_25_views")
  make_timeline(agg_diff_df.index, agg_diff_df["view_25_views"], figname="view_25_views_diff")
  for hour in set(agg_df.loc["2024-05-04"].index.hour):
    make_timeline(
      agg_df.loc[f"2024-05-04 {hour:02}"].index[1:],
      agg_df.loc[f"2024-05-04 {hour:02}"]["date_25_views"][1:],
      figname=f"date_25_views_{hour}")
    make_timeline(
      agg_diff_df.loc[f"2024-05-04 {hour:02}"].index[1:],
      agg_diff_df.loc[f"2024-05-04 {hour:02}"]["date_25_views"][1:],
      figname=f"date_25_views_diff_{hour}")

def each_calc():
  scanned_data = scan_data()
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
  test_id_df.to_csv("./test_output.csv")
  
  plt.plot(test_id_df.index, test_id_df["views"])
  plt.savefig("./test_output_views.png")
  plt.close()
  plt.plot(test_id_df.index, test_id_df["likes"])
  plt.savefig("./test_output_likes.png")
  plt.close()
  plt.plot(test_id_df.index, test_id_df["comments"])
  plt.savefig("./test_output_comments.png")
  plt.close()
  

if __name__ == "__main__":
  if os.environ.get("AWS_ACCESS_KEY_ID"):
    each_calc()
    # agg_calc()
  else:
    agg_calc(local=True)
