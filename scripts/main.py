from dyn_api import main as scan_data
import pandas as pd
from matplotlib import pyplot as plt

def main():
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
  
  plt.plot(agg_df["date"], agg_df["view_25_views"])
  plt.savefig("./test_1.png")
  plt.plot(agg_df["date"].iloc[1:,:], agg_df["view_25_views"].diff().dropna())
  plt.savefig("./test_2.png")
  plt.plot(agg_df["date"], agg_df["date_25_views"])
  plt.savefig("./test_3.png")
  plt.plot(agg_df["date"].iloc[1:,:], agg_df["date_25_views"].diff().dropna())
  plt.savefig("./test_4.png")


if __name__ == "__main__":
  main()
