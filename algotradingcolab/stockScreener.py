from datetime import date
import importlib
from pandas.core.indexes import period
import talib    

# Stadard Python packages
import numpy as np
import pandas as pd

# # Standard plotly imports
from plotly.subplots import make_subplots
import plotly.graph_objs as go  
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Our Libraries
import config
from db.database import DataBase


## Initialize the DB
db = DataBase(config.DB_ACCESS[config.DB_LOCATION])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create the dropdown lists
db.execute("SELECT id, name, symbol from stocks")
rv = db.cursor.fetchall()

ticker_dict  = { entry[2] : entry for entry in rv}
ticker_dropdown_options = [{"label": ticker, "value" : ticker} for ticker in list(ticker_dict)]
allowable_time_frames = ["1Min"]
time_frame_dropdown_options = [{"label": time_frame, "value" : time_frame} for time_frame in allowable_time_frames]
technical_periods_dropdown_options = [{"label" : i, "value" : i} for i in range(5,500)]


app.layout = html.Div(children=[

    ## Top Section
    html.Div([
        html.H1("Stock Screener "),
        html.H3(id="company-name")
    ], style = {"textAlign" : "center"} ),
    html.Div([
        html.Div([
            html.Label("Ticker:"),
            dcc.Dropdown(
                id='ticker-dropdown',
                options=ticker_dropdown_options,
                value="AAPL"
            )], style={"width" : 100, "margin-right": "30px"}),

        html.Div([
            html.Label("Time-Frame:"),
            dcc.Dropdown(
                id='time-frame-dropdown',
                options=time_frame_dropdown_options,
                value= "1Min",
            )], style={"width" : 100, "margin-right": "30px"}),
        
        html.Div([
            html.Label("Number Of Periods:"),
            dcc.Input(
                id='num-periods-input',
                type='number',
                value=200,
                debounce=True
            )], style={"width" : 200})
    ],
    style={"columnCount" : 3, "display" : "flex", "justify-content" : "center"}),
    
    ## Graph
    html.Div(
        id="graph-container",
        children=dcc.Graph(id='quant-chart',
                           style={'height' : 650}),
        style={'backgroundColor' : 'rgba(250,250,250,1)'}
    ),

    ## Bottm Technical Analysis settings
    html.Div([
        html.Center([html.H3("Technical Analysis Settings")]),
        html.Div(
            [
                html.Div([

                    html.Div([
                        html.Label("SMA-Periods:", style={"height":40}),
                        html.Label("EMA-Periods:", style={"height":40}),
                        html.Label("Bollinger Bands Period:", style={"height":40})
                    ], style={"width" : 180}),

                    html.Div([
                        dcc.Dropdown(
                            id='sma-periods-dropdown',
                            multi = True,
                            options = technical_periods_dropdown_options,
                            value = [100]
                        ),
                        dcc.Dropdown(
                            id="ema-periods-dropdown",
                            multi = True,
                            options = technical_periods_dropdown_options,
                            value = [20]
                        ),
                        dcc.Input(
                            id='bb-bands-period-dropdown',
                            type='number',
                            value = 20,
                            debounce=True,
                        ),
                    ], style={"width" : 210})
                ],
                style={"columnCount":2, "display" : "flex", "height" : 600, "margin-right": "30px"}),

                html.Div([

                    html.Div([
                        html.Label("MACD periods:", style={"height":40}),
                        html.Label("MACD Signal Period:", style={"height":40})
                    ], style={"width" : 150}),

                    html.Div([
                        dcc.Dropdown(
                            id="macd-periods-dropdown",
                            multi = True,
                            options = technical_periods_dropdown_options,
                            value = [20, 12]
                        ),
                        dcc.Input(
                            id='macd-signal-period',
                            type='number',
                            value=9,
                            debounce=True
                        )
                    ], style={"width" : 210})
                ], style={"columnCount":2, "display" : "flex", "height" : 400  })
            ], style={"columnCount" : 2, "display" : "flex", "justify-content" : "center"})
    ])
])


@app.callback(  
    [Output('quant-chart','figure'),
     Output('company-name', 'children')],
    [Input('ticker-dropdown', 'value'),
     Input('time-frame-dropdown', 'value'),
     Input('num-periods-input', 'value'),
     Input('sma-periods-dropdown', 'value'),
     Input('ema-periods-dropdown', 'value'),
     Input('bb-bands-period-dropdown', 'value'),
     Input('macd-periods-dropdown', 'value'),
     Input('macd-signal-period', 'value')])
