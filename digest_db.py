import pymongo
import itertools

def removeDuplicates(database, collection_name, duplicate_col="ID"):
    collection = database[collection_name]
    print(f"Number of documents in {collection_name} before removing duplicates:", collection.count_documents({}))

    index_uuid = pymongo.IndexModel(
        [
            (duplicate_col, pymongo.ASCENDING)
        ],
    )

    collection.create_indexes([index_uuid])
    pipeline = [
        {"$sort": {"ID":1}},
        {
            "$group": {
                "_id": f"${duplicate_col}",
                "dups": {"$addToSet": "$_id"},
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {"count": {"$gt": 1}}
        },
    ]

    it_cursor = collection.aggregate(
        pipeline, allowDiskUse=True
    )

    dups = list(itertools.chain.from_iterable(map(lambda x: x["dups"][1:], it_cursor)))
    collection.delete_many({"_id":{"$in": dups}})
    collection.drop_index(f"{duplicate_col}_1")

    print(f"Number of documents in {collection_name} after removing duplicates:", collection.count_documents({}))

des_connection_url = "mongodb+srv://damanh1211:AH8Gos6j2TQqakoD@foodycluster.brwq9u2.mongodb.net/"
des_client = pymongo.MongoClient(des_connection_url)
des_foody_db = des_client["foody"]

for collection_name in des_foody_db.list_collection_names():
    print("#"*20)
    removeDuplicates(des_foody_db, collection_name)