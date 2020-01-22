from os import path
import numpy as np
import matplotlib.pyplot as plt
import re


def process_filters(df, filters):
    for f in filters:
        df = process_filter(df, f)
    return df


def process_filter(df, filter_dict):
    dim = filter_dict["dim"]
    op = filter_dict["op"]
    val = filter_dict["val"]

    case = {
        "eq": lambda x: x[x[dim] == val],
        "<=": lambda x: x[x[dim] <= val],
        "==": lambda x: x[x[dim] == val],
        "re": lambda x: x[x[dim].apply(lambda y: bool(re.search(val.lower(), str(y).lower())))],
        "isin": lambda x: x[df[dim].isin(val)]
    }
    return case[op](df)


def process_day_df_columns(df):
    weekday_map = {0: "Monday",
                   1: "Tuesday",
                   2: "Wednesday",
                   3: "Thursday",
                   4: "Friday",
                   5: "Saturday",
                   6: "Sunday"}
    weekend = ["Sunday", "Saturday"]
    df['day_of_week'] = df['date'].apply(lambda x:
                                         weekday_map[x.weekday()]
                                         if x.weekday() in weekday_map
                                         else "Unknown")
    df['month'] = df['date'].apply(lambda x: str(x.month))
    df["is_weekday"] = df["day_of_week"].apply(lambda x: not (x in weekend))
    return df


