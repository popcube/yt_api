from matplotlib import pyplot as plt
import pandas as pd
import sys


plt.rcParams["font.family"] = "IPAexGothic"


def top_views(df):
  data_cols=["now30_view_speed[/day]","now7_view_speed[/day]","now3_view_speed[/day]","now1_view_speed[/day]"]
  # for col in data_cols:
  #   df[col] = -1 * df[col]

  x_axis = ["30days", "7days", "3days", "1day"]
  # cm_colors = plt.cm.get_cmap("Dark2").colors
  cm_colors = plt.cm.get_cmap("tab20").colors

  plt.figure(figsize=(7, 7))
  for idx in df.index[:13]:
    plt.plot(
      x_axis,
      df.loc[idx, data_cols],
      color=cm_colors[idx % len(cm_colors)],
      marker='o',
      linestyle='dashed',
      linewidth=1,
      markersize=5,
      label=df.loc[idx, "title"].replace("&amp;", "&"),
    )
    # if df.loc[idx, data_cols].mean() < 1000:
    #   print(df.loc[idx, data_cols])
  plt.legend(loc="upper left", bbox_to_anchor=(0, 0.8))
  plt.title("現在より○日前までの再生数増加率平均[views/day]")
  plt.tight_layout()
    
  # plt.show()
  plt.savefig("./local/top_views.png")
  plt.close()
  
def latest_views(df):
  # data_cols=["now30_view_speed[/day]","now7_view_speed[/day]","now3_view_speed[/day]","now1_view_speed[/day]"]
  data_cols=["day30_view_speed[/day]","day7_view_speed[/day]","day3_view_speed[/day]","day1_view_speed[/day]"]
  # for col in data_cols:
  #   df[col] = -1 * df[col]

  x_axis = ["30days", "7days", "3days", "1day"]
  # cm_colors = plt.cm.get_cmap("Dark2").colors
  cm_colors = plt.cm.get_cmap("tab10").colors

  plt.figure(figsize=(7, 7))
  for idx in df[data_cols].dropna(how="all").index[:25]:
    # try:
    plt.plot(
      x_axis,
      df.loc[idx, data_cols].apply(float),
      color=cm_colors[idx % len(cm_colors)],
      marker=['o', '^', 's', 'D'][idx // len(cm_colors)],
      linestyle='dashed',
      linewidth=1,
      markersize=5,
      label=df.loc[idx, "title"].replace("&amp;", "&"),
    )
    # except Exception as e:
    #   print(df.loc[idx-1, data_cols].apply(type))
    #   print(df.loc[idx, data_cols].apply(type))
    #   print(e)
  plt.legend(loc="upper left", bbox_to_anchor=(0, 1), framealpha=0)
  plt.title("リリースより○日後までの再生数増加率平均[views/day]")
  plt.tight_layout()
    
  # plt.show()
  # sys.exit(9)
  plt.savefig("./local/latest_views.png")
  plt.close()

if __name__ == "__main__":
  src_csv_path = "./summary_list.csv"
  break_row = 0
  with open(src_csv_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
      if line.startswith("id,") and idx != 0:
        break_row = idx
        break
      
  # print(break_idx)
  # sys.exit(0)


  df = pd.read_csv(src_csv_path, nrows=break_row, encoding="utf-8", parse_dates=True)
  latest_views(df)
  df = pd.read_csv(src_csv_path, skiprows=break_row, encoding="utf-8", parse_dates=True)
  top_views(df)
