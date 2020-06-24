import pandas as pd
import seaborn as sns
import plotly.express as px
import io
import matplotlib.pyplot as plt
import datetime
from matplotlib.figure import Figure
import base64
import json


class DataVisualization:

    def __init__(self):
        # the dictionary hosting all the data frames from the api server
        self.matrix = dict()

    def add_data_for_visualization(self, source):
        # Execute the source function and transform its return into a dataframe
        response = source()
        dataframe = pd.DataFrame(json.loads(response.get_data().decode("utf-8")))
        # save the dataframe into general matrix that stores every dataframe
        self.matrix[source] = dataframe
        return source

    # This method should plot the data obtained under "daily" route
    def daily_data_plot(self, source):
        df = self.matrix[source].drop('date', axis=1)
        df.index.name = 'date'
        # drop unnecessary poi column
        if 'poi_id' in df.columns:
            df = df.drop('poi_id', 1)
        # Construct the plot
        fig = Figure()
        axe = fig.subplots(1, len(df.columns),
                           squeeze=False)
        y = 0
        # Use looping to plot all the graphs
        for column in df.columns:
            df[column].plot(ax=axe[0, y], figsize=(12, 6))
            axe[0, y].set_title(column)
            y += 1
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        def wraper():
          return f"<img src='data:image/png;base64,{data}' width='1100'/>"

        wraper.__name__ = source.__name__
        return wraper


    def hour_data_plot(self, source):  # This method serves to plot all the hour-based data, and plot them in heatmap
        # get the dataframe from self.matrix
        df = self.matrix[source]
        # drop unnecessary poi column
        if 'poi_id' in df.columns:
            df = df.drop('poi_id', 1)
        # preserve the order of  date as the pivotal table in Pandas automatically sort the input
        index_list = [i for i in df.date.unique()]
        # set the index of data frame as 'date' column
        df = df.set_index('date')
        # generate the column list which will be used to generate dataframe for all the dimension
        columns = [i for i in df.columns if i != 'hour']
        # construct a hash table to store different dataframe for every dimension
        dataframe_dict = dict()
        # using pivotal table to convert the dataframe into what i need to plot heatmap
        for column in columns:
            dataframe_dict[column] = pd.pivot_table(df[['hour', column]],
                                                    index=['date'],
                                                    columns=['hour'])
            # re set the index based on the original order that has been preserved
            dataframe_dict[column] = dataframe_dict[column].reindex(index_list)
            dataframe_dict[column].columns = dataframe_dict[column].columns.droplevel()
        # set up the subplot object for accommodating heatmaps

        x = 0
        fig, axe = plt.subplots(len(columns), 1,
                                squeeze=False,
                                constrained_layout=True,
                               figsize=(10, 6.5))
        # fig.tight_layout()
        # using loop to plot all the heatmaps
        for column in columns:
            sns.heatmap(dataframe_dict[column], ax=axe[x, 0])
            axe[x, 0].set_title(column)
            x += 1
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        def wraper():
            return f"<img src='data:image/png;base64,{data}' width='1100'/>"

        wraper.__name__ = source.__name__
        return wraper


# The class for geographic data visualization which inherits DataVisualization class
class GeoVisualization(DataVisualization):

    # Define the function to implement plot
    def geo_plot(self, source_poi, intersted_data):
        df_poi = self.matrix[source_poi]
        df_interested_data = self.matrix[intersted_data]
        # Joining the POI data with the data of interest
        df = df_interested_data.merge(df_poi, on='poi_id')
        print(df)
        # If there is no geo data in the data set, raises error
        if "lat" not in df.columns or "lon" not in df.columns:
            raise Exception('There are no geographic data available in the data')
        hover_data = {"poi_id": False, "lat": False, "lon": False}
        hover_data.update(dict((c, True) for c in df.columns if c != "poi_id" and c != "lat" and c != "lon"))
        # Construct an instance of figure
        fig = px.scatter_mapbox(df,
                                lat="lat",
                                lon="lon",
                                size=[10 for _ in range(len(df.index))],
                                hover_name="name",
                                hover_data=hover_data,
                                color_discrete_sequence=["fuchsia"],
                                zoom=3,
                                height=300,
                                animation_frame="date",
                                animation_group="poi_id",)
        fig.update_layout(mapbox_style="open-street-map",height=600)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        #fig.write_html(r"C:\Users\Xiaokeai\Desktop\POI.html")
        div = opy.plot(fig, auto_open=False, output_type='div')
        return div


