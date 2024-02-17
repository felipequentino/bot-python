from pymongo import MongoClient
from random import randint

class Dbconnection:

    def __init__(self):
        self.connection_string = ("mongodb+srv://felipequentino:159753852f@cluster0.xczbmrd.mongodb.net/?retryWrites=true&w=majority")
        self.client = MongoClient(self.connection_string)
        self.db = self.client.get_database("bot")
        self.records = self.db.users
        self.cards = self.db.cards
        self.id_value = self.db.id_value

    def get_users(self):
        return self.records.find()

    def get_user(self, id):
        user = self.records.find_one({"id": id})
        if user:
            return user.get("name")
        else:
            return None

    def add_card(self, obra, nome, link, id):
        card = {
            "obra": obra,
            "nome": nome,
            "link": link,
            "id": id
        }
        self.cards.insert_one(card)

    def add_user(self, id, name, data):
        user = {
            "id": id,
            "name": name,
            "data": data,
            "colecao": []
        }
        existing_user = self.records.find_one({"id": id})
        if not existing_user:
            self.records.insert_one(user)  # Passando 'user' diretamente como o documento
            print("Usuário adicionado.")
        else:
            print("Usuário já existente.")

    def get_random_photo(self):
        document = self.id_value.find_one({"nome": "name"})
        max_id = int(document.get("photo_id")) - 1
        print(max_id)
        random_number = str(randint(1, max_id))
        photo = self.cards.find_one({"id": random_number})
        return photo

""" records = db.users

print(records.count_documents({}))

new_user = {
    "name": "Felipe",
    "age": 20,
    "id":"50"
}

records.insert_one(new_user)

new_users = [
    {
        "name": "Davi",
        "age": 21,
        "id":"123456789"
    },
    {
        "name": "João",
        "age": 22,
        "id":"123456789"
    },
    {
        "name": "Maria",
        "age": 23,
        "id":"123456789"
    }
]

records.insert_many(new_users)

# find documents

print(list(records.find()))

print()

print(records.find_one({"name": "Felipe"}))

#update documents

user_updates = {
    "name": "Bellingham",
}
records.update_one({"id": "50"}, {"$set": user_updates})
print(records.find_one({"id": "50"}))

# delete documents
#records.delete_one({"id": "50"}) """
