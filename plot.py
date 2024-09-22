import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import random
import pandas as pd

# Dash 앱 초기화
app = dash.Dash(__name__)

# 가상 데이터 생성
def generate_data():
    data = {
        'time': pd.date_range(start='1/1/2022', periods=1000, freq='T'),
        'value1': [random.randint(1, 100) for _ in range(1000)],
        'value2': [random.randint(1, 100) for _ in range(1000)],
        'value3': [random.randint(1, 100) for _ in range(1000)]
    }
    return pd.DataFrame(data)

df = generate_data()

# 윈도우 크기
windowsize = 100

# 레이아웃 설정
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(id='graph1'),
            dcc.Graph(id='graph2')
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        html.Div([
            dcc.Graph(id='graph3')
        ], style={'width': '50%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'height': '100vh'})
    ], style={'display': 'flex'}),  # 여기에 콤마 추가

    dcc.Interval(
        id='interval-component',
        interval=1000,  # 1초마다 업데이트
        n_intervals=0
    )
])

# 그래프 1 업데이트 콜백
@app.callback(
    Output('graph1', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph1(n):
    start = n % (len(df) - windowsize)
    end = start + windowsize
    trace = go.Scatter(x=df['time'][start:end], y=df['value1'][start:end], mode='lines', name='Value 1')
    return {'data': [trace], 'layout': go.Layout(title='Graph 1')}

# 그래프 2 업데이트 콜백
@app.callback(
    Output('graph2', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph2(n):
    start = n % (len(df) - windowsize)
    end = start + windowsize
    trace = go.Scatter(x=df['time'][start:end], y=df['value2'][start:end], mode='lines', name='Value 2')
    return {'data': [trace], 'layout': go.Layout(title='Graph 2')}

# 그래프 3 업데이트 콜백
@app.callback(
    Output('graph3', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph3(n):
    start = n % (len(df) - windowsize)
    end = start + windowsize
    trace = go.Scatter(x=df['time'][start:end], y=df['value3'][start:end], mode='lines', name='Value 3')
    return {'data': [trace], 'layout': go.Layout(title='Graph 3')}

# 앱 실행
if __name__ == '__main__':
    app.run_server(debug=True)