# Demonstrate the UI components
if __name__ == '__main__':
    # the data sets from api
    stats_hourly = [
  {
    "clicks": 23,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 0,
    "impressions": 10746,
    "poi_id": 3,
    "revenue": 64.9215630000000
  },
  {
    "clicks": 201,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 1,
    "impressions": 141397,
    "poi_id": 4,
    "revenue": 696.4485960000000
  },
  {
    "clicks": 217,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 2,
    "impressions": 137464,
    "poi_id": 1,
    "revenue": 732.0955030000000
  },
  {
    "clicks": 139,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 3,
    "impressions": 109217,
    "poi_id": 2,
    "revenue": 496.6397510000000
  },
  {
    "clicks": 74,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 4,
    "impressions": 112129,
    "poi_id": 4,
    "revenue": 446.7138830000000
  },
  {
    "clicks": 76,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 5,
    "impressions": 105182,
    "poi_id": 3,
    "revenue": 435.9536840000000
  },
  {
    "clicks": 152,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 6,
    "impressions": 111925,
    "poi_id": 2,
    "revenue": 519.1064970000000
  },
  {
    "clicks": 129,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 7,
    "impressions": 106769,
    "poi_id": 4,
    "revenue": 483.0718670000000
  },
  {
    "clicks": 135,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 8,
    "impressions": 123464,
    "poi_id": 4,
    "revenue": 561.3373030000000
  },
  {
    "clicks": 163,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 9,
    "impressions": 145333,
    "poi_id": 4,
    "revenue": 637.8506700000000
  },
  {
    "clicks": 180,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 10,
    "impressions": 152529,
    "poi_id": 4,
    "revenue": 657.6138580000000
  },
  {
    "clicks": 200,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 11,
    "impressions": 165321,
    "poi_id": 1,
    "revenue": 647.5332910000000
  },
  {
    "clicks": 195,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 12,
    "impressions": 152531,
    "poi_id": 2,
    "revenue": 684.3440180000000
  },
  {
    "clicks": 181,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 13,
    "impressions": 143520,
    "poi_id": 2,
    "revenue": 646.0625610000000
  },
  {
    "clicks": 314,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 14,
    "impressions": 168021,
    "poi_id": 3,
    "revenue": 886.5780050000000
  },
  {
    "clicks": 193,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 15,
    "impressions": 127771,
    "poi_id": 1,
    "revenue": 599.0013210000000
  },
  {
    "clicks": 211,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 16,
    "impressions": 106157,
    "poi_id": 3,
    "revenue": 603.1255660000000
  },
  {
    "clicks": 191,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 17,
    "impressions": 104870,
    "poi_id": 1,
    "revenue": 563.1118780000000
  },
  {
    "clicks": 173,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 18,
    "impressions": 86798,
    "poi_id": 4,
    "revenue": 488.8465350000000
  },
  {
    "clicks": 210,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 19,
    "impressions": 165917,
    "poi_id": 2,
    "revenue": 853.6791170000000
  },
  {
    "clicks": 99,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 20,
    "impressions": 95662,
    "poi_id": 3,
    "revenue": 452.6468010000000
  },
  {
    "clicks": 61,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 21,
    "impressions": 60086,
    "poi_id": 1,
    "revenue": 280.0887910000000
  },
  {
    "clicks": 86,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 22,
    "impressions": 113981,
    "poi_id": 3,
    "revenue": 561.3447040000000
  },
  {
    "clicks": 24,
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "hour": 23,
    "impressions": 17819,
    "poi_id": 3,
    "revenue": 94.0077160000000
  },
  {
    "clicks": 56,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 0,
    "impressions": 13316,
    "poi_id": 1,
    "revenue": 69.9917250000000
  },
  {
    "clicks": 69,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 1,
    "impressions": 32275,
    "poi_id": 4,
    "revenue": 115.2967230000000
  },
  {
    "clicks": 33,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 2,
    "impressions": 25567,
    "poi_id": 2,
    "revenue": 71.9015000000000
  },
  {
    "clicks": 12,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 3,
    "impressions": 24386,
    "poi_id": 2,
    "revenue": 43.9822160000000
  },
  {
    "clicks": 6,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 4,
    "impressions": 22305,
    "poi_id": 3,
    "revenue": 48.8441270000000
  },
  {
    "clicks": 12,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 5,
    "impressions": 23725,
    "poi_id": 4,
    "revenue": 63.5116560000000
  },
  {
    "clicks": 56,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 6,
    "impressions": 42763,
    "poi_id": 2,
    "revenue": 223.0633420000000
  },
  {
    "clicks": 56,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 7,
    "impressions": 40521,
    "poi_id": 1,
    "revenue": 220.4801670000000
  },
  {
    "clicks": 57,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 8,
    "impressions": 44862,
    "poi_id": 3,
    "revenue": 241.3888750000000
  },
  {
    "clicks": 94,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 9,
    "impressions": 49395,
    "poi_id": 3,
    "revenue": 249.6256080000000
  },
  {
    "clicks": 69,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 10,
    "impressions": 45008,
    "poi_id": 2,
    "revenue": 245.4707360000000
  },
  {
    "clicks": 87,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 11,
    "impressions": 48927,
    "poi_id": 3,
    "revenue": 242.2166710000000
  },
  {
    "clicks": 90,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 12,
    "impressions": 48836,
    "poi_id": 1,
    "revenue": 231.3379990000000
  },
  {
    "clicks": 71,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 13,
    "impressions": 48813,
    "poi_id": 4,
    "revenue": 225.6352260000000
  },
  {
    "clicks": 85,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 14,
    "impressions": 48375,
    "poi_id": 3,
    "revenue": 229.2786800000000
  },
  {
    "clicks": 57,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 15,
    "impressions": 49551,
    "poi_id": 1,
    "revenue": 223.7558460000000
  },
  {
    "clicks": 79,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 16,
    "impressions": 48362,
    "poi_id": 4,
    "revenue": 218.2177440000000
  },
  {
    "clicks": 94,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 17,
    "impressions": 47735,
    "poi_id": 2,
    "revenue": 217.3931840000000
  },
  {
    "clicks": 76,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 18,
    "impressions": 46311,
    "poi_id": 1,
    "revenue": 210.8744190000000
  },
  {
    "clicks": 67,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 19,
    "impressions": 45117,
    "poi_id": 1,
    "revenue": 209.2310100000000
  },
  {
    "clicks": 66,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 20,
    "impressions": 44123,
    "poi_id": 4,
    "revenue": 202.8335090000000
  },
  {
    "clicks": 78,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 21,
    "impressions": 43651,
    "poi_id": 3,
    "revenue": 201.6316030000000
  },
  {
    "clicks": 71,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 22,
    "impressions": 38390,
    "poi_id": 1,
    "revenue": 168.7712120000000
  },
  {
    "clicks": 48,
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "hour": 23,
    "impressions": 20756,
    "poi_id": 2,
    "revenue": 100.6141860000000
  },
  {
    "clicks": 67,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 0,
    "impressions": 18307,
    "poi_id": 4,
    "revenue": 87.4227050000000
  },
  {
    "clicks": 59,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 1,
    "impressions": 30113,
    "poi_id": 4,
    "revenue": 110.7214860000000
  },
  {
    "clicks": 29,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 2,
    "impressions": 27469,
    "poi_id": 4,
    "revenue": 73.0471470000000
  },
  {
    "clicks": 6,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 3,
    "impressions": 17418,
    "poi_id": 2,
    "revenue": 32.9492880000000
  },
  {
    "clicks": 15,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 4,
    "impressions": 21419,
    "poi_id": 4,
    "revenue": 43.1942410000000
  },
  {
    "clicks": 23,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 5,
    "impressions": 20871,
    "poi_id": 2,
    "revenue": 54.7799660000000
  },
  {
    "clicks": 72,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 6,
    "impressions": 41661,
    "poi_id": 1,
    "revenue": 215.0006050000000
  },
  {
    "clicks": 62,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 7,
    "impressions": 46586,
    "poi_id": 1,
    "revenue": 229.3272530000000
  },
  {
    "clicks": 84,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 8,
    "impressions": 49793,
    "poi_id": 1,
    "revenue": 248.0798430000000
  },
  {
    "clicks": 55,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 9,
    "impressions": 45010,
    "poi_id": 2,
    "revenue": 223.4354770000000
  },
  {
    "clicks": 79,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 10,
    "impressions": 56260,
    "poi_id": 2,
    "revenue": 264.6692640000000
  },
  {
    "clicks": 74,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 11,
    "impressions": 56859,
    "poi_id": 3,
    "revenue": 284.8601950000000
  },
  {
    "clicks": 73,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 12,
    "impressions": 53547,
    "poi_id": 1,
    "revenue": 254.4689300000000
  },
  {
    "clicks": 60,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 13,
    "impressions": 52312,
    "poi_id": 4,
    "revenue": 245.0337340000000
  },
  {
    "clicks": 56,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 14,
    "impressions": 50947,
    "poi_id": 4,
    "revenue": 238.0440430000000
  },
  {
    "clicks": 59,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 15,
    "impressions": 48849,
    "poi_id": 4,
    "revenue": 221.1546890000000
  },
  {
    "clicks": 64,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 16,
    "impressions": 46647,
    "poi_id": 2,
    "revenue": 215.6478030000000
  },
  {
    "clicks": 50,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 17,
    "impressions": 47437,
    "poi_id": 1,
    "revenue": 217.6272090000000
  },
  {
    "clicks": 50,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 18,
    "impressions": 45867,
    "poi_id": 3,
    "revenue": 210.7244290000000
  },
  {
    "clicks": 66,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 19,
    "impressions": 42472,
    "poi_id": 3,
    "revenue": 205.9077960000000
  },
  {
    "clicks": 58,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 20,
    "impressions": 43274,
    "poi_id": 1,
    "revenue": 205.6855580000000
  },
  {
    "clicks": 58,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 21,
    "impressions": 42913,
    "poi_id": 1,
    "revenue": 205.8066010000000
  },
  {
    "clicks": 34,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 22,
    "impressions": 37201,
    "poi_id": 3,
    "revenue": 168.9752980000000
  },
  {
    "clicks": 21,
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "hour": 23,
    "impressions": 18988,
    "poi_id": 4,
    "revenue": 93.3980400000000
  },
  {
    "clicks": 51,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 0,
    "impressions": 19744,
    "poi_id": 3,
    "revenue": 96.7490290000000
  },
  {
    "clicks": 52,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 1,
    "impressions": 31576,
    "poi_id": 4,
    "revenue": 127.0472440000000
  },
  {
    "clicks": 31,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 2,
    "impressions": 24471,
    "poi_id": 4,
    "revenue": 72.9980320000000
  },
  {
    "clicks": 6,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 3,
    "impressions": 15103,
    "poi_id": 2,
    "revenue": 32.2022460000000
  },
  {
    "clicks": 8,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 4,
    "impressions": 20216,
    "poi_id": 3,
    "revenue": 45.5858750000000
  },
  {
    "clicks": 9,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 5,
    "impressions": 19679,
    "poi_id": 1,
    "revenue": 56.8603970000000
  },
  {
    "clicks": 65,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 6,
    "impressions": 45383,
    "poi_id": 4,
    "revenue": 243.3083480000000
  },
  {
    "clicks": 55,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 7,
    "impressions": 47779,
    "poi_id": 2,
    "revenue": 238.6230680000000
  },
  {
    "clicks": 64,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 8,
    "impressions": 52703,
    "poi_id": 1,
    "revenue": 261.5696250000000
  },
  {
    "clicks": 63,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 9,
    "impressions": 52978,
    "poi_id": 3,
    "revenue": 257.3575390000000
  },
  {
    "clicks": 66,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 10,
    "impressions": 50976,
    "poi_id": 4,
    "revenue": 248.2284500000000
  },
  {
    "clicks": 68,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 11,
    "impressions": 50652,
    "poi_id": 1,
    "revenue": 245.2707750000000
  },
  {
    "clicks": 66,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 12,
    "impressions": 50382,
    "poi_id": 1,
    "revenue": 238.7660000000000
  },
  {
    "clicks": 78,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 13,
    "impressions": 49857,
    "poi_id": 4,
    "revenue": 234.4847420000000
  },
  {
    "clicks": 74,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 14,
    "impressions": 48773,
    "poi_id": 1,
    "revenue": 227.8905720000000
  },
  {
    "clicks": 71,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 15,
    "impressions": 44999,
    "poi_id": 1,
    "revenue": 215.9949090000000
  },
  {
    "clicks": 58,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 16,
    "impressions": 47213,
    "poi_id": 2,
    "revenue": 222.4189280000000
  },
  {
    "clicks": 57,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 17,
    "impressions": 45531,
    "poi_id": 2,
    "revenue": 214.7642890000000
  },
  {
    "clicks": 64,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 18,
    "impressions": 44255,
    "poi_id": 4,
    "revenue": 208.0608440000000
  },
  {
    "clicks": 64,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 19,
    "impressions": 42494,
    "poi_id": 3,
    "revenue": 206.2058220000000
  },
  {
    "clicks": 72,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 20,
    "impressions": 43345,
    "poi_id": 1,
    "revenue": 205.2605540000000
  },
  {
    "clicks": 71,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 21,
    "impressions": 43552,
    "poi_id": 3,
    "revenue": 201.9234330000000
  },
  {
    "clicks": 59,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 22,
    "impressions": 37205,
    "poi_id": 3,
    "revenue": 166.0467280000000
  },
  {
    "clicks": 39,
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "hour": 23,
    "impressions": 19708,
    "poi_id": 3,
    "revenue": 96.7321010000000
  },
  {
    "clicks": 62,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 0,
    "impressions": 20163,
    "poi_id": 4,
    "revenue": 98.1922020000000
  },
  {
    "clicks": 42,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 1,
    "impressions": 29395,
    "poi_id": 1,
    "revenue": 124.0678140000000
  },
  {
    "clicks": 24,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 2,
    "impressions": 22507,
    "poi_id": 1,
    "revenue": 72.2681070000000
  },
  {
    "clicks": 13,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 3,
    "impressions": 14545,
    "poi_id": 4,
    "revenue": 35.6927280000000
  },
  {
    "clicks": 5,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 4,
    "impressions": 14889,
    "poi_id": 2,
    "revenue": 36.9674330000000
  },
  {
    "clicks": 15,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 5,
    "impressions": 19443,
    "poi_id": 4,
    "revenue": 62.0260700000000
  },
  {
    "clicks": 67,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 6,
    "impressions": 43959,
    "poi_id": 3,
    "revenue": 238.7670680000000
  },
  {
    "clicks": 54,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 7,
    "impressions": 47634,
    "poi_id": 1,
    "revenue": 239.2143510000000
  },
  {
    "clicks": 69,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 8,
    "impressions": 52186,
    "poi_id": 3,
    "revenue": 263.4281800000000
  },
  {
    "clicks": 63,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 9,
    "impressions": 52899,
    "poi_id": 3,
    "revenue": 261.4129600000000
  },
  {
    "clicks": 67,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 10,
    "impressions": 53064,
    "poi_id": 2,
    "revenue": 262.6935900000000
  },
  {
    "clicks": 65,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 11,
    "impressions": 49619,
    "poi_id": 1,
    "revenue": 246.4739270000000
  },
  {
    "clicks": 76,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 12,
    "impressions": 51928,
    "poi_id": 4,
    "revenue": 250.4194500000000
  },
  {
    "clicks": 50,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 13,
    "impressions": 52342,
    "poi_id": 1,
    "revenue": 239.2027510000000
  },
  {
    "clicks": 53,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 14,
    "impressions": 50903,
    "poi_id": 2,
    "revenue": 233.5372990000000
  },
  {
    "clicks": 55,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 15,
    "impressions": 47794,
    "poi_id": 4,
    "revenue": 225.0855990000000
  },
  {
    "clicks": 62,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 16,
    "impressions": 47628,
    "poi_id": 4,
    "revenue": 225.6750690000000
  },
  {
    "clicks": 70,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 17,
    "impressions": 48000,
    "poi_id": 2,
    "revenue": 238.4758720000000
  },
  {
    "clicks": 51,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 18,
    "impressions": 47138,
    "poi_id": 4,
    "revenue": 232.1392190000000
  },
  {
    "clicks": 66,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 19,
    "impressions": 43525,
    "poi_id": 4,
    "revenue": 215.5197710000000
  },
  {
    "clicks": 54,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 20,
    "impressions": 43579,
    "poi_id": 1,
    "revenue": 213.8766470000000
  },
  {
    "clicks": 50,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 21,
    "impressions": 42519,
    "poi_id": 1,
    "revenue": 207.0633420000000
  },
  {
    "clicks": 48,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 22,
    "impressions": 37063,
    "poi_id": 1,
    "revenue": 169.1746510000000
  },
  {
    "clicks": 29,
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "hour": 23,
    "impressions": 19992,
    "poi_id": 3,
    "revenue": 105.1058380000000
  },
  {
    "clicks": 40,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 0,
    "impressions": 18087,
    "poi_id": 2,
    "revenue": 84.8078360000000
  },
  {
    "clicks": 59,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 1,
    "impressions": 32617,
    "poi_id": 4,
    "revenue": 125.4369970000000
  },
  {
    "clicks": 22,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 2,
    "impressions": 25736,
    "poi_id": 2,
    "revenue": 74.4438110000000
  },
  {
    "clicks": 11,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 3,
    "impressions": 19339,
    "poi_id": 3,
    "revenue": 38.6491520000000
  },
  {
    "clicks": 13,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 4,
    "impressions": 21218,
    "poi_id": 3,
    "revenue": 47.7479600000000
  },
  {
    "clicks": 9,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 5,
    "impressions": 22531,
    "poi_id": 4,
    "revenue": 63.4525230000000
  },
  {
    "clicks": 65,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 6,
    "impressions": 45906,
    "poi_id": 1,
    "revenue": 248.0314750000000
  },
  {
    "clicks": 66,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 7,
    "impressions": 48250,
    "poi_id": 2,
    "revenue": 249.0314090000000
  },
  {
    "clicks": 78,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 8,
    "impressions": 53515,
    "poi_id": 1,
    "revenue": 280.8003440000000
  },
  {
    "clicks": 81,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 9,
    "impressions": 52715,
    "poi_id": 2,
    "revenue": 269.3409560000000
  },
  {
    "clicks": 77,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 10,
    "impressions": 50166,
    "poi_id": 1,
    "revenue": 253.7730060000000
  },
  {
    "clicks": 61,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 11,
    "impressions": 48047,
    "poi_id": 3,
    "revenue": 243.0035030000000
  },
  {
    "clicks": 57,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 12,
    "impressions": 74993,
    "poi_id": 1,
    "revenue": 269.7355090000000
  },
  {
    "clicks": 96,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 13,
    "impressions": 71068,
    "poi_id": 4,
    "revenue": 258.4626040000000
  },
  {
    "clicks": 55,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 14,
    "impressions": 68003,
    "poi_id": 3,
    "revenue": 251.7689310000000
  },
  {
    "clicks": 72,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 15,
    "impressions": 65106,
    "poi_id": 4,
    "revenue": 250.6005740000000
  },
  {
    "clicks": 79,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 16,
    "impressions": 60888,
    "poi_id": 2,
    "revenue": 235.8163120000000
  },
  {
    "clicks": 84,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 17,
    "impressions": 61449,
    "poi_id": 4,
    "revenue": 244.7288860000000
  },
  {
    "clicks": 82,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 18,
    "impressions": 58052,
    "poi_id": 4,
    "revenue": 243.2341800000000
  },
  {
    "clicks": 78,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 19,
    "impressions": 52004,
    "poi_id": 1,
    "revenue": 229.9988450000000
  },
  {
    "clicks": 91,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 20,
    "impressions": 52134,
    "poi_id": 1,
    "revenue": 230.4846730000000
  },
  {
    "clicks": 79,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 21,
    "impressions": 51259,
    "poi_id": 2,
    "revenue": 223.9919720000000
  },
  {
    "clicks": 77,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 22,
    "impressions": 44417,
    "poi_id": 1,
    "revenue": 189.1914210000000
  },
  {
    "clicks": 41,
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "hour": 23,
    "impressions": 24532,
    "poi_id": 1,
    "revenue": 127.1229570000000
  },
  {
    "clicks": 67,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 0,
    "impressions": 20217,
    "poi_id": 3,
    "revenue": 95.1189460000000
  },
  {
    "clicks": 60,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 1,
    "impressions": 31637,
    "poi_id": 1,
    "revenue": 123.9998600000000
  },
  {
    "clicks": 38,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 2,
    "impressions": 27410,
    "poi_id": 4,
    "revenue": 85.9776660000000
  },
  {
    "clicks": 6,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 3,
    "impressions": 19629,
    "poi_id": 4,
    "revenue": 40.0719810000000
  },
  {
    "clicks": 12,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 4,
    "impressions": 19992,
    "poi_id": 1,
    "revenue": 47.0120870000000
  },
  {
    "clicks": 8,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 5,
    "impressions": 20838,
    "poi_id": 4,
    "revenue": 58.2720540000000
  },
  {
    "clicks": 77,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 6,
    "impressions": 43948,
    "poi_id": 2,
    "revenue": 241.6657770000000
  },
  {
    "clicks": 98,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 7,
    "impressions": 49556,
    "poi_id": 3,
    "revenue": 252.3126290000000
  },
  {
    "clicks": 97,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 8,
    "impressions": 60859,
    "poi_id": 3,
    "revenue": 275.8964840000000
  },
  {
    "clicks": 94,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 9,
    "impressions": 61209,
    "poi_id": 4,
    "revenue": 273.2124780000000
  },
  {
    "clicks": 96,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 10,
    "impressions": 59768,
    "poi_id": 2,
    "revenue": 265.8951580000000
  },
  {
    "clicks": 81,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 11,
    "impressions": 60831,
    "poi_id": 1,
    "revenue": 258.3778300000000
  },
  {
    "clicks": 81,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 12,
    "impressions": 61682,
    "poi_id": 3,
    "revenue": 253.6509280000000
  },
  {
    "clicks": 79,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 13,
    "impressions": 60679,
    "poi_id": 3,
    "revenue": 250.0681240000000
  },
  {
    "clicks": 65,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 14,
    "impressions": 59211,
    "poi_id": 3,
    "revenue": 238.9390140000000
  },
  {
    "clicks": 74,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 15,
    "impressions": 59092,
    "poi_id": 4,
    "revenue": 239.1331930000000
  },
  {
    "clicks": 70,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 16,
    "impressions": 57960,
    "poi_id": 4,
    "revenue": 234.0132630000000
  },
  {
    "clicks": 84,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 17,
    "impressions": 56197,
    "poi_id": 3,
    "revenue": 227.7702160000000
  },
  {
    "clicks": 64,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 18,
    "impressions": 56268,
    "poi_id": 2,
    "revenue": 229.2961960000000
  },
  {
    "clicks": 70,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 19,
    "impressions": 51332,
    "poi_id": 1,
    "revenue": 219.9699670000000
  },
  {
    "clicks": 71,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 20,
    "impressions": 53153,
    "poi_id": 3,
    "revenue": 220.2625790000000
  },
  {
    "clicks": 60,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 21,
    "impressions": 53117,
    "poi_id": 4,
    "revenue": 216.3960460000000
  },
  {
    "clicks": 56,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 22,
    "impressions": 46493,
    "poi_id": 4,
    "revenue": 183.7111940000000
  },
  {
    "clicks": 39,
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "hour": 23,
    "impressions": 24244,
    "poi_id": 4,
    "revenue": 113.0830980000000
  }
]
    events_hourly = [
  {
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "events": 14,
    "hour": 1,
    "poi_id": 4
  },
  {
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 4,
    "poi_id": 3
  },
  {
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 7,
    "poi_id": 3
  },
  {
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 14,
    "poi_id": 4
  },
  {
    "date": "Sun, 01 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 22,
    "poi_id": 4
  },
  {
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 6,
    "poi_id": 3
  },
  {
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 8,
    "poi_id": 2
  },
  {
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 11,
    "poi_id": 1
  },
  {
    "date": "Mon, 02 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 14,
    "poi_id": 1
  },
  {
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 0,
    "poi_id": 3
  },
  {
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "events": 3,
    "hour": 8,
    "poi_id": 1
  },
  {
    "date": "Tue, 03 Jan 2017 00:00:00 GMT",
    "events": 1,
    "hour": 11,
    "poi_id": 2
  },
  {
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 0,
    "poi_id": 2
  },
  {
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 5,
    "poi_id": 2
  },
  {
    "date": "Wed, 04 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 14,
    "poi_id": 4
  },
  {
    "date": "Thu, 05 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 20,
    "poi_id": 3
  },
  {
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 1,
    "poi_id": 1
  },
  {
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 6,
    "poi_id": 3
  },
  {
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 9,
    "poi_id": 4
  },
  {
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "events": 3,
    "hour": 11,
    "poi_id": 3
  },
  {
    "date": "Fri, 06 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 12,
    "poi_id": 1
  },
  {
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 1,
    "poi_id": 3
  },
  {
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 3,
    "poi_id": 3
  },
  {
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "events": 3,
    "hour": 12,
    "poi_id": 1
  },
  {
    "date": "Sat, 07 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 19,
    "poi_id": 4
  },
  {
    "date": "Sun, 08 Jan 2017 00:00:00 GMT",
    "events": 14,
    "hour": 5,
    "poi_id": 1
  },
  {
    "date": "Sun, 08 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 11,
    "poi_id": 2
  },
  {
    "date": "Sun, 08 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 13,
    "poi_id": 3
  },
  {
    "date": "Mon, 09 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 0,
    "poi_id": 2
  },
  {
    "date": "Mon, 09 Jan 2017 00:00:00 GMT",
    "events": 1,
    "hour": 3,
    "poi_id": 3
  },
  {
    "date": "Mon, 09 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 5,
    "poi_id": 1
  },
  {
    "date": "Mon, 09 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 8,
    "poi_id": 1
  },
  {
    "date": "Mon, 09 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 11,
    "poi_id": 2
  },
  {
    "date": "Mon, 09 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 19,
    "poi_id": 3
  },
  {
    "date": "Mon, 09 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 23,
    "poi_id": 1
  },
  {
    "date": "Tue, 10 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 9,
    "poi_id": 1
  },
  {
    "date": "Tue, 10 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 11,
    "poi_id": 2
  },
  {
    "date": "Tue, 10 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 22,
    "poi_id": 2
  },
  {
    "date": "Wed, 11 Jan 2017 00:00:00 GMT",
    "events": 3,
    "hour": 2,
    "poi_id": 1
  },
  {
    "date": "Wed, 11 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 6,
    "poi_id": 3
  },
  {
    "date": "Wed, 11 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 10,
    "poi_id": 1
  },
  {
    "date": "Thu, 12 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 9,
    "poi_id": 1
  },
  {
    "date": "Thu, 12 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 13,
    "poi_id": 1
  },
  {
    "date": "Fri, 13 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 2,
    "poi_id": 2
  },
  {
    "date": "Fri, 13 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 7,
    "poi_id": 3
  },
  {
    "date": "Fri, 13 Jan 2017 00:00:00 GMT",
    "events": 9,
    "hour": 10,
    "poi_id": 1
  },
  {
    "date": "Fri, 13 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 14,
    "poi_id": 4
  },
  {
    "date": "Fri, 13 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 19,
    "poi_id": 4
  },
  {
    "date": "Fri, 13 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 21,
    "poi_id": 3
  },
  {
    "date": "Sat, 14 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 2,
    "poi_id": 4
  },
  {
    "date": "Sat, 14 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 7,
    "poi_id": 2
  },
  {
    "date": "Sat, 14 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 8,
    "poi_id": 3
  },
  {
    "date": "Sun, 15 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 5,
    "poi_id": 3
  },
  {
    "date": "Mon, 16 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 1,
    "poi_id": 4
  },
  {
    "date": "Mon, 16 Jan 2017 00:00:00 GMT",
    "events": 9,
    "hour": 11,
    "poi_id": 4
  },
  {
    "date": "Mon, 16 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 19,
    "poi_id": 2
  },
  {
    "date": "Mon, 16 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 20,
    "poi_id": 1
  },
  {
    "date": "Tue, 17 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 3,
    "poi_id": 1
  },
  {
    "date": "Tue, 17 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 17,
    "poi_id": 4
  },
  {
    "date": "Wed, 18 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 0,
    "poi_id": 2
  },
  {
    "date": "Wed, 18 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 3,
    "poi_id": 3
  },
  {
    "date": "Wed, 18 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 5,
    "poi_id": 1
  },
  {
    "date": "Wed, 18 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 13,
    "poi_id": 3
  },
  {
    "date": "Wed, 18 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 19,
    "poi_id": 4
  },
  {
    "date": "Thu, 19 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 0,
    "poi_id": 4
  },
  {
    "date": "Thu, 19 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 1,
    "poi_id": 4
  },
  {
    "date": "Thu, 19 Jan 2017 00:00:00 GMT",
    "events": 14,
    "hour": 5,
    "poi_id": 1
  },
  {
    "date": "Thu, 19 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 7,
    "poi_id": 2
  },
  {
    "date": "Thu, 19 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 8,
    "poi_id": 2
  },
  {
    "date": "Thu, 19 Jan 2017 00:00:00 GMT",
    "events": 9,
    "hour": 22,
    "poi_id": 1
  },
  {
    "date": "Fri, 20 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 4,
    "poi_id": 4
  },
  {
    "date": "Fri, 20 Jan 2017 00:00:00 GMT",
    "events": 3,
    "hour": 8,
    "poi_id": 2
  },
  {
    "date": "Fri, 20 Jan 2017 00:00:00 GMT",
    "events": 9,
    "hour": 14,
    "poi_id": 2
  },
  {
    "date": "Fri, 20 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 15,
    "poi_id": 1
  },
  {
    "date": "Fri, 20 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 17,
    "poi_id": 3
  },
  {
    "date": "Fri, 20 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 18,
    "poi_id": 4
  },
  {
    "date": "Fri, 20 Jan 2017 00:00:00 GMT",
    "events": 9,
    "hour": 20,
    "poi_id": 1
  },
  {
    "date": "Sat, 21 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 4,
    "poi_id": 3
  },
  {
    "date": "Sat, 21 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 12,
    "poi_id": 3
  },
  {
    "date": "Sun, 22 Jan 2017 00:00:00 GMT",
    "events": 3,
    "hour": 4,
    "poi_id": 3
  },
  {
    "date": "Sun, 22 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 7,
    "poi_id": 3
  },
  {
    "date": "Sun, 22 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 14,
    "poi_id": 1
  },
  {
    "date": "Mon, 23 Jan 2017 00:00:00 GMT",
    "events": 1,
    "hour": 10,
    "poi_id": 1
  },
  {
    "date": "Mon, 23 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 17,
    "poi_id": 1
  },
  {
    "date": "Mon, 23 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 18,
    "poi_id": 1
  },
  {
    "date": "Tue, 24 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 2,
    "poi_id": 4
  },
  {
    "date": "Tue, 24 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 7,
    "poi_id": 3
  },
  {
    "date": "Tue, 24 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 8,
    "poi_id": 1
  },
  {
    "date": "Tue, 24 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 9,
    "poi_id": 4
  },
  {
    "date": "Tue, 24 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 16,
    "poi_id": 3
  },
  {
    "date": "Tue, 24 Jan 2017 00:00:00 GMT",
    "events": 1,
    "hour": 20,
    "poi_id": 3
  },
  {
    "date": "Wed, 25 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 0,
    "poi_id": 3
  },
  {
    "date": "Wed, 25 Jan 2017 00:00:00 GMT",
    "events": 1,
    "hour": 2,
    "poi_id": 3
  },
  {
    "date": "Wed, 25 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 6,
    "poi_id": 1
  },
  {
    "date": "Wed, 25 Jan 2017 00:00:00 GMT",
    "events": 8,
    "hour": 9,
    "poi_id": 3
  },
  {
    "date": "Thu, 26 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 1,
    "poi_id": 3
  },
  {
    "date": "Thu, 26 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 3,
    "poi_id": 4
  },
  {
    "date": "Thu, 26 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 11,
    "poi_id": 3
  },
  {
    "date": "Thu, 26 Jan 2017 00:00:00 GMT",
    "events": 11,
    "hour": 12,
    "poi_id": 4
  },
  {
    "date": "Thu, 26 Jan 2017 00:00:00 GMT",
    "events": 13,
    "hour": 14,
    "poi_id": 1
  },
  {
    "date": "Thu, 26 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 19,
    "poi_id": 4
  },
  {
    "date": "Thu, 26 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 22,
    "poi_id": 3
  },
  {
    "date": "Fri, 27 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 20,
    "poi_id": 2
  },
  {
    "date": "Fri, 27 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 23,
    "poi_id": 1
  },
  {
    "date": "Sat, 28 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 3,
    "poi_id": 3
  },
  {
    "date": "Sat, 28 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 7,
    "poi_id": 1
  },
  {
    "date": "Sat, 28 Jan 2017 00:00:00 GMT",
    "events": 3,
    "hour": 13,
    "poi_id": 1
  },
  {
    "date": "Sat, 28 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 15,
    "poi_id": 3
  },
  {
    "date": "Sat, 28 Jan 2017 00:00:00 GMT",
    "events": 10,
    "hour": 16,
    "poi_id": 4
  },
  {
    "date": "Sat, 28 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 21,
    "poi_id": 4
  },
  {
    "date": "Sun, 29 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 4,
    "poi_id": 1
  },
  {
    "date": "Sun, 29 Jan 2017 00:00:00 GMT",
    "events": 12,
    "hour": 6,
    "poi_id": 2
  },
  {
    "date": "Sun, 29 Jan 2017 00:00:00 GMT",
    "events": 14,
    "hour": 14,
    "poi_id": 4
  },
  {
    "date": "Sun, 29 Jan 2017 00:00:00 GMT",
    "events": 4,
    "hour": 22,
    "poi_id": 2
  },
  {
    "date": "Mon, 30 Jan 2017 00:00:00 GMT",
    "events": 6,
    "hour": 5,
    "poi_id": 3
  },
  {
    "date": "Mon, 30 Jan 2017 00:00:00 GMT",
    "events": 14,
    "hour": 6,
    "poi_id": 4
  },
  {
    "date": "Mon, 30 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 7,
    "poi_id": 2
  },
  {
    "date": "Mon, 30 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 11,
    "poi_id": 2
  },
  {
    "date": "Mon, 30 Jan 2017 00:00:00 GMT",
    "events": 7,
    "hour": 13,
    "poi_id": 1
  },
  {
    "date": "Mon, 30 Jan 2017 00:00:00 GMT",
    "events": 5,
    "hour": 17,
    "poi_id": 1
  },
  {
    "date": "Tue, 31 Jan 2017 00:00:00 GMT",
    "events": 14,
    "hour": 11,
    "poi_id": 4
  },
  {
    "date": "Tue, 31 Jan 2017 00:00:00 GMT",
    "events": 2,
    "hour": 14,
    "poi_id": 3
  },
  {
    "date": "Tue, 31 Jan 2017 00:00:00 GMT",
    "events": 14,
    "hour": 18,
    "poi_id": 4
  },
  {
    "date": "Tue, 31 Jan 2017 00:00:00 GMT",
    "events": 9,
    "hour": 20,
    "poi_id": 3
  },
  {
    "date": "Wed, 01 Feb 2017 00:00:00 GMT",
    "events": 5,
    "hour": 2,
    "poi_id": 3
  },
  {
    "date": "Wed, 01 Feb 2017 00:00:00 GMT",
    "events": 7,
    "hour": 8,
    "poi_id": 2
  },
  {
    "date": "Wed, 01 Feb 2017 00:00:00 GMT",
    "events": 13,
    "hour": 16,
    "poi_id": 1
  },
  {
    "date": "Thu, 02 Feb 2017 00:00:00 GMT",
    "events": 9,
    "hour": 0,
    "poi_id": 3
  },
  {
    "date": "Thu, 02 Feb 2017 00:00:00 GMT",
    "events": 10,
    "hour": 19,
    "poi_id": 1
  },
  {
    "date": "Thu, 02 Feb 2017 00:00:00 GMT",
    "events": 8,
    "hour": 21,
    "poi_id": 1
  },
  {
    "date": "Fri, 03 Feb 2017 00:00:00 GMT",
    "events": 13,
    "hour": 5,
    "poi_id": 3
  },
  {
    "date": "Fri, 03 Feb 2017 00:00:00 GMT",
    "events": 13,
    "hour": 8,
    "poi_id": 4
  },
  {
    "date": "Fri, 03 Feb 2017 00:00:00 GMT",
    "events": 9,
    "hour": 12,
    "poi_id": 3
  },
  {
    "date": "Fri, 03 Feb 2017 00:00:00 GMT",
    "events": 12,
    "hour": 16,
    "poi_id": 1
  },
  {
    "date": "Sat, 04 Feb 2017 00:00:00 GMT",
    "events": 11,
    "hour": 9,
    "poi_id": 1
  },
  {
    "date": "Sat, 04 Feb 2017 00:00:00 GMT",
    "events": 6,
    "hour": 10,
    "poi_id": 2
  },
  {
    "date": "Sat, 04 Feb 2017 00:00:00 GMT",
    "events": 12,
    "hour": 13,
    "poi_id": 2
  },
  {
    "date": "Sat, 04 Feb 2017 00:00:00 GMT",
    "events": 8,
    "hour": 23,
    "poi_id": 1
  },
  {
    "date": "Sun, 05 Feb 2017 00:00:00 GMT",
    "events": 10,
    "hour": 12,
    "poi_id": 1
  },
  {
    "date": "Sun, 05 Feb 2017 00:00:00 GMT",
    "events": 2,
    "hour": 16,
    "poi_id": 1
  },
  {
    "date": "Sun, 05 Feb 2017 00:00:00 GMT",
    "events": 6,
    "hour": 20,
    "poi_id": 4
  },
  {
    "date": "Sun, 05 Feb 2017 00:00:00 GMT",
    "events": 3,
    "hour": 21,
    "poi_id": 2
  },
  {
    "date": "Mon, 06 Feb 2017 00:00:00 GMT",
    "events": 4,
    "hour": 9,
    "poi_id": 3
  },
  {
    "date": "Mon, 06 Feb 2017 00:00:00 GMT",
    "events": 14,
    "hour": 13,
    "poi_id": 4
  },
  {
    "date": "Mon, 06 Feb 2017 00:00:00 GMT",
    "events": 7,
    "hour": 16,
    "poi_id": 3
  },
  {
    "date": "Mon, 06 Feb 2017 00:00:00 GMT",
    "events": 2,
    "hour": 23,
    "poi_id": 2
  },
  {
    "date": "Tue, 07 Feb 2017 00:00:00 GMT",
    "events": 3,
    "hour": 3,
    "poi_id": 4
  },
  {
    "date": "Tue, 07 Feb 2017 00:00:00 GMT",
    "events": 1,
    "hour": 13,
    "poi_id": 4
  },
  {
    "date": "Tue, 07 Feb 2017 00:00:00 GMT",
    "events": 10,
    "hour": 22,
    "poi_id": 3
  },
  {
    "date": "Wed, 08 Feb 2017 00:00:00 GMT",
    "events": 4,
    "hour": 5,
    "poi_id": 4
  },
  {
    "date": "Wed, 08 Feb 2017 00:00:00 GMT",
    "events": 4,
    "hour": 13,
    "poi_id": 1
  },
  {
    "date": "Wed, 08 Feb 2017 00:00:00 GMT",
    "events": 9,
    "hour": 17,
    "poi_id": 3
  },
  {
    "date": "Wed, 08 Feb 2017 00:00:00 GMT",
    "events": 13,
    "hour": 22,
    "poi_id": 2
  },
  {
    "date": "Wed, 08 Feb 2017 00:00:00 GMT",
    "events": 4,
    "hour": 23,
    "poi_id": 1
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 13,
    "hour": 2,
    "poi_id": 2
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 4,
    "hour": 6,
    "poi_id": 4
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 5,
    "hour": 7,
    "poi_id": 3
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 3,
    "hour": 8,
    "poi_id": 2
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 2,
    "hour": 17,
    "poi_id": 2
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 14,
    "hour": 18,
    "poi_id": 3
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 2,
    "hour": 19,
    "poi_id": 2
  },
  {
    "date": "Thu, 09 Feb 2017 00:00:00 GMT",
    "events": 11,
    "hour": 22,
    "poi_id": 1
  },
  {
    "date": "Fri, 10 Feb 2017 00:00:00 GMT",
    "events": 8,
    "hour": 5,
    "poi_id": 3
  },
  {
    "date": "Fri, 10 Feb 2017 00:00:00 GMT",
    "events": 5,
    "hour": 7,
    "poi_id": 1
  },
  {
    "date": "Fri, 10 Feb 2017 00:00:00 GMT",
    "events": 1,
    "hour": 9,
    "poi_id": 2
  },
  {
    "date": "Fri, 10 Feb 2017 00:00:00 GMT",
    "events": 13,
    "hour": 22,
    "poi_id": 3
  },
  {
    "date": "Sat, 11 Feb 2017 00:00:00 GMT",
    "events": 5,
    "hour": 7,
    "poi_id": 3
  },
  {
    "date": "Sat, 11 Feb 2017 00:00:00 GMT",
    "events": 4,
    "hour": 14,
    "poi_id": 3
  }
]
    click_daily = [
      {
        "clicks": 3627,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "impressions": 2764609,
        "revenue": 13092.1234790000000
      },
      {
        "clicks": 1489,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "impressions": 943070,
        "revenue": 4275.3479640000000
      },
      {
        "clicks": 1274,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "impressions": 962220,
        "revenue": 4349.9616000000000
      },
      {
        "clicks": 1311,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "impressions": 948574,
        "revenue": 4364.3495500000000
      },
      {
        "clicks": 1210,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "impressions": 952714,
        "revenue": 4496.4799380000000
      },
      {
        "clicks": 1473,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "impressions": 1122032,
        "revenue": 4733.6558360000000
      },
      {
        "clicks": 1547,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "impressions": 1115322,
        "revenue": 4644.1067680000000
      }
    ]
    click_hourly = [
      {
        "clicks": 23,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 0,
        "impressions": 10746,
        "revenue": 64.9215630000000
      },
      {
        "clicks": 201,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 1,
        "impressions": 141397,
        "revenue": 696.4485960000000
      },
      {
        "clicks": 217,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 2,
        "impressions": 137464,
        "revenue": 732.0955030000000
      },
      {
        "clicks": 139,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 3,
        "impressions": 109217,
        "revenue": 496.6397510000000
      },
      {
        "clicks": 74,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 4,
        "impressions": 112129,
        "revenue": 446.7138830000000
      },
      {
        "clicks": 76,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 5,
        "impressions": 105182,
        "revenue": 435.9536840000000
      },
      {
        "clicks": 152,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 6,
        "impressions": 111925,
        "revenue": 519.1064970000000
      },
      {
        "clicks": 129,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 7,
        "impressions": 106769,
        "revenue": 483.0718670000000
      },
      {
        "clicks": 135,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 8,
        "impressions": 123464,
        "revenue": 561.3373030000000
      },
      {
        "clicks": 163,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 9,
        "impressions": 145333,
        "revenue": 637.8506700000000
      },
      {
        "clicks": 180,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 10,
        "impressions": 152529,
        "revenue": 657.6138580000000
      },
      {
        "clicks": 200,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 11,
        "impressions": 165321,
        "revenue": 647.5332910000000
      },
      {
        "clicks": 195,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 12,
        "impressions": 152531,
        "revenue": 684.3440180000000
      },
      {
        "clicks": 181,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 13,
        "impressions": 143520,
        "revenue": 646.0625610000000
      },
      {
        "clicks": 314,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 14,
        "impressions": 168021,
        "revenue": 886.5780050000000
      },
      {
        "clicks": 193,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 15,
        "impressions": 127771,
        "revenue": 599.0013210000000
      },
      {
        "clicks": 211,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 16,
        "impressions": 106157,
        "revenue": 603.1255660000000
      },
      {
        "clicks": 191,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 17,
        "impressions": 104870,
        "revenue": 563.1118780000000
      },
      {
        "clicks": 173,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 18,
        "impressions": 86798,
        "revenue": 488.8465350000000
      },
      {
        "clicks": 210,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 19,
        "impressions": 165917,
        "revenue": 853.6791170000000
      },
      {
        "clicks": 99,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 20,
        "impressions": 95662,
        "revenue": 452.6468010000000
      },
      {
        "clicks": 61,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 21,
        "impressions": 60086,
        "revenue": 280.0887910000000
      },
      {
        "clicks": 86,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 22,
        "impressions": 113981,
        "revenue": 561.3447040000000
      },
      {
        "clicks": 24,
        "date": "Sun, 01 Jan 2017 00:00:00 GMT",
        "hour": 23,
        "impressions": 17819,
        "revenue": 94.0077160000000
      },
      {
        "clicks": 56,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 0,
        "impressions": 13316,
        "revenue": 69.9917250000000
      },
      {
        "clicks": 69,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 1,
        "impressions": 32275,
        "revenue": 115.2967230000000
      },
      {
        "clicks": 33,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 2,
        "impressions": 25567,
        "revenue": 71.9015000000000
      },
      {
        "clicks": 12,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 3,
        "impressions": 24386,
        "revenue": 43.9822160000000
      },
      {
        "clicks": 6,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 4,
        "impressions": 22305,
        "revenue": 48.8441270000000
      },
      {
        "clicks": 12,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 5,
        "impressions": 23725,
        "revenue": 63.5116560000000
      },
      {
        "clicks": 56,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 6,
        "impressions": 42763,
        "revenue": 223.0633420000000
      },
      {
        "clicks": 56,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 7,
        "impressions": 40521,
        "revenue": 220.4801670000000
      },
      {
        "clicks": 57,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 8,
        "impressions": 44862,
        "revenue": 241.3888750000000
      },
      {
        "clicks": 94,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 9,
        "impressions": 49395,
        "revenue": 249.6256080000000
      },
      {
        "clicks": 69,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 10,
        "impressions": 45008,
        "revenue": 245.4707360000000
      },
      {
        "clicks": 87,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 11,
        "impressions": 48927,
        "revenue": 242.2166710000000
      },
      {
        "clicks": 90,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 12,
        "impressions": 48836,
        "revenue": 231.3379990000000
      },
      {
        "clicks": 71,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 13,
        "impressions": 48813,
        "revenue": 225.6352260000000
      },
      {
        "clicks": 85,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 14,
        "impressions": 48375,
        "revenue": 229.2786800000000
      },
      {
        "clicks": 57,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 15,
        "impressions": 49551,
        "revenue": 223.7558460000000
      },
      {
        "clicks": 79,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 16,
        "impressions": 48362,
        "revenue": 218.2177440000000
      },
      {
        "clicks": 94,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 17,
        "impressions": 47735,
        "revenue": 217.3931840000000
      },
      {
        "clicks": 76,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 18,
        "impressions": 46311,
        "revenue": 210.8744190000000
      },
      {
        "clicks": 67,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 19,
        "impressions": 45117,
        "revenue": 209.2310100000000
      },
      {
        "clicks": 66,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 20,
        "impressions": 44123,
        "revenue": 202.8335090000000
      },
      {
        "clicks": 78,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 21,
        "impressions": 43651,
        "revenue": 201.6316030000000
      },
      {
        "clicks": 71,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 22,
        "impressions": 38390,
        "revenue": 168.7712120000000
      },
      {
        "clicks": 48,
        "date": "Mon, 02 Jan 2017 00:00:00 GMT",
        "hour": 23,
        "impressions": 20756,
        "revenue": 100.6141860000000
      },
      {
        "clicks": 67,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 0,
        "impressions": 18307,
        "revenue": 87.4227050000000
      },
      {
        "clicks": 59,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 1,
        "impressions": 30113,
        "revenue": 110.7214860000000
      },
      {
        "clicks": 29,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 2,
        "impressions": 27469,
        "revenue": 73.0471470000000
      },
      {
        "clicks": 6,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 3,
        "impressions": 17418,
        "revenue": 32.9492880000000
      },
      {
        "clicks": 15,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 4,
        "impressions": 21419,
        "revenue": 43.1942410000000
      },
      {
        "clicks": 23,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 5,
        "impressions": 20871,
        "revenue": 54.7799660000000
      },
      {
        "clicks": 72,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 6,
        "impressions": 41661,
        "revenue": 215.0006050000000
      },
      {
        "clicks": 62,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 7,
        "impressions": 46586,
        "revenue": 229.3272530000000
      },
      {
        "clicks": 84,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 8,
        "impressions": 49793,
        "revenue": 248.0798430000000
      },
      {
        "clicks": 55,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 9,
        "impressions": 45010,
        "revenue": 223.4354770000000
      },
      {
        "clicks": 79,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 10,
        "impressions": 56260,
        "revenue": 264.6692640000000
      },
      {
        "clicks": 74,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 11,
        "impressions": 56859,
        "revenue": 284.8601950000000
      },
      {
        "clicks": 73,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 12,
        "impressions": 53547,
        "revenue": 254.4689300000000
      },
      {
        "clicks": 60,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 13,
        "impressions": 52312,
        "revenue": 245.0337340000000
      },
      {
        "clicks": 56,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 14,
        "impressions": 50947,
        "revenue": 238.0440430000000
      },
      {
        "clicks": 59,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 15,
        "impressions": 48849,
        "revenue": 221.1546890000000
      },
      {
        "clicks": 64,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 16,
        "impressions": 46647,
        "revenue": 215.6478030000000
      },
      {
        "clicks": 50,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 17,
        "impressions": 47437,
        "revenue": 217.6272090000000
      },
      {
        "clicks": 50,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 18,
        "impressions": 45867,
        "revenue": 210.7244290000000
      },
      {
        "clicks": 66,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 19,
        "impressions": 42472,
        "revenue": 205.9077960000000
      },
      {
        "clicks": 58,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 20,
        "impressions": 43274,
        "revenue": 205.6855580000000
      },
      {
        "clicks": 58,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 21,
        "impressions": 42913,
        "revenue": 205.8066010000000
      },
      {
        "clicks": 34,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 22,
        "impressions": 37201,
        "revenue": 168.9752980000000
      },
      {
        "clicks": 21,
        "date": "Tue, 03 Jan 2017 00:00:00 GMT",
        "hour": 23,
        "impressions": 18988,
        "revenue": 93.3980400000000
      },
      {
        "clicks": 51,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 0,
        "impressions": 19744,
        "revenue": 96.7490290000000
      },
      {
        "clicks": 52,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 1,
        "impressions": 31576,
        "revenue": 127.0472440000000
      },
      {
        "clicks": 31,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 2,
        "impressions": 24471,
        "revenue": 72.9980320000000
      },
      {
        "clicks": 6,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 3,
        "impressions": 15103,
        "revenue": 32.2022460000000
      },
      {
        "clicks": 8,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 4,
        "impressions": 20216,
        "revenue": 45.5858750000000
      },
      {
        "clicks": 9,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 5,
        "impressions": 19679,
        "revenue": 56.8603970000000
      },
      {
        "clicks": 65,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 6,
        "impressions": 45383,
        "revenue": 243.3083480000000
      },
      {
        "clicks": 55,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 7,
        "impressions": 47779,
        "revenue": 238.6230680000000
      },
      {
        "clicks": 64,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 8,
        "impressions": 52703,
        "revenue": 261.5696250000000
      },
      {
        "clicks": 63,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 9,
        "impressions": 52978,
        "revenue": 257.3575390000000
      },
      {
        "clicks": 66,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 10,
        "impressions": 50976,
        "revenue": 248.2284500000000
      },
      {
        "clicks": 68,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 11,
        "impressions": 50652,
        "revenue": 245.2707750000000
      },
      {
        "clicks": 66,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 12,
        "impressions": 50382,
        "revenue": 238.7660000000000
      },
      {
        "clicks": 78,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 13,
        "impressions": 49857,
        "revenue": 234.4847420000000
      },
      {
        "clicks": 74,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 14,
        "impressions": 48773,
        "revenue": 227.8905720000000
      },
      {
        "clicks": 71,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 15,
        "impressions": 44999,
        "revenue": 215.9949090000000
      },
      {
        "clicks": 58,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 16,
        "impressions": 47213,
        "revenue": 222.4189280000000
      },
      {
        "clicks": 57,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 17,
        "impressions": 45531,
        "revenue": 214.7642890000000
      },
      {
        "clicks": 64,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 18,
        "impressions": 44255,
        "revenue": 208.0608440000000
      },
      {
        "clicks": 64,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 19,
        "impressions": 42494,
        "revenue": 206.2058220000000
      },
      {
        "clicks": 72,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 20,
        "impressions": 43345,
        "revenue": 205.2605540000000
      },
      {
        "clicks": 71,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 21,
        "impressions": 43552,
        "revenue": 201.9234330000000
      },
      {
        "clicks": 59,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 22,
        "impressions": 37205,
        "revenue": 166.0467280000000
      },
      {
        "clicks": 39,
        "date": "Wed, 04 Jan 2017 00:00:00 GMT",
        "hour": 23,
        "impressions": 19708,
        "revenue": 96.7321010000000
      },
      {
        "clicks": 62,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 0,
        "impressions": 20163,
        "revenue": 98.1922020000000
      },
      {
        "clicks": 42,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 1,
        "impressions": 29395,
        "revenue": 124.0678140000000
      },
      {
        "clicks": 24,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 2,
        "impressions": 22507,
        "revenue": 72.2681070000000
      },
      {
        "clicks": 13,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 3,
        "impressions": 14545,
        "revenue": 35.6927280000000
      },
      {
        "clicks": 5,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 4,
        "impressions": 14889,
        "revenue": 36.9674330000000
      },
      {
        "clicks": 15,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 5,
        "impressions": 19443,
        "revenue": 62.0260700000000
      },
      {
        "clicks": 67,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 6,
        "impressions": 43959,
        "revenue": 238.7670680000000
      },
      {
        "clicks": 54,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 7,
        "impressions": 47634,
        "revenue": 239.2143510000000
      },
      {
        "clicks": 69,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 8,
        "impressions": 52186,
        "revenue": 263.4281800000000
      },
      {
        "clicks": 63,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 9,
        "impressions": 52899,
        "revenue": 261.4129600000000
      },
      {
        "clicks": 67,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 10,
        "impressions": 53064,
        "revenue": 262.6935900000000
      },
      {
        "clicks": 65,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 11,
        "impressions": 49619,
        "revenue": 246.4739270000000
      },
      {
        "clicks": 76,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 12,
        "impressions": 51928,
        "revenue": 250.4194500000000
      },
      {
        "clicks": 50,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 13,
        "impressions": 52342,
        "revenue": 239.2027510000000
      },
      {
        "clicks": 53,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 14,
        "impressions": 50903,
        "revenue": 233.5372990000000
      },
      {
        "clicks": 55,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 15,
        "impressions": 47794,
        "revenue": 225.0855990000000
      },
      {
        "clicks": 62,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 16,
        "impressions": 47628,
        "revenue": 225.6750690000000
      },
      {
        "clicks": 70,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 17,
        "impressions": 48000,
        "revenue": 238.4758720000000
      },
      {
        "clicks": 51,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 18,
        "impressions": 47138,
        "revenue": 232.1392190000000
      },
      {
        "clicks": 66,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 19,
        "impressions": 43525,
        "revenue": 215.5197710000000
      },
      {
        "clicks": 54,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 20,
        "impressions": 43579,
        "revenue": 213.8766470000000
      },
      {
        "clicks": 50,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 21,
        "impressions": 42519,
        "revenue": 207.0633420000000
      },
      {
        "clicks": 48,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 22,
        "impressions": 37063,
        "revenue": 169.1746510000000
      },
      {
        "clicks": 29,
        "date": "Thu, 05 Jan 2017 00:00:00 GMT",
        "hour": 23,
        "impressions": 19992,
        "revenue": 105.1058380000000
      },
      {
        "clicks": 40,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 0,
        "impressions": 18087,
        "revenue": 84.8078360000000
      },
      {
        "clicks": 59,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 1,
        "impressions": 32617,
        "revenue": 125.4369970000000
      },
      {
        "clicks": 22,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 2,
        "impressions": 25736,
        "revenue": 74.4438110000000
      },
      {
        "clicks": 11,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 3,
        "impressions": 19339,
        "revenue": 38.6491520000000
      },
      {
        "clicks": 13,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 4,
        "impressions": 21218,
        "revenue": 47.7479600000000
      },
      {
        "clicks": 9,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 5,
        "impressions": 22531,
        "revenue": 63.4525230000000
      },
      {
        "clicks": 65,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 6,
        "impressions": 45906,
        "revenue": 248.0314750000000
      },
      {
        "clicks": 66,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 7,
        "impressions": 48250,
        "revenue": 249.0314090000000
      },
      {
        "clicks": 78,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 8,
        "impressions": 53515,
        "revenue": 280.8003440000000
      },
      {
        "clicks": 81,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 9,
        "impressions": 52715,
        "revenue": 269.3409560000000
      },
      {
        "clicks": 77,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 10,
        "impressions": 50166,
        "revenue": 253.7730060000000
      },
      {
        "clicks": 61,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 11,
        "impressions": 48047,
        "revenue": 243.0035030000000
      },
      {
        "clicks": 57,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 12,
        "impressions": 74993,
        "revenue": 269.7355090000000
      },
      {
        "clicks": 96,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 13,
        "impressions": 71068,
        "revenue": 258.4626040000000
      },
      {
        "clicks": 55,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 14,
        "impressions": 68003,
        "revenue": 251.7689310000000
      },
      {
        "clicks": 72,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 15,
        "impressions": 65106,
        "revenue": 250.6005740000000
      },
      {
        "clicks": 79,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 16,
        "impressions": 60888,
        "revenue": 235.8163120000000
      },
      {
        "clicks": 84,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 17,
        "impressions": 61449,
        "revenue": 244.7288860000000
      },
      {
        "clicks": 82,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 18,
        "impressions": 58052,
        "revenue": 243.2341800000000
      },
      {
        "clicks": 78,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 19,
        "impressions": 52004,
        "revenue": 229.9988450000000
      },
      {
        "clicks": 91,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 20,
        "impressions": 52134,
        "revenue": 230.4846730000000
      },
      {
        "clicks": 79,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 21,
        "impressions": 51259,
        "revenue": 223.9919720000000
      },
      {
        "clicks": 77,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 22,
        "impressions": 44417,
        "revenue": 189.1914210000000
      },
      {
        "clicks": 41,
        "date": "Fri, 06 Jan 2017 00:00:00 GMT",
        "hour": 23,
        "impressions": 24532,
        "revenue": 127.1229570000000
      },
      {
        "clicks": 67,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 0,
        "impressions": 20217,
        "revenue": 95.1189460000000
      },
      {
        "clicks": 60,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 1,
        "impressions": 31637,
        "revenue": 123.9998600000000
      },
      {
        "clicks": 38,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 2,
        "impressions": 27410,
        "revenue": 85.9776660000000
      },
      {
        "clicks": 6,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 3,
        "impressions": 19629,
        "revenue": 40.0719810000000
      },
      {
        "clicks": 12,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 4,
        "impressions": 19992,
        "revenue": 47.0120870000000
      },
      {
        "clicks": 8,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 5,
        "impressions": 20838,
        "revenue": 58.2720540000000
      },
      {
        "clicks": 77,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 6,
        "impressions": 43948,
        "revenue": 241.6657770000000
      },
      {
        "clicks": 98,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 7,
        "impressions": 49556,
        "revenue": 252.3126290000000
      },
      {
        "clicks": 97,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 8,
        "impressions": 60859,
        "revenue": 275.8964840000000
      },
      {
        "clicks": 94,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 9,
        "impressions": 61209,
        "revenue": 273.2124780000000
      },
      {
        "clicks": 96,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 10,
        "impressions": 59768,
        "revenue": 265.8951580000000
      },
      {
        "clicks": 81,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 11,
        "impressions": 60831,
        "revenue": 258.3778300000000
      },
      {
        "clicks": 81,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 12,
        "impressions": 61682,
        "revenue": 253.6509280000000
      },
      {
        "clicks": 79,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 13,
        "impressions": 60679,
        "revenue": 250.0681240000000
      },
      {
        "clicks": 65,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 14,
        "impressions": 59211,
        "revenue": 238.9390140000000
      },
      {
        "clicks": 74,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 15,
        "impressions": 59092,
        "revenue": 239.1331930000000
      },
      {
        "clicks": 70,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 16,
        "impressions": 57960,
        "revenue": 234.0132630000000
      },
      {
        "clicks": 84,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 17,
        "impressions": 56197,
        "revenue": 227.7702160000000
      },
      {
        "clicks": 64,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 18,
        "impressions": 56268,
        "revenue": 229.2961960000000
      },
      {
        "clicks": 70,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 19,
        "impressions": 51332,
        "revenue": 219.9699670000000
      },
      {
        "clicks": 71,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 20,
        "impressions": 53153,
        "revenue": 220.2625790000000
      },
      {
        "clicks": 60,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 21,
        "impressions": 53117,
        "revenue": 216.3960460000000
      },
      {
        "clicks": 56,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 22,
        "impressions": 46493,
        "revenue": 183.7111940000000
      },
      {
        "clicks": 39,
        "date": "Sat, 07 Jan 2017 00:00:00 GMT",
        "hour": 23,
        "impressions": 24244,
        "revenue": 113.0830980000000
      }
    ]
    poi = [
      {
        "lat": 43.6708,
        "lon": -79.3899,
        "name": "EQ Works",
        "poi_id": 1
      },
      {
        "lat": 43.6426,
        "lon": -79.3871,
        "name": "CN Tower",
        "poi_id": 2
      },
      {
        "lat": 43.0896,
        "lon": -79.0849,
        "name": "Niagara Falls",
        "poi_id": 3
      },
      {
        "lat": 49.2965,
        "lon": -123.0884,
        "name": "Vancouver Harbour",
        "poi_id": 4
      }
    ]

    # construct an instance of visualization component
    figure = GeoVisualization()


    #@figure.add_data_for_visualization
    def demo_daily():
        return click_daily

    @figure.add_data_for_visualization
    def demo_hourly():
        return str(events_hourly)


    #@figure.add_data_for_visualization
    def demo_poi():
        return poi

    figure.hour_data_plot(demo_hourly)
    #figure.daily_data_plot(demo_daily)
    #figure.geo_plot(demo_poi, demo_hourly)