class Analytics:

    @staticmethod
    def filter_desc(self, filters):
        if type(filters) == dict:
            filters = [filters]
        filter_descs = []
        for f in filters:
            filter_val = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,*]", " ", str(f["val"]))
            filter_descs.append("{0} {1} {2}".format(f["dim"], f["op"], filter_val))
        return " AND ".join(filter_descs)

        print(f)

    def metrics_barchart(self, df, metric, groupby_dim, title=None, filters=None, save_dir=None, show=False, order=[]):
        data = metric.get_data(df, groupby_dim=groupby_dim, filters=filters)
        if order:
            mapping = {day: i for i, day in enumerate(order)}
            key = data['x'].map(mapping)
            data = data.iloc[key.argsort()]

        metric_name = metric.metric_name

        index = np.arange(len(set(data["x"])))
        plt.bar(index, data["y"],
                tick_label=data["x"]
                )
        plt.ylabel(metric_name)
        plt.xlabel(groupby_dim)
        if not title:
            title = metric_name + " grouped by " + groupby_dim
            if filters:
                title = title + " [" + self.filter_desc(filters) + "]"
            plt.title(title)
        if save_dir:
            plt.savefig(path.join(save_dir, title + ".svg"),
                        format='svg',
                        orientation='landscape',
                        papertype='letter')
        if show:
            plt.show()
        plt.close()

    def distribution_plot(self, df, dist, filters=None, save_dir=None, show=False):
        figsize = (15, 5)
        print("here001")
        title = "{0} ({1})".format(dist.metric_name, dist.x_units)
        if filters:
            title = title + " [" + self.filter_desc(filters) + "]"

        args = {"x_unit": dist.x_units}

        bins = np.arange(0, 100, 25)
        interval = 1
        print("here002")
        data = dist.get_data(df, filters=filters, args=args)
        print("here003")
        if dist.x_units == "days":
            bins = np.arange(0, 30, 1)
            data = np.clip(data['y'], bins[0], bins[-1])
        elif dist.x_units == "weeks":
            bins = np.arange(0, 50, 1)
            data = np.clip(data['y'], bins[0], bins[-1])
        elif dist.x_units in ["4hours", "hours"]:
            interval = 4
            bins = np.arange(0, 5 * 24, interval)
            data = np.clip(data['y'], bins[0], bins[-1])
        elif dist.x_units == "1hours":
            interval = 1
            bins = np.arange(0, 48, interval)
            data = np.clip(data['y'], bins[0], bins[-1])
        elif dist.x_units == "halfhours":
            interval = 0.5
            bins = np.arange(0, 24, interval)
            data = np.clip(data['y'], bins[0], bins[-1])
            figsize = (20, 5)
        else:
            interval = 1
            print(min(data["y"]), max(data['y']))
            bins = np.arange(0, 20, interval)
            data = data["y"]
            # data = np.clip(data['y'], bins[0], bins[-1])
        print("here004")
        fig, ax = plt.subplots(figsize=figsize)
        _, bins, patches = plt.hist(data, bins=bins, rwidth=0.96)
        print("here005")
        print(bins)
        xlabels = bins[1:].astype(str)
        print(xlabels)
        xlabels[-1] += '+'
        N_labels = len(xlabels)
        plt.xlim([bins[0], bins[-1]])
        plt.xticks(interval * np.arange(N_labels) + interval / 2)
        ax.set_xticklabels(xlabels)

        plt.title(title)
        plt.ylabel(dist.y_label)
        plt.xlabel(dist.x_label)

        if save_dir:
            print(save_dir, title)
            plt.savefig(path.join(save_dir, title + ".svg"),
                        format='svg',
                        orientation='landscape',
                        papertype='letter')
        if show:
            plt.show()
        return

    def time_distribution_plt(self, data, x_units, save_dir=None, show=False, title=None, x_label=None, y_label=None):
        fig_size = (15, 5)
        title = title if title else "Some Time Binned Distribution"
        x_label = x_label if x_label else x_units
        y_label = y_label if y_label else "Frequency"

        secs2hrs = 60 * 60
        secs2days = secs2hrs * 24

        if x_units in ["days"]:
            y_data = data.dt.days + data.dt.seconds / secs2days
        elif x_units in ["weeks"]:
            y_data = data.dt.days / 7
        elif x_units in ["1hours", "4hours", "halfhours"]:
            y_data = data.dt.days * 24 + data.dt.seconds / secs2hrs

        interval = 1
        bins = np.arange(0, 100, 25)
        if x_units == "days":
            bins = np.arange(0, 30, interval)
        elif x_units == "weeks":
            bins = np.arange(0, 50, interval)
        elif x_units == "4hours":
            interval = 4
            bins = np.arange(0, 5 * 24, interval)
        elif x_units == "1hours":
            bins = np.arange(0, 48, interval)
        elif x_units == "halfhours":
            interval = 0.5
            bins = np.arange(0, 24, interval)
            fig_size = (20, 5)
        else:
            bins = np.arange(0, max(data, interval))

        y_data = np.clip(y_data, bins[0], bins[-1])

        fig, ax = plt.subplots(figsize=fig_size)
        _, bins, patches = plt.hist(y_data, bins=bins, rwidth=0.96)
        plt.xlim([bins[0], bins[-1]])

        xtic_labels = bins[1:].astype(str)
        xtic_labels[-1] += '+'
        plt.xticks(interval * np.arange(len(xtic_labels)) + interval / 2)
        ax.set_xticklabels(xtic_labels)

        plt.title(title)
        plt.ylabel(y_label)
        plt.xlabel(x_label)

        if save_dir:
            plt.savefig(path.join(save_dir, title + ".svg"),
                        format='svg',
                        orientation='landscape',
                        papertype='letter')
        if show:
            plt.show()
        plt.close()
        return

    def discrete_distribution_plt(self, data, overflow=None, save_dir=None, show=False, title=None, x_label=None,
                                  y_label=None):
        fig_size = (15, 6)
        bins = range(0, 2 + int(max(data)))
        if overflow:
            overflow = overflow if max(data) > overflow else False
        if overflow:
            bins = range(0, overflow + 1)
            data = np.clip(data, 0, overflow)

        fig, ax = plt.subplots(figsize=fig_size)
        _, bins, patches = plt.hist(data,
                                    bins=bins,
                                    rwidth=0.98,
                                    alpha=0.5,
                                    )
        xlabels = [str(x) for x in bins[0:-1]]
        if overflow:
            xlabels[-1] += "+"
        plt.xlim([bins[0], bins[-1]])
        plt.xticks(np.arange(len(xlabels)) + 1 / 2, xlabels)
        plt.title(title if title else "Discrete Distribution Plot")
        plt.xlabel(x_label if x_label else "bins")
        plt.ylabel(y_label if y_label else "Frequency")
        if save_dir:
            plt.savefig(path.join(save_dir, title + ".svg"),
                        format='svg',
                        orientation='landscape',
                        papertype='letter')
        if show:
            plt.show()
        plt.close()
        return
