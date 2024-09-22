'''
final+plot
'''

# mongodb관련 import 
from pymongo import MongoClient
import pandas as pd
import pprint

# 그래프 관련 import 
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
# =============================================== Dash 앱 초기화

# ===============================================


# 데이터 불러오기 
DF = pd.read_csv('./data/sample2.csv', dtype={'THK_A': float, 'TOP_A':float, 'thick1':float, 'thick2':float})

# THK_A = DF["THK_A"]
# TOP_A = DF["TOP_A"]
# thick1 = DF["thick1"] # THK_A랑 쌍
# thick2 = DF["thick2"] # TOP_A랑 쌍 
idx = 0

'''
DB 연결 : Mongo Client 
'''
client = MongoClient(host='localhost', port=27017)
# print(client.list_database_names()) # ['admin', 'config', 'local', 'nodejs']
'''
DB 접근
'''
db = client['mydb']

'''
Collection=Table 접근
'''
test_collection = db['test']

THK_AAS = db['THK_AASX'] # THK사 AAS collection에 접근
TOP_AAS = db["TOP_AASX"] # TOP사 AAS collection에 접근
THK_result = db["THK_result"] # THK 결과 저장 collecton
TOP_result = db["TOP_result"] # TOP 결과 저장 collection

val_dict = {}
def col_or_prop(in_list):
    global val_dict
    # ["Identification", "Technical_Data", "Operational_Data"]가 이 함수를 통해 한번씩 들어옴 
    for in_dict in in_list:
        if isinstance(in_dict, dict):  # in_dict가 딕셔너리인지 확인
            if in_dict.get("modelType") == "Property":
                if "value" in in_dict.keys():
                    # 아아아아ㅏ아아아악 
                    # print(in_dict["idShort"], "==>", in_dict["value"])
                    val_dict[in_dict["idShort"]] = in_dict["value"]
            elif in_dict.get("modelType") == "SubmodelElementCollection":
                if isinstance(in_dict["value"], list):  # value가 리스트인지 확인
                    col_or_prop(in_dict["value"])
        else:
            print("Unexpected data format:", in_dict)
    
            
def mapping(collection, current, thick, lot):
    # 쿼리
    global val_dict
    document = collection.find_one({"submodels": {"$exists": True}})
    # print(document.keys()) # dict_keys(['_id', 'assetAdministrationShells', 'submodels', 'conceptDescriptions'])
    sm = document["submodels"]
    # sm_idShorts = ["Identification", "Technical_Data", "Operational_Data"]

    temp_dict = {} # 최상단 "Identification", "Technical_Data"、 "Operational_Data"
    for i in range(len(sm)):
        # print(sm[i]["submodelElements"])
        temp_elements = sm[i]["submodelElements"] 
        # print("=================================", sm[i]["idShort"]) # "Identification", "Technical_Data"、 "Operational_Data" 반복 
        sm_name = sm[i]["idShort"]
        col_or_prop(temp_elements)
        temp_dict[sm_name] = val_dict
        val_dict = {}
    
    # mapping
    temp_dict['Operational_Data']['Measure_Thickness'] = thick
    temp_dict['Technical_Data']['Setting_Current'] = current
    temp_dict['Operational_Data']['Lot_Number'] = lot
    # pprint.pprint(temp_dict)
    return temp_dict

def read_db():
    pass 

for row_idx in range(len(DF)):
    pass
    # print(f"================================= row {row_idx}")
    # mapping함수를 통한 document 생성
    # temp_THK = mapping(THK_AAS, DF["THK_A"][row_idx], DF["thick1"][row_idx], row_idx)
    # temp_TOP = mapping(TOP_AAS, DF["TOP_A"][row_idx], DF["thick2"][row_idx], row_idx)
    # # # test_collection
    # # post_id = test_collection.insert_one(temp_dict).inserted_id
    # # print(post_id)
    # post_id1 = THK_result.insert_one(temp_THK).inserted_id
    # post_id2 = TOP_result.insert_one(temp_TOP).inserted_id
    
print("end")
    
# DB에서 데이터 불러오기 
# Operational_Data 안의 Lot_num만 조회
query = {}
projection = {'Operational_Data.Lot_Number': 1, 'Operational_Data.Measure_Thickness': 1, '_id': 0, 'Technical_Data.Setting_Current':1}  # Lot_num 필드만을 가져오고, _id는 제외

THK_docs = THK_result.find(query, projection)
TOP_docs = TOP_result.find(query, projection)

# 결과 출력
def df_out(docs):
    Setting_Current = []
    Lot_Number = []
    Measure_Thickness = []
    for doc in docs:
       Setting_Current.append(doc['Technical_Data']['Setting_Current'])
       Lot_Number.append(doc['Operational_Data']['Lot_Number'])
       Measure_Thickness.append(doc['Operational_Data']['Measure_Thickness'])

    data = {
        'Setting_Current': Setting_Current,
        'Lot_Number': Lot_Number,
        'Measure_Thickness': Measure_Thickness,
    }
    # print(data)
    df = pd.DataFrame(data)
    return df

THK_df = df_out(THK_docs)
TOP_df = df_out(TOP_docs)

# print(THK_df)
    
    
    
