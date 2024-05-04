from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys
import pandas as pd
from scipy.interpolate import make_interp_spline
# import numpy as np
import os

plt.rcParams["font.family"] = "IPAexGothic"

account = os.environ.get("ACCOUNT")
if account is None:
    account = ""
else:
    account = f"（@{account}）"


def make_fill_pairs(x_in):
    x_fill_pairs = []
    # print(x_in)

    if len(x_in) == 0:
        return x_fill_pairs

    x_datalist_seconds = (x_in[-1] - x_in[0]).total_seconds()
    # x_datalist_hours = x_datalist_days * 24 + x_in[-1].hour
    # print(x_in[-1].hour)
    x_datelist = [datetime(x_in[0].year, x_in[0].month, x_in[0].day, x_in[0].hour) +
                  timedelta(hours=1) * i for i in range(int(x_datalist_seconds) // 3600 + 2)]
    x_temp = [xd for xd in x_datelist if xd.hour == 17 or xd.hour == 23]

    if len(x_temp) == 0:
        return x_fill_pairs

    # print(x_datelist)
    if x_temp[0].hour == 23:
        x_temp.insert(0, x_in[0])
    if x_temp[-1].hour == 17:
        x_temp.append(x_in[-1])
    # print(x_temp)

    if len(x_temp) % 2 != 0:
        print("error: x_temp has odd number count!")
        sys.exit(1)

    for i in range(len(x_temp)//2):
        ii = 2*i
        x_fill_pairs.append([x_temp[ii], x_temp[ii+1]])

    return x_fill_pairs

# タイムラインチャート作成


def make_timeline(
    x, y, figname,
    tl=False,
    y0=False,
    nan_idxs=[],
    adjusted_idxs=[],
    annot_dfds=False,
    y_label="",
    interp=False,
    event_hline=None,
    ylim=None,
    xlim=None,
    data_annots=()
):

    plt.figure(figsize=(15, 8))

    # 移動平均線
    if tl:
        # y_mean10 = pd.Series(y).rolling(10).mean()
        y_mean60 = pd.Series(y).rolling(60).mean()

    plt.scatter(x, y, marker='None')

    if event_hline is not None:
        plt.title(f"公式ツイッター{account}フォロワー数＆イベント参加人数観測", y=1, pad=45)
    elif type(annot_dfds) is not bool:
        plt.title(f"公式ツイッター{account}フォロワー数観測", y=1, pad=45)
    else:
        plt.title(f"公式ツイッター{account}フォロワー数観測", )

    x_range = max(x) - min(x)
    y_range = max(y) - min(y)

    xaxis_minor_interval_presets = [1, 2, 3, 4,
                                    6, 8, 12] + [24 * i for i in range(1, 100)]
    xaxis_minor_interval = max(
        int(x_range.total_seconds()) // (40 * 60 * 60), 1)
    for i, xaxis_minor_interval_preset in enumerate(xaxis_minor_interval_presets):
        if xaxis_minor_interval < xaxis_minor_interval_preset:
            if i == 0:
                xaxis_minor_interval = xaxis_minor_interval_presets[0]
                break
            else:
                xaxis_minor_interval = xaxis_minor_interval_presets[i-1]
                break
    else:
        print("##### ERROR ##### \nxaxis minor tick value not found!")
        sys.exit(1)

    xaxis_minor_byhour = [0]
    if xaxis_minor_interval < 24:
        xaxis_minor_byhour = [xaxis_minor_interval *
                              i for i in range(24 // xaxis_minor_interval)]
    if x_range.days <= 90:
        xaxis_major_loc = mdates.RRuleLocator(mdates.rrulewrapper(
            mdates.DAILY, byhour=11, byminute=30))
        plt.gca().xaxis.set_major_locator(xaxis_major_loc)
    else:
        # every Monday
        xaxis_major_loc = mdates.RRuleLocator(mdates.rrulewrapper(
            mdates.DAILY, byweekday=0, byhour=11, byminute=30))
        plt.gca().xaxis.set_major_locator(xaxis_major_loc)

    if x_range.days <= 20:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%a'))
    elif x_range.days <= 40:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%a'))
        plt.xticks(rotation=90)
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=90)

    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=xaxis_minor_byhour))
    if not (len(xaxis_minor_byhour) == 1 and xaxis_minor_byhour[0] == 0):
        plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

    # if y_range != 0:
    #     plt.gca().yaxis.set_major_locator(
    #         ticker.MultipleLocator(max(5*(y_range//60), 1)))
    #     plt.gca().yaxis.set_minor_locator(
    #         ticker.MultipleLocator(max(y_range//60, 1) * 1))
    # plt.gca().yaxis.set_major_formatter(
    #     ticker.ScalarFormatter(useOffset=False, useMathText=False))
    # plt.gca().yaxis.get_major_formatter().set_scientific(False)

    plt.gca().tick_params(axis='x', which='major', length=14, color="white")
    x_fill_pairs = make_fill_pairs(x)

    y_label_temp = y_label if len(y_label) > 0 else "元データ"
    # print(x_fill_pairs)

    # アノテーションがないとき（一日毎の表示以外）
    if type(annot_dfds) is bool:
        plt.plot(x, y, c="grey", zorder=1, label=y_label_temp)
    if tl:
        # plt.plot(x, y_mean10, c="orange", linewidth=2,
        #          zorder=5, label="10分移動平均")
        plt.plot(x, y_mean60, c="red", linewidth=2, zorder=10, label="60分移動平均")
        if y0:
            plt.gca().fill_between(x, [max(0, ym) for ym in y_mean60], [
                0] * len(y_mean60), fc="cyan")
            plt.gca().fill_between(
                x, [0] * len(y_mean60), [min(0, ym) for ym in y_mean60], fc="pink")

    if ylim is not None:
        plt.gca().set_ylim(bottom=ylim["bottom"], top=ylim["top"])
    if xlim is not None:
        plt.gca().set_xlim(xlim["left"], xlim["right"])

    # 差分表示のときはnan部を点で表現
    if 'dif' in figname:
        if len(y_label) == 0:
            plt.gca().set_ylabel("フォロワー数増減量推移")
        plt.axhline(y=0, linestyle="dotted")
        if len(nan_idxs) > 0:
            plt.plot(
                [x[ni] for ni in nan_idxs if ni < len(x)],
                [y[ni] for ni in nan_idxs if ni < len(y)],
                marker='o', color="blue", linewidth=0, zorder=20, label="無視されるデータ点"
            )
        if len(adjusted_idxs) > 0:
            plt.plot(
                [x[ni] for ni in adjusted_idxs if ni < len(x)],
                [y[ni] for ni in adjusted_idxs if ni < len(y)],
                marker='o', color="orange", linewidth=0, zorder=20, label="平均化されるデータ点"
            )
    # 実数表示の時はnan部を2点間の線で表現
    else:
        if len(y_label) == 0:
            plt.gca().set_ylabel("フォロワー数推移")
        for i, ni in enumerate(nan_idxs):
            if i == 0:
                plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                         color="blue", zorder=20, label="その他ノイズっぽい増減")
            else:
                plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                         color="blue", zorder=20)
        for i, ni in enumerate(adjusted_idxs):
            if i == 0:
                plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                         color="orange", zorder=20, label="振動ノイズっぽい増減")
            else:
                plt.plot([x[ni-1], x[ni]], [y[ni-1], y[ni]],
                         color="orange", zorder=20)

    if len(y_label) > 0:
        plt.gca().set_ylabel(y_label)

    # この処理時点でのy軸描画範囲 {最小値、最大値}
    ylim = plt.gca().get_ylim()

    # アノテーションがあるとき（一日毎の表示限定）
    if type(annot_dfds) is pd.core.series.Series or type(annot_dfds) is pd.core.frame.DataFrame:
        plt.plot(x, y, marker='o', markerfacecolor='black', markeredgewidth=0,
                 markersize=4, linewidth=0, label=y_label_temp)

        if interp and len(x) >= 4 and x_range != 0:
            X_Y_Spline = make_interp_spline(
                list(map(lambda ix: ix.timestamp(), x)), y)
            X_ = [min(x) + i * 0.001 * x_range for i in range(1001)]
            X_ = list(map(lambda ix: ix.timestamp(), X_))
            Y_ = X_Y_Spline(X_)
            # print(x[:5])
            # print(list(map(datetime.utcfromtimestamp, X_))[:5])
            # sys.exit(9)
            plt.plot(list(map(datetime.utcfromtimestamp, X_)),
                     Y_, c="grey", zorder=1, label="補完曲線")
        else:
            plt.plot(x, y, c="grey", zorder=1)
        # plt.show()
        # sys.exit()
        cm_colors = plt.cm.get_cmap("Dark2").colors
        for i, al in enumerate(annot_dfds.index):
            x_text = i / len(annot_dfds.index)
            ci = i % len(cm_colors)
            plt.gca().annotate(i+1, xy=(al, ylim[1]), size=15, xytext=(
                x_text, 1.05), textcoords='axes fraction',
                bbox={
                    "boxstyle": "circle",
                    "fc": "white",
                    "ec": cm_colors[ci]
            },
                arrowprops={
                    "arrowstyle": "wedge",
                    "color": cm_colors[ci]
            })
            plt.axvline(x=al, ymin=0, ymax=1,
                        linestyle="dotted", color=cm_colors[ci])

    label_flgs = [True, True]
    for x_fill_pair in x_fill_pairs:
        fc = ""
        label = None
        if x_fill_pair[0].weekday() == 5 or x_fill_pair[0].weekday() == 6:
            fc = "#FCCBE2"
            if label_flgs[1]:
                label = "土日 17時-23時"
                label_flgs[1] = False
        else:
            fc = "#BCECE0"
            if label_flgs[0]:
                label = "平日 17時-23時"
                label_flgs[0] = False

        plt.gca().fill_between(x_fill_pair, *ylim, fc=fc, zorder=0, label=label)

    # data annotation
    if len(data_annots) > 0:
        for data_annot in data_annots:
            # print(data_annot)
            if len(data_annot) == 3:
                va = "top" if data_annot[2] == "min" else "bottom"
                # remove trailing zero and dot from annotation string
                plt.annotate(f"{data_annot[1]:5,.3f}".rstrip("0").rstrip("."), xy=data_annot[:2],
                             horizontalalignment="center", verticalalignment=va, zorder=2)
            # plt.show()

    if event_hline is None:
        plt.legend().set(zorder=21)

    # イベント開催期間追記用
    else:
        plt.legend(loc="lower right", bbox_to_anchor=(1, 1))
        ax2 = plt.gca().twinx()
        event_hline = event_hline[(event_hline["start_date"] <= max(x)) & (
            min(x) <= event_hline["end_date"])]
        start_cond = event_hline["start_date"] <= min(x)
        end_cond = event_hline["end_date"] >= max(x)
        event_hline.loc[start_cond, "start_date"] = event_hline["start_date"][start_cond].apply(
            lambda xx: max(min(x), xx))
        event_hline.loc[end_cond, "end_date"] = event_hline["end_date"][end_cond].apply(
            lambda xx: min(max(x), xx))
        ax2.hlines(event_hline["participants"], xmin=event_hline["start_date"],
                   xmax=event_hline["end_date"], colors=event_hline["color"], linewidth=7, alpha=0.8)
        # for ei in event_hline.index:
        #     eh = event_hline.loc[ei]
        #     ax2.axhline(eh["participants"], xmin=eh["start_date"],
        #                 xmax=eh["end_date"], color=eh["color"], label=eh["unit"])

        ax2.yaxis.set_major_formatter(
            ticker.ScalarFormatter(useOffset=False, useMathText=False))
        ax2.yaxis.get_major_formatter().set_scientific(False)
        ax2.set_ylabel("イベント参加人数")

        eh_set_for_legend = event_hline.drop_duplicates(subset="unit")
        proxy_artists = [Line2D([0, 1], [0, 1], color=eh_set_for_legend.loc[ei, "color"])
                         for ei in eh_set_for_legend.index]
        unit_names = {
            "vs": "バチャシン",
            "l/n": "レオニ",
            "mmj": "モモジャン",
            "vbs": "ビビバス",
            "wxs": "ワンダショ",
            "n25": "ニーゴ",
            "mix": "混合"
        }
        proxy_labels = eh_set_for_legend["unit"].map(unit_names)

        plt.legend(proxy_artists, proxy_labels, loc="lower left", ncol=10, bbox_to_anchor=(
            0, 1), edgecolor="white")

    # ローカル実行ならグラフ表示、Actions実行ならグラフ保存
    if len(sys.argv) > 1:
        if len(sys.argv) == 2 and sys.argv[1] == "local":
            plt.show()
            return

    plt.savefig(f'./{figname}.png')
    print(f'./{figname}.png is saved!')
    plt.close()


