from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import sys
import os
from functools import partial
# import numpy as np


plt.rcParams["font.family"] = "IPAexGothic"
    
# def yscale_f_forward(x_list: list):
#   res_list = []
#   for x in x_list:
#     if x >= 1:
#       res_list.append(np.power(10.0, x))
#     elif x > -1:
#       res_list.append(x * 10)
#     else:
#       res_list.append(-1 * np.power(10.0, abs(x)))
#   return np.array(res_list)
  
# def yscale_f_backward(x_list: list):
#   res_list = []
#   for x in x_list:
#     if x >= 10:
#       res_list.append(np.log(10.0, x))
#     elif x > -10:
#       res_list.append(x / 10)
#     else:
#       res_list.append(-1 * np.log(10.0, abs(x)))
#   return np.array(res_list)
def func_data_lim(x, data_lim=(None, None)):
  ok_flag = True
  if data_lim[0] is not None:
    if x < data_lim[0]:
      ok_flag = False
  if data_lim[1] is not None:
    if x > data_lim[1]:
      ok_flag = False
  return x if ok_flag else None

def top_data_show(df: pd.DataFrame, data_lim=(None, None)):
  global local_str
  global gen_date
  apply_data_lim = partial(func_data_lim, data_lim=data_lim)
  # data_cols=["now30_view_speed[/day]","now7_view_speed[/day]","now3_view_speed[/day]","now1_view_speed[/day]"]
  # for col in data_cols:
  #   df[col] = -1 * df[col]
  

  # x_axis = ["30days", "7days", "3days", "1day"]
  data_cols = df.columns[df.columns.str.startswith("now")].sort_values(
      key=lambda x: x.str[3:].str.split("_").str[0].astype(int), ascending=False)
  x_axis = [col.split("_")[0][3:] for col in data_cols]
  data_category = data_cols[0].split("_")[1]
  # cm_colors = plt.cm.get_cmap("Dark2").colors
  cm_colors = plt.get_cmap("tab10").colors

  plt.figure(figsize=(12, 7))
  for i, idx in enumerate(df[data_cols].index[:25]):
    plt.plot(
      x_axis,
      df.loc[idx, data_cols].apply(apply_data_lim),
      color=cm_colors[i % len(cm_colors)],
      marker=['o', '^', 's', 'D', "x", "+"][i // len(cm_colors)],
      linestyle='dashed',
      linewidth=1,
      markersize=5,
      # label=df.loc[idx, "title"].replace("&amp;", "&"),      
      label=f"{df.loc[idx, 'view']:,} {df.loc[idx, 'title'].replace('&amp;', '&')}"
    )
    # if df.loc[idx, data_cols].mean() < 1000:
    #   print(df.loc[idx, data_cols])
  plt.yscale("log")
  # plt.yscale("function", functions=(yscale_f_forward, yscale_f_backward))
  plt.gca().yaxis.set_major_formatter("{x:,.2f}")
  plt.gca().yaxis.set_minor_formatter("{x:,.2f}")
  plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
  plt.title(f"{gen_date}より○日前までの平均{data_category}速度[/day]", loc="left")
  plt.tight_layout()
    
  # plt.show()
  plt.savefig(f"./{local_str}top_now_{data_category}.png")
  plt.close()
  
def latest_data_show(df: pd.DataFrame, data_lim=(None, None)):
  global local_str
  global gen_date
  apply_data_lim = partial(func_data_lim, data_lim=data_lim)
  # data_cols=["now30_view_speed[/day]","now7_view_speed[/day]","now3_view_speed[/day]","now1_view_speed[/day]"]
  # data_cols=["day30_view_speed[/day]","day7_view_speed[/day]","day3_view_speed[/day]","day1_view_speed[/day]"]
  # data_cols=df.columns
  # for col in data_cols:
  #   df[col] = -1 * df[col]
  for daynow in ["day", "now"]:

    # x_axis = ["30days", "7days", "3days", "1day"]
    data_cols = df.columns[df.columns.str.startswith(daynow)].sort_values(
      key=lambda x: x.str[len(daynow):].str.split("_").str[0].astype(int), ascending=False)
    x_axis = [col.split("_")[0][len(daynow):] for col in data_cols]
    data_category = data_cols[0].split("_")[1]
    # cm_colors = plt.cm.get_cmap("Dark2").colors
    cm_colors = plt.get_cmap("tab10").colors

    plt.figure(figsize=(12, 7))
    for i, idx in enumerate(df[data_cols].dropna(how="all").index[:30]):
      plt.plot(
        x_axis,
        df.loc[idx, data_cols].apply(float).apply(apply_data_lim),
        color=cm_colors[i % len(cm_colors)],
        marker=['o', '^', 's', 'D', "x", "+"][i // len(cm_colors)],
        linestyle='dashed',
        linewidth=1,
        markersize=5,
        label=df.loc[idx, "date"].split()[0].replace("-", "/") + " " + \
          df.loc[idx, 'title'].replace('&amp;','&'),
      )
      # except Exception as e:
      #   print(df.loc[idx-1, data_cols].apply(type))
      #   print(df.loc[idx, data_cols].apply(type))
      #   print(e)
    plt.yscale("log")
    plt.gca().yaxis.set_major_formatter("{x:,.1f}")
    # plt.gca().yaxis.set_minor_formatter("{x:,.2f}")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), framealpha=0)
    if daynow == "day":
      plt.title(f"リリースより○日後までの平均{data_category}速度[/day]", loc="left")
    elif daynow == "now":
      plt.title(f"{gen_date}より○日前までの平均{data_category}速度[/day]", loc="left")
    plt.tight_layout()
      
    # plt.show()
    plt.savefig(f"./{local_str}latest_{daynow}_{data_category}.png")
    plt.close()
    
def main():
  global gen_date
  global local_str

  local_str = "" if os.environ.get("CI") else "local/"
  src_csv_path = f"./{local_str}summary_list.csv"
  break_row = 0
  with open(src_csv_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
      if line.startswith("id,") and idx != 0:
        break_row = idx
        break
      
  # print(break_idx)
  # sys.exit(0)

  with open(f"./{local_str}GENERATED_DATE.csv") as f:
    gen_date = f.read().split()[0]

  df = pd.read_csv(src_csv_path, nrows=break_row -1, encoding="utf-8", parse_dates=True, index_col="id", date_format="%Y-%m-%d %H:%M:%S")
  # print(df.filter(regex="title|_views_speed").tail())
  latest_data_show(df.filter(regex="title|(^date$)|_views_speed"))
  latest_data_show(df.filter(regex="title|(^date$)|_likes_speed"))
  latest_data_show(df.filter(regex="title|(^date$)|_comments_speed"), data_lim=(0.1, None))
  df = pd.read_csv(src_csv_path, skiprows=break_row, encoding="utf-8", parse_dates=True, index_col="id", date_format="%Y-%m-%d %H:%M:%S")
  # print(df.filter(regex="title|_views_speed").head())
  top_data_show(df.filter(regex="title|(^view$)|_views_speed"))
  top_data_show(df.filter(regex="title|(^view$)|_likes_speed"), data_lim=(8, None))
  top_data_show(df.filter(regex="title|(^view$)|_comments_speed"), data_lim=(0.1, None))

if __name__ == "__main__":
  main()