def update_plot(ticker : str,
                time_frame : str,
                periods : int,
                sma_periods : list[int] ,
                ema_periods : list[int] ,
                bb_band_periods: int ,    
                macd_periods: list[int] ,
                macd_signal_period : int,
                ):

    if ticker is None: ticker = "AAPL"
    if time_frame is None : time_frame = "1Day"
    if periods is None: periods = 200
    if not sma_periods: sma_periods = [100]
    if not ema_periods: ema_periods = [20]
    if bb_band_periods is None: bb_band_periods = 20
    if not macd_periods or len(macd_periods) < 2: macd_periods = [20, 12]
    if macd_signal_period is None : macd_signal_period = 9

    max_ta_periods = max(sma_periods + ema_periods + [periods, bb_band_periods, macd_signal_period] + macd_periods)


    # Get requested num of points
    sql_cmd =   f"""
                    SELECT * FROM price_minute 
                    WHERE stock_id = {ticker_dict[ticker][0]}
                    ORDER BY date_time DESC
                    LIMIT {periods + max_ta_periods }
                """
    db.execute(sql_cmd)
    rv = db.cursor.fetchall()

    data = { pd.Timestamp(p[1]) : {"o" : p[2], "h" : p[3], "l" : p[4], "c" : p[5], "v" : p[6]} for p in rv}
    df = pd.DataFrame(data.values(), data.keys())
    df.sort_index(inplace = True)
    
    # # Create the plot with all of the traces
    fig = make_subplots(rows=4, row_heights=[0.2, 0.6, 0.2, 0.2],  vertical_spacing=0, horizontal_spacing=0,  shared_xaxes=True)

    # Add to the top subplot
    dates = df.index
    rsi = talib.RSI(df.c)
    fig.add_traces(data=[go.Scatter(x=dates, y=rsi, name="RSI", line_width=0.7, showlegend=False),
                            go.Scatter(x=dates, y= [70]*len(dates), line=dict(color='black', width=0.5), showlegend=False, hoverinfo='skip'),
                            go.Scatter(x=dates, y= [30]*len(dates), line=dict(color='black', width=0.5), showlegend=False, hoverinfo='skip'),
                            go.Scatter(x=dates, y= [50]*len(dates), line=dict(color='black', width=0.5 , dash='dash'), showlegend=False, hoverinfo='skip')],
                            rows=1,
                            cols=1
                    )
  
    # # Add the the middle subplot
    bb_high, bb_mid, bb_low = talib.BBANDS(df.c, timeperiod=bb_band_periods)
    trace_data=[go.Candlestick(x=dates,open=df.o, high=df.h, low=df.l, close=df.c, name=ticker),
                go.Scatter(x=dates, y=bb_high, name="Bollinger Bands", line_width=0.5, line_color='rgba(164, 224, 248, 1)', legendgroup="bbands"),
                go.Scatter(x=dates, y=bb_low, name="low", fill='tonexty', line_width=0.5, line_color='rgba(164, 224, 248, 1)', fillcolor='rgba(164, 224, 248, 0.3)', legendgroup="bbands", showlegend=False, hoverinfo='skip'),
                go.Scatter(x=dates, y=bb_mid, name="mean", line_width = 0.5, line_color = 'rgba(164, 224, 255, 1)', legendgroup="bbands",showlegend=False, hoverinfo='skip')
                ]


    trace_data.extend([go.Scatter(x=dates, y=talib.SMA(df.c, per), name=f"SMA{per}", line_width=0.7) for per in sma_periods])
    trace_data.extend([go.Scatter(x=dates, y=talib.EMA(df.c, per), name=f"EMA{per}", line_width=0.7) for per in ema_periods])    
    fig.add_traces(data=trace_data, rows=2, cols=1)

    # # Add Volume plot
    volume_data = [go.Bar(x=dates, y=df.v, name="Volume", showlegend=False),
                   go.Scatter(x=dates, y=talib.OBV(df.c, df.v), name="OBV", line_width=0.5)]
    fig.add_traces(data=volume_data, rows=3, cols=1)

    # # # Add to the bottom subplot
    macd, macdsignal, macdhist = talib.MACD(df.c, fastperiod = min(macd_periods), slowperiod = max(macd_periods), signalperiod = macd_signal_period)
    
    gtz_mask = (macdhist > 0).to_numpy()
    ltz_mask = (macdhist <= 0).to_numpy()
    fig.add_traces(data=[go.Scatter(x=dates, y=macd, name=f"MACD({max(macd_periods)},{min(macd_periods)}, {macd_signal_period})", line_width=0.7, line_color="black", legendgroup="macd"),
                         go.Scatter(x=dates, y=macdsignal, name=f"Signal({macd_signal_period})", line_width=0.7, line_color="red", showlegend=False, legendgroup="macd"),
                         go.Bar(x=dates[gtz_mask], y=macdhist[gtz_mask], marker=dict(color='green'), showlegend=False, hoverinfo='skip'),
                         go.Bar(x=dates[ltz_mask], y=macdhist[ltz_mask], marker=dict(color='red'), showlegend=False, hoverinfo='skip')],
                         rows=4,
                         cols=1)

    fig.update_layout(
        plot_bgcolor='rgba(250,250,250,1)',
        paper_bgcolor='rgba(250,250,250,1)',
        hovermode='x unified',
        legend=dict(orientation="h", xanchor="center", y=1.1, x=0.5),
    )   


    fig.update_xaxes(rangeslider_visible=False, visible=True, range = (dates[max_ta_periods], dates[-1]))
    fig.update_yaxes(row=1, col=1, title="RSI", tickvals = [30, 50, 70])
    fig.update_yaxes(row=2, col=1, title="Share Price")
    fig.update_yaxes(row=3, col=1, title="Volume")
    fig.update_yaxes(row=4, col=1, title="MACD")



    return [fig, ticker_dict[ticker][1]]


if __name__ == '__main__':
    app.run_server(debug=True)
    
