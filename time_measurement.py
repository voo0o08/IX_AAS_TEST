'''
데이터 저장 시간 측정 
'''

# mongodb관련 import 
from pymongo import MongoClient
import pandas as pd
import pprint
import time
start = time.time()

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


THK_DICT = {}
TOP_DICT = {}

val_dict = {}
def col_or_prop(in_list):
    '''collection인지 property인지 분해하는 내용'''
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
    
    
def dict_definition(collection,):
    # 쿼리
    global val_dict
    
    document = collection.find_one({"submodels": {"$exists": True}})
    # print(document.keys()) # dict_keys(['_id', 'assetAdministrationShells', 'submodels', 'conceptDescriptions'])
    sm = document["submodels"]
    # sm_idShorts = ["Identification", "Technical_Data", "Operational_Data"]

    temp_dict = {} # 최상단 "Identification", "Technical_Data", "Operational_Data"
    
    for i in range(len(sm)):
        # print(sm[i]["submodelElements"])
        temp_elements = sm[i]["submodelElements"] 
        # print("=================================", sm[i]["idShort"]) # "Identification", "Technical_Data"、 "Operational_Data" 반복 
        sm_name = sm[i]["idShort"]
        col_or_prop(temp_elements)
        temp_dict[sm_name] = val_dict
        val_dict = {}
    return temp_dict
        
    

def mapping(base_dict, current, thick, lot):
    """ 기초 사전에 값을 매핑하고 새로운 사전을 반환하는 함수 """
    new_dict = {key: value.copy() for key, value in base_dict.items()}
    new_dict['Operational_Data']['Measure_Thickness'] = thick
    new_dict['Technical_Data']['Setting_Current'] = current
    new_dict['Operational_Data']['Lot_Number'] = lot
    return new_dict

# ========================================= main문 
for row_idx in range(10): # len(DF)
    
    if row_idx == 0:
        a = time.time()
        THK_DICT = dict_definition(THK_AAS) # mapping(AAS, current, thick, lot)
        TOP_DICT = dict_definition(TOP_AAS)
        b = time.time()
        print(b-a)

    # print(f"================================= row {row_idx}")
    # mapping함수를 통한 document 생성
    map_time1 = time.time()
    temp_THK = mapping(THK_DICT, DF["THK_A"][row_idx], DF["thick1"][row_idx], row_idx) # mapping(AAS, current, thick, lot)
    temp_TOP = mapping(TOP_DICT, DF["TOP_A"][row_idx], DF["thick2"][row_idx], row_idx)
    map_time2 = time.time()
    print(f"mapping에 걸리는 시간{map_time2-map_time1}")
    # print("------------------------------")
    # print(temp_TOP)
    # # test_collection
    # post_id = test_collection.insert_one(temp_dict).inserted_id
    # print(post_id)
    insert_time1 = time.time()
    post_id1 = THK_result.insert_one(temp_THK).inserted_id
    post_id2 = TOP_result.insert_one(temp_TOP).inserted_id
    insert_time2 = time.time()
    print(f"insert에 걸리는 시간{insert_time2-insert_time1}")
    print()
    

print("end")
end = time.time()
# print(f"실행 시간 => {end - start:.5f} sec")
    
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



