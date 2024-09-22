'''
mongoDB 모듈 test
참고 링크 
https://wooiljeong.github.io/python/mongodb-01/
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
DB 접근과 마찬가지로 db.myCol or db['myCol']
'''
collection = db['myCol']

'''
Document 생성
:MongoDB는 data를 JSON으로 저장 
즉, 유사한 data type인 dictionary데이터를 Collection에 Document로 저장 가능 
'''
import datetime
post = {"author":"Mike",
        "text":"My first blog post",
        "tags":["mongodb", "python", "pymongo"],
        "date":datetime.datetime.now(datetime.timezone.utc)}
print("\n======== 저장할 데이터 ========")
print(post)

'''
Collecion 접근 및 Document 추가 : insert_one
여러개 추가할 때는 inset_many()
'''
post_collection = db.posts # 컬렉션에 접근
post_id = post_collection.insert_one(post).inserted_id # document 추가(insert_one() 메서드 이용)
print("\n======== post id ========")
print(post_id)

'''
db 인스턴스의 list_collection_names()를 호출하여 DB에 존재하는 collectino 목록 보기
'''
names = db.list_collection_names()
print("\n======== names ========")
print(names)

'''
단일 Document 조회 : find_one()메서드 이용
SQL의 Where 구문과 같이 특정 요소 필터링 가능 
여러개 조회할 때는 find()메서드 이용 
'''
print()
import pprint
pprint.pprint(post_collection.find_one())
pprint.pprint(post_collection.find_one({"author": "Mike"})) # 쿼리를 통한 Documents 조회

# pprint.pprint(post_collection.find_one({"_id": post_id}))
# print(type(post_id)) # <class 'bson.objectid.ObjectId'>
print()
for doc in post_collection.find({"author":"Mike"}): # find를 이용한 여러개 조회 
    pprint.pprint(post)