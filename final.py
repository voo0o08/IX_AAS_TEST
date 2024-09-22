'''
참고 링크 
https://wooiljeong.github.io/python/mongodb-01/

1. 1차 도금 데이터를 읽어 온다
2. AAS파일(DB_a) 내의 정보를 읽고, DB_a의 다른 collection에 저장
3. 1차 도금에 기반하여 2차 도금의 setting값을 조정
4. AAS파일(DB_b) 내의 정보를 읽고, DB_b의 다른 collection에 저장
'''
from pymongo import MongoClient
import pandas as pd
import pprint

# 데이터 불러오기 
DF = pd.read_csv('./data/sample.csv', dtype={'THK_A': float, 'TOP_A':float, 'thick1':float, 'thick2':float})

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
                    print(in_dict["idShort"], "==>", in_dict["value"])
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
        print("=================================", sm[i]["idShort"]) # "Identification", "Technical_Data"、 "Operational_Data" 반복 
        sm_name = sm[i]["idShort"]
        col_or_prop(temp_elements)
        temp_dict[sm_name] = val_dict
        val_dict = {}
    
    # mapping
    temp_dict['Operational_Data']['Measure_Thickness'] = thick
    temp_dict['Technical_Data']['Setting_Current'] = current
    temp_dict['Operational_Data']['Lot_Number'] = lot
    pprint.pprint(temp_dict)
    return temp_dict

# DF["THK_A"] DF["thick1"]
for row_idx in range(3):
    print(f"================================= row {row_idx}")
    temp_THK = mapping(THK_AAS, DF["THK_A"][row_idx], DF["thick1"][row_idx], row_idx)
    temp_TOP = mapping(TOP_AAS, DF["TOP_A"][row_idx], DF["thick2"][row_idx], row_idx)
    # # test_collection
    # post_id = test_collection.insert_one(temp_dict).inserted_id
    # print(post_id)
    post_id1 = THK_result.insert_one(temp_THK).inserted_id
    post_id2 = TOP_result.insert_one(temp_TOP).inserted_id

'''
Document 생성
:MongoDB는 data를 JSON으로 저장 
즉, 유사한 data type인 dictionary데이터를 Collection에 Document로 저장 가능 
'''
# THK_A, thick 부분을 AAS에 받아와서 변경하고 
# 데이터 형 체크하고 
# import datetime
# post = {"THK_A":THK_A[idx],
#         "thick":thick1[idx],
#         "date":datetime.datetime.now(datetime.timezone.utc)}
# print("\n======== 저장할 데이터 ========")
# print(post)

# '''
# Collecion 접근 및 Document 추가 : insert_one
# 여러개 추가할 때는 inset_many()
# '''
# post_id = test_collection.insert_one(post).inserted_id # document 추가(insert_one() 메서드 이용)
# print("\n======== post id ========")
# print(post_id)

# '''
# db 인스턴스의 list_collection_names()를 호출하여 DB에 존재하는 collectino 목록 보기
# '''
# names = db.list_collection_names()
# print("\n======== names ========")
# print(names)