# ==================================================================== 그래프 그리기 
windowsize = 100
# 그래프 1 업데이트 콜백
# 그래프 1과 그래프 2 업데이트 콜백
line_num = 10  # 예시 값, 필요에 따라 수정

# Dash 앱 초기화
app = dash.Dash(__name__)

# 레이아웃 설정
app.layout = html.Div([
    html.Div([
        dcc.Graph(id='graph1', style={'height': '45vh'}),
        dcc.Graph(id='graph2', style={'height': '45vh'})
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    html.Div([
        dcc.Graph(id='graph3', style={'height': '90vh'})
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'middle', 'text-align': 'center'}),
    
    dcc.Interval(
        id='interval-component',
        interval=500,  # 1초마다 업데이트
        n_intervals=0
    )
])

def draw_side_view(idx, thick_list1, thick_list2):
    y_center = 30
    core_thick = 10
    thick1 = thick_list1[idx]
    thick2 = thick_list2[idx]

    fig = go.Figure()

    top = y_center + core_thick
    bottom = y_center - core_thick

    # core부
    fig.add_shape(type="rect", x0=0, x1=line_num, y0=bottom, y1=top,
                  fillcolor="black", opacity=1, line_width=0)

    # 1차 도금
    fig.add_shape(type="rect", x0=0, x1=line_num, y0=top, y1=top + thick1,
                  fillcolor="yellow", opacity=1, line_width=0)

    fig.add_shape(type="rect", x0=0, x1=line_num, y0=bottom - thick1, y1=bottom,
                  fillcolor="yellow", opacity=1, line_width=0)
    top = y_center + core_thick + thick1
    bottom = y_center - core_thick - thick1

    # 접착제부
    fig.add_shape(type="rect", x0=0, x1=line_num, y0=top, y1=top + core_thick,
                  fillcolor="lightgray", opacity=1, line_width=0)
    fig.add_shape(type="rect", x0=0, x1=line_num, y0=bottom - core_thick, y1=bottom,
                  fillcolor="lightgray", opacity=1, line_width=0)
    top += core_thick
    bottom -= core_thick

    # 2차 도금
    fig.add_shape(type="rect", x0=0, x1=line_num, y0=top, y1=top + thick2,
                  fillcolor="yellow", opacity=1, line_width=0)

    fig.add_shape(type="rect", x0=0, x1=line_num, y0=bottom - thick2, y1=bottom,
                  fillcolor="yellow", opacity=1, line_width=0)

    fig.update_layout(
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='Thickness (micrometers)',
            range=[0, 70],
            showgrid=True,
        ),
        template='plotly_white'
    )

    return fig

# 그래프 1과 그래프 2, 그래프 3 업데이트 콜백
@app.callback(
    [Output('graph1', 'figure'), Output('graph2', 'figure'), Output('graph3', 'figure')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    # 그래프 1 데이터 (THK_df)
    start_thk = n % (len(THK_df) - windowsize)
    end_thk = start_thk + windowsize
    trace1_thk = go.Scatter(
        x=THK_df['Lot_Number'][start_thk:end_thk],
        y=THK_df['Setting_Current'][start_thk:end_thk],
        mode='lines',
        name='Setting_Current'
    )
    trace2_thk = go.Scatter(
        x=THK_df['Lot_Number'][start_thk:end_thk],
        y=THK_df['Measure_Thickness'][start_thk:end_thk],
        mode='lines',
        name='Measure_Thickness',
        yaxis='y2'
    )
    layout_thk = go.Layout(
        title='Graph 1 - Setting Current & Measure Thickness (THK)',
        yaxis=dict(title='Setting Current'),
        yaxis2=dict(
            title='Measure Thickness',
            overlaying='y',
            side='right'
        )
    )
    figure1 = {'data': [trace1_thk, trace2_thk], 'layout': layout_thk}

    # 그래프 2 데이터 (TOP_df)
    start_top = n % (len(TOP_df) - windowsize)
    end_top = start_top + windowsize
    trace1_top = go.Scatter(
        x=TOP_df['Lot_Number'][start_top:end_top],
        y=TOP_df['Setting_Current'][start_top:end_top],
        mode='lines',
        name='Setting_Current'
    )
    trace2_top = go.Scatter(
        x=TOP_df['Lot_Number'][start_top:end_top],
        y=TOP_df['Measure_Thickness'][start_top:end_top],
        mode='lines',
        name='Measure_Thickness',
        yaxis='y2'
    )
    layout_top = go.Layout(
        title='Graph 2 - Setting Current & Measure Thickness (TOP)',
        yaxis=dict(title='Setting Current'),
        yaxis2=dict(
            title='Measure Thickness',
            overlaying='y',
            side='right'
        )
    )
    figure2 = {'data': [trace1_top, trace2_top], 'layout': layout_top}

    # figure1과 figure2의 마지막 데이터를 바탕으로 figure3 생성
    thick_list1 = THK_df['Measure_Thickness'].tolist()
    thick_list2 = TOP_df['Measure_Thickness'].tolist()

    idx_thk = end_thk - 1
    idx_top = end_top - 1

    # figure3은 figure1과 figure2의 마지막 데이터 인덱스를 바탕으로 그림
    figure3 = draw_side_view(idx_thk, thick_list1, thick_list2)

    return figure1, figure2, figure3

# 앱 실행
if __name__ == '__main__':
    app.run_server(debug=True)

