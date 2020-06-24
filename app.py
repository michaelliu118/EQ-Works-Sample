from flask import Flask,jsonify
import sqlalchemy
from RateLimiter import RateLimiter
from UICOMPONENTS import DataVisualization as ui
from UICOMPONENTS import GeoVisualization as Geo

app = Flask(__name__)
ctx = app.app_context()
ctx.push()
rl_index = RateLimiter(5)
rl_eh = RateLimiter(5)
rl_ed = RateLimiter(5)
rl_sh = RateLimiter(5)
rl_sd = RateLimiter(5)
rl_poi = RateLimiter(5)
figure = ui()
geo = Geo()

# database engine
engine = sqlalchemy.create_engine('postgresql://readonly:w2UIO@#bg532!@work-samples-db.cx4wctygygyq.us-east-1.rds.amazonaws.com:5432/work_samples')
def queryHelper(query):
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return jsonify([dict(row.items()) for row in result])

@app.route('/')
@rl_index.request
def index():
    return 'welcome eq works'

@app.route('/events/hourly')
@figure.hour_data_plot
@geo.add_data_for_visualization
@figure.add_data_for_visualization
def events_hourly():
    return queryHelper('''
        SELECT *
        FROM public.hourly_events
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/events/daily')
@figure.daily_data_plot
@figure.add_data_for_visualization
def events_daily():
    return queryHelper('''
        SELECT date, SUM(events) AS events
        FROM public.hourly_events
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')


@app.route('/stats/hourly')
@figure.hour_data_plot
@figure.add_data_for_visualization
@rl_sh.request
def stats_hourly():
    return queryHelper('''
        SELECT clicks, date,hour,impressions,poi_id, CAST(revenue AS int)
        FROM public.hourly_stats
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/stats/daily')

@rl_sd.request
def stats_daily():
    return queryHelper('''
        SELECT date,
            SUM(impressions) AS impressions,
            SUM(clicks) AS clicks,
            SUM(revenue) AS revenue
        FROM public.hourly_stats
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')
@geo.add_data_for_visualization
def poi():
    return queryHelper('''
        SELECT *
        FROM public.poi;
    ''')

fig = geo.geo_plot(poi, events_hourly)
@app.route('/poi')
def poi_func():
    return fig

import webbrowser

webbrowser.open("http://127.0.0.1:5000/")
app.run(debug=True)