def make_multi_timeline(
    dfs, figname,
    y_label=None,
    y_labels=None,
    ylim=None
):

    plt.figure(figsize=(15, 8))
    plt.title(f"公式ツイッター{account}フォロワー数観測")

    for df in dfs:
        plt.scatter(df.index, df.iloc[:, 0], marker='None')

    xyx = [min([min(df.index.to_list()) for df in dfs]),
           max([max(df.index.to_list()) for df in dfs])]
    xyy = [min([min(df.iloc[:, 0].to_list()) for df in dfs]),
           max([max(df.iloc[:, 0].to_list()) for df in dfs])]
    x_range = xyx[1] - xyx[0]
    y_range = xyy[1] - xyy[0]

    xaxis_minor_interval_presets = [1, 2, 3, 4,
                                    6, 8, 12] + [24 * i for i in range(1, 100)]
    xaxis_minor_interval = max(
        int(x_range.total_seconds()) // (40 * 60 * 60), 1)
    for i, xaxis_minor_interval_preset in enumerate(xaxis_minor_interval_presets):
        if xaxis_minor_interval < xaxis_minor_interval_preset:
            if i == 0:
                xaxis_minor_interval = xaxis_minor_interval_presets[0]
                break
            else:
                xaxis_minor_interval = xaxis_minor_interval_presets[i-1]
                break

    xaxis_minor_byhour = [0]
    if xaxis_minor_interval < 24:
        xaxis_minor_byhour = [xaxis_minor_interval *
                              i for i in range(24 // xaxis_minor_interval)]
    if x_range.days <= 90:
        xaxis_major_loc = mdates.RRuleLocator(mdates.rrulewrapper(
            mdates.DAILY, byhour=11, byminute=30))
        plt.gca().xaxis.set_major_locator(xaxis_major_loc)
    else:
        # every Monday
        xaxis_major_loc = mdates.RRuleLocator(mdates.rrulewrapper(
            mdates.DAILY, byweekday=0, byhour=11, byminute=30))
        plt.gca().xaxis.set_major_locator(xaxis_major_loc)

    if x_range.days <= 20:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%a'))
    elif x_range.days <= 40:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%a'))
        plt.xticks(rotation=90)
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=90)

    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=xaxis_minor_byhour))
    if not (len(xaxis_minor_byhour) == 1 and xaxis_minor_byhour[0] == 0):
        plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H'))

    if y_range != 0:
        plt.gca().yaxis.set_major_locator(
            ticker.MultipleLocator(max(5*(y_range//60), 1)))
        plt.gca().yaxis.set_minor_locator(
            ticker.MultipleLocator(max(y_range//60, 1) * 1))
    plt.gca().yaxis.set_major_formatter(
        ticker.ScalarFormatter(useOffset=False, useMathText=False))
    plt.gca().yaxis.get_major_formatter().set_scientific(False)

    plt.gca().tick_params(axis='x', which='major', length=14, color="white")

    x_fill_pairs = make_fill_pairs(xyx)
    if ylim is not None:
        plt.gca().set_ylim(bottom=ylim["bottom"], top=ylim["top"])

    if y_label:
        plt.gca().set_ylabel(y_label)
    else:
        plt.gca().set_ylabel("フォロワー数増減量推移")

    # この処理時点でのy軸描画範囲 {最小値、最大値}
    ylim = plt.gca().get_ylim()

    if not y_labels:
        y_labels = ["データ" + str(i) for i in range(len(dfs))]

    cm_colors = plt.cm.get_cmap("Dark2").colors
    for i, df in enumerate(dfs):
        ci = i % len(cm_colors)
        plt.plot(df.index, df.iloc[:, 0],
                 c=cm_colors[ci], zorder=1, label=y_labels[i])

    label_flgs = [True, True]
    for x_fill_pair in x_fill_pairs:
        fc = ""
        label = None
        if x_fill_pair[0].weekday() == 5 or x_fill_pair[0].weekday() == 6:
            fc = "#FCCBE2"
            if label_flgs[1]:
                label = "土日 17時-23時"
                label_flgs[1] = False
        else:
            fc = "#BCECE0"
            if label_flgs[0]:
                label = "平日 17時-23時"
                label_flgs[0] = False

        plt.gca().fill_between(x_fill_pair, *ylim, fc=fc, zorder=0, label=label)
    plt.axhline(y=0, linestyle="dotted")

    plt.legend()

    # ローカル実行ならグラフ表示、Actions実行ならグラフ保存
    if len(sys.argv) > 1:
        if len(sys.argv) == 2 and sys.argv[1] == "local":
            plt.show()
            return

    plt.savefig(f'./{figname}.png')
    print(f'./{figname}.png is saved!')
    plt.close()
