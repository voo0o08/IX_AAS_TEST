'''
mongoDB 내의 AAS에서 원하는 값 찾기 
근데 생각해보니 AAS파일이 한 collection안에 하나의 document로 정의됨 
'''
from pymongo import MongoClient

'''
DB 연결 : Mongo Client 
방법1. 서버 URL 입력
방법2. localhost 입력
'''
client = MongoClient(host='localhost', port=27017)

print(client.list_database_names()) # ['admin', 'config', 'local', 'nodejs']

'''
DB 접근 
방법1. 메서드 형태 (db = client.mydb)
방법2. Dictionary 형태 (db = client['mydb'])
'''
db = client['mydb']

'''
Collection=Table 접근
'''
collection = db['THK_AASX'] # 컬렉션에 접근
# 모든 문서를 가져옴
# documents = collection.find()

# 모든 문서를 출력
# for document in documents:
#     print(document)


# '''
# db 인스턴스의 list_collection_names()를 호출하여 DB에 존재하는 collection 목록 보기
# '''
# names = db.list_collection_names()
# print("\n======== names ========")
# print(names)

'''
단일 Document 조회 : find_one()메서드 이용
SQL의 Where 구문과 같이 특정 요소 필터링 가능 
여러개 조회할 때는 find()메서드 이용 
'''
print()
import pprint
# pprint.pprint(collection.find_one())
# pprint.pprint(collection.find({"submodels": {"$exists": True}})) # 쿼리를 통한 Documents 조회
# for doc in collection.find({"submodels": {"$exists": True}}): # find를 이용한 여러개 조회 
#     print("==================================================================")
#     pprint.pprint(doc)
#     print(type(doc))

# 쿼리
document = collection.find_one({"submodels": {"$exists": True}})
# print(document.keys()) # dict_keys(['_id', 'assetAdministrationShells', 'submodels', 'conceptDescriptions'])

# pprint.pprint(document)

sm = document["submodels"]
# sm_idShorts = ["Identification", "Technical_Data", "Operational_Data"]
# pprint.pp(sm[2])


def col_or_prop(in_list):
    for in_dict in in_list:
        if isinstance(in_dict, dict):  # in_dict가 딕셔너리인지 확인
            if in_dict.get("modelType") == "Property":
                if "value" in in_dict.keys():
                    # 아아아아ㅏ아아아악 
                    print(in_dict["idShort"], "==>", in_dict["value"])
            elif in_dict.get("modelType") == "SubmodelElementCollection":
                if isinstance(in_dict["value"], list):  # value가 리스트인지 확인
                    col_or_prop(in_dict["value"])
        else:
            print("Unexpected data format:", in_dict)

for i in range(len(sm)):
    temp_elements = sm[i]["submodelElements"]
    col_or_prop(temp_elements)
    
    # for j in range(len(temp_elements)):
    #     if temp_elements[j]["modelType"] == "Property":
    #         print(temp_elements[j]["idShort"], "==>", temp_elements[j]["value"])
    #     elif temp_elements[j]["modelType"] == "SubmodelElementCollection": # collection이라 더 타고 들어가야함 
    #         for val_list in temp_elements[j]["value"]:
    #             print(val_list["idShort"], "==>", val_list["value"])




# Technical_Data = sm[1]
# pprint.pprint(Technical_Data["submodelElements"][0]["value"][0])





# for match in collection.find({ "submodels.0.submodelElements" : {"$exists": True} }):
#      print(match)


# pprint.pprint(post_collection.find_one({"_id": post_id}))
# print(type(post_id)) # <class 'bson.objectid.ObjectId'>
# print()
# for doc in collection.find({"author":"Mike"}): # find를 이용한 여러개 조회 
#     pprint.pprint(doc)