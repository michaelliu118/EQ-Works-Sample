import os
from flask import Flask, jsonify
import sqlalchemy
from RateLimiter import RateLimiter
#from UICOMPONENTS import DataVistualization as ui

app = Flask(__name__)
rl_index = RateLimiter(5)
rl_eh = RateLimiter(5)
rl_ed = RateLimiter(5)
rl_sh = RateLimiter(5)
rl_sd = RateLimiter(5)
rl_poi = RateLimiter(5)


# database engine
engine = sqlalchemy.create_engine(os.getenv('SQL_URI'))


@app.route('/')
@rl_index.request
def index():
    return 'Welcome to EQ Works'


@app.route('/events/hourly')
@rl_eh.request
def events_hourly():
    return queryHelper('''
        SELECT date, hour, events
        FROM public.hourly_events
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/events/daily')
@rl_ed.request
def events_daily():
    return queryHelper('''
        SELECT date, SUM(events) AS events
        FROM public.hourly_events
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')


@app.route('/stats/hourly')
@rl_sh.request
def stats_hourly():
    return queryHelper('''
        SELECT date, hour, impressions, clicks, revenue
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

@app.route('/poi')
@rl_poi.request
def poi():
    return queryHelper('''
        SELECT *
        FROM public.poi;
    ''')

def queryHelper(query):
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return jsonify([dict(row.items()) for row in result])