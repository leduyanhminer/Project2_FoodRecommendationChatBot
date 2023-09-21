from pymongo import MongoClient
from prettytable import PrettyTable

# Kết nối tới MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['rasa']  # Tên database
collection = db['tracker']  # Tên collection

# Tạo bảng
table = PrettyTable()
table.field_names = ["Number", "Text", "Intent", "Confidence", "Bot Action"]

# Truy vấn dữ liệu từ collection
cursor = collection.find()

# Lặp qua các bản ghi và trích xuất thông tin
for index, document in enumerate(cursor, start=1):
    events = document['events']
    status = 0
    for event in events:
        if event['event'] == 'user' and status%2 == 0:
            user_message = event['text']
            intent = None
            confidence = None
            intent = event.get('parse_data', {}).get('intent', {}).get('name')
            confidence = event.get('parse_data', {}).get('intent', {}).get('confidence')
            status += 1
        if event['event'] == 'action' and status%2 == 1:
            if 'name' in event and event['name'] != 'action_listen':
                bot_action = None
                bot_action = event['name']
                status += 1
        if status == 2:
            table.add_row([index, user_message, intent, confidence, bot_action])
            status = 0


# In ra bảng
print(table)
