import pandas as pd
import sys
from matplotlib import pyplot as plt
from make_timeline import make_timeline
from datetime import datetime, timedelta

# df = pd.read_csv("./agg_df.csv", index_col="date", parse_dates=True)
df = pd.read_csv("./agg_df.csv", parse_dates=["date"], index_col="date")
df_diff = df.diff().dropna()
# df_diff.columns = [s + "_diff" for s in df_diff.columns]
sr_elapsed_time = df.index.to_series().diff().dropna().apply(lambda x: x.total_seconds())
df_diff_normed = df_diff.apply(lambda x: x / sr_elapsed_time, axis="index")
# df_diff = df_diff / df_diff.index.to_series()
# print(df_diff)
# print(df_diff_normed)

# sys.exit(0)
cut_range_dict = {
    "view_25_views": 9,
    "view_25_likes": 0.08,
    "view_25_comments": 0.019,
    "date_25_views": 35,
    "date_25_likes": 2,
    "date_25_comments": 0.2
}
for column in df_diff_normed.columns:
    # print(column, df_diff_normed[column].quantile([0.05, 0.995]).to_list())
    # continue
    df_t = df_diff_normed[column]
    max_range = cut_range_dict[column]
    plt.hist(df_t, bins=21, range=(0, max_range), log=True)
    plt.hist(df_t, bins=21, range=(max_range, max_range*2), log=True)
    plt.savefig(column + "_histo.jpg")
    plt.close()
    # sys.exit()
    sr_cut_t = df_t[(0 <= df_t) & (df_t <= max_range)]

    # plt.plot(sr_view_25_cut.index, sr_view_25_cut)
    # plt.show()

    sr_cut_10days_t = sr_cut_t[sr_cut_t.index > datetime.now() + timedelta(days=-10)]

    make_timeline(sr_cut_10days_t.index, sr_cut_10days_t, figname=column)
