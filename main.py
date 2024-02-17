import datetime
import re

import telebot
import time
from bson import ObjectId

from raw import Dbconnection

mongo = Dbconnection()
user_collections = mongo.db.users

TOKEN = "6552472055:AAHZN1OsX4YkLb5FZ2Ltt8bU7ILNPd-tYq0"
bot = telebot.TeleBot(TOKEN)

vetor_vazio = []


def registro(mensagem):
    user_id = mensagem.from_user.id
    user = mongo.db.users.find_one({"id": user_id})
    return user


def verificacao(mensagem):
    # verificar se o usuário é um usuário do sistema
    user_id = mensagem.from_user.id
    user = mongo.db.users.find_one({"id": user_id})
    if user is None:
        bot.send_message(mensagem.chat.id,
                         "Você não está cadastrado no sistema. Utilize o comando /add_user para ser cadastrado.")
        return False
    else:
        return True


@bot.message_handler(commands=["help"])
def help(mensagem):
    bot.send_message(mensagem.chat.id,
                     "Lista de comandos:\n/add_user - Adicionar você como usuário do "
                     "sistema. OBRIGATÓRIO PARA REALIZAR QUALQUER OUTRO COMANDO\n\n/colec - Permite visualizar os personagens que você possui\n/card - "
                     "Pesquisa pelo nome do personagem\n/id - Pesquise por personagens usando seu ID\n/cards - Pesquise uma obra "
                     "inclusa no bot, com resultados em forma de lista\n/giro - Gire a roleta para ganhar uma "
                     "carta\n/trocar - Troque cartas com outros usuários\n/help - Lista de comandos")

@bot.message_handler(commands=["card"])
def card(mensagem):
    verificar = verificacao(mensagem)
    if not verificar:
        return
    elif mensagem.text.startswith('/card '):
        nome1 = mensagem.text[len('/card '):]

        nome = list(mongo.db.cards.find({"nome": re.compile(nome1, re.IGNORECASE)}))
        if len(list(nome)) == 0:
            bot.reply_to(mensagem, "Personagem não existente. Certifique-se de que você digitou o nome do "
                                   "personagem com os acentos.")
        else:
            nome_correto = nome[0].get("nome")
            nome_correto = list(mongo.db.cards.find({"nome": nome_correto}))
            bot.send_message(mensagem.chat.id, f"Esses são os cards do personagem: {nome1}")
            for i in nome_correto:
                bot.send_photo(mensagem.chat.id, i.get("link"))
                bot.send_message(mensagem.chat.id,
                                 f"Obra: {i.get('obra')}\nNome: {i.get('nome')}\nID: {i.get('id')}")
    else:
        bot.reply_to(mensagem, 'Você digitou apenas /card, por favor, digite /card nome_do_personagem.')
@bot.message_handler(commands=["cards"])
def cards(mensagem):
    verificar = verificacao(mensagem)
    if not verificar:
        return
    elif mensagem.text.startswith('/cards '):
        obra1 = mensagem.text[len('/cards '):]

        obra = list(mongo.db.cards.find({"obra": re.compile(obra1, re.IGNORECASE)}))
        if len(list(obra)) == 0:
            bot.reply_to(mensagem, "Coleção não existente. Certifique-se de que você digitou o nome da obra "
                                   "com os acentos.")
        else:
            nome_correto = obra[0].get("obra")
            obra_correta = list(mongo.db.cards.find({"obra": nome_correto}))
            bot.send_message(mensagem.chat.id, f"Esses são os cards da coleção: {nome_correto}")
            for i in obra_correta:
                bot.send_photo(mensagem.chat.id, i.get("link"))
                bot.send_message(mensagem.chat.id,
                                 f"Personagem: {i.get('nome')}\nID: {i.get('id')}")
    else:

        bot.reply_to(mensagem, 'Você digitou apenas /cards, por favor, digite /cards nome_da_obra.')


@bot.message_handler(commands=['id'])
def handle_card_command(message):
    verificao = verificacao(message)
    if not verificao:
        return
    # Verifica se a mensagem contém um argumento após o comando /card
    elif message.text.startswith('/id '):
        carta_id = message.text[len('/id '):]
        card = mongo.db.cards.find_one({"id": carta_id})
        if card is None:
            bot.reply_to(message, "ID de carta não existente.")
        else:
            bot.send_photo(message.chat.id, card.get("link"))
            bot.send_message(message.chat.id,
                             f"Obra: {card.get('obra')}\nPersonagem: {card.get('nome')}\nID: {card.get('id')}")
    else:

        bot.reply_to(message, 'Você digitou apenas /id, por favor, digite /id id_da_carta.')


@bot.message_handler(commands=["add_user"])
def add_user(mensagem):
    # Check if the message is from a user (not a bot or system message)
    if mensagem.from_user is None:
        bot.send_message(mensagem.chat.id, "Esse comando só pode ser usado por usuários individuais.")
        return

    # Obtém o ID do usuário do Telegram
    user_id = mensagem.from_user.id
    name = mensagem.from_user.first_name
    data = datetime.datetime.now()

    if user_collections.find_one({"id": user_id}):
        bot.send_message(mensagem.chat.id, f"Usuário {user_id}, {name} já existente no banco de dados.")
    else:
        mongo.add_user(user_id, name, data)
        bot.send_message(mensagem.chat.id, f"Usuário {user_id}, {name} adicionado ao banco de dados.")


@bot.message_handler(commands=["add_card"])
def add_card(message):
    verificao = verificacao(message)
    if not verificao:
        return
    else:
        user_id = message.from_user.id
        msg = bot.send_message(user_id, "Envie os dados da carta no formato: Obra;Personagem;Link_da_Imagem")
        bot.register_next_step_handler(msg,
                                       capture_card_data)  # After this message, the bot will execute capture_card_data


def capture_card_data(message):
    user_id = message.from_user.id
    data = message.text.split(";")

    if len(data) != 3:
        bot.send_message(user_id, "Por favor, envie os dados no formato correto: Obra;Personagem;Link_da_Imagem")
        return

    document = mongo.db.id_value.find_one({"nome": "name"})
    img_id = document.get("photo_id")
    id_int = int(img_id) + 1
    id_int = str(id_int)
    # Update photo_id
    mongo.db.id_value.update_one({"nome": "name"}, {"$set": {"photo_id": id_int}})

    obra, name, img_link = data
    mongo.add_card(obra, name, img_link, img_id)
    bot.send_photo(user_id, img_link,
                   caption=f"Carta adicionada com sucesso!\nObra: {obra}\nPersonagem: {name}\nID: {img_id}")


def random():
    photo = mongo.get_random_photo()
    return photo


@bot.message_handler(commands=["giro"])
def giro(mensagem):
    verificar = verificacao(mensagem)
    if not verificar:
        return
    else:
        total_photos = mongo.db.cards.count_documents({})  # Get total number of photos
        user_id = mensagem.from_user.id
        user = mongo.db.users.find_one({"id": user_id})

        if len(user.get("colecao")) == total_photos:  # Check if user has all photos
            bot.send_message(mensagem.chat.id, "Você já possui todas as cartas disponíveis.")
        else:
            photo = random()
            while photo.get("id") in user.get("colecao"):
                photo = random()

            bot.send_photo(mensagem.chat.id, photo.get("link"))
            bot.send_message(mensagem.chat.id, f"Obra: {photo.get('obra')}\nPersonagem: {photo.get('nome')}")
            mongo.db.users.update_one({"id": user_id}, {"$push": {"colecao": photo.get("id")}})
            bot.send_message(mensagem.chat.id, "Carta adicionada a sua coleção.")


@bot.message_handler(commands=["trocar"])
def trocar_cards(mensagem):
    verificar = verificacao(mensagem)
    if not verificar:
        return
    else:
        # Trocar cartas
        user_id = mensagem.from_user.id
        texto = bot.send_message(user_id,
                                 "Envie o ID da carta que deseja receber, e o ID da carta que você dará na troca "
                                 "RESPECTIVAMENTE!\n"
                                 "Envie os ID's separados por ponto e vírgula, exemplo: 9999;1111 .")
        bot.register_next_step_handler(texto, get_card_troca)


def get_card_troca(mensagem):
    user_id = mensagem.from_user.id
    texto = mensagem.text.split(";")
    if len(texto) != 2:
        bot.send_message(user_id, "Por favor, envie os dados no formato correto: "
                                  "ID_da_carta_que_você_quer;ID_da_carta_que_você_dará")
        return
    id1, id2 = texto

    if id1 == id2:
        bot.send_message(user_id, "Você não pode trocar uma carta por ela mesma.")
        return
    card1 = mongo.db.cards.find_one({"id": id1})
    card2 = mongo.db.cards.find_one({"id": id2})
    bot.send_message(user_id,
                     f"Essa é a carta que você deseja:\nObra: {card1.get('obra')}\nPersonagem: {card1.get('nome')}\nID: {card1.get('id')}")
    bot.send_photo(user_id, card1.get("link"))
    # Verificar se o usuário possui a carta que ele dará em troca
    user = mongo.db.users.find_one({"id": user_id})
    if id2 not in user.get("colecao"):
        bot.send_message(user_id, "Você não possui a carta que deseja dar em troca.")
        return
    elif id1 in user.get("colecao"):
        bot.send_message(user_id, "Você já possui a carta que deseja receber.")
    else:
        bot.send_message(user_id,
                         f"Essa é a carta que você possui:\nObra: {card2.get('obra')}\nPersonagem: {card2.get('nome')}\nID: {card2.get('id')} ")
        bot.send_photo(user_id, card2.get("link"))
        bot.send_message(user_id, "Estes usuários tem a carta que você deseja:\n")
        get_card_owners(mensagem, id1, id2)


def get_card_owners(mensagem, id1, id2):
    user_id = mensagem.from_user.id
    user_owners = list(mongo.db.users.find({"colecao": {"$in": [id1]}}))
    contd = len(list(user_owners))
    if contd == 0:
        bot.send_message(user_id, "Nenhum usuário possui a carta que você deseja.")
        return  # Cancelar a troca
    else:
        for i in user_owners:
            print('teste se chegou aqui')
            bot.send_message(user_id, f"Usuário: {i.get('name')}\nID: {i.get('id')}")
        msg = bot.send_message(user_id,
                               "Envie APENAS o ID do usuário que você deseja trocar as cartas para enviá-lo uma solicitação de troca. Ou digite outra coisa para "
                               "cancelar a troca.")
        bot.register_next_step_handler(msg, confirmar_troca, id1, id2)


def confirmar_troca(mensagem, id1, id2):
    user = mongo.db.users.find_one({"id": mensagem.from_user.id})
    id_user_troca = int(mensagem.text)
    user_troca = mongo.db.users.find_one({"id": id_user_troca})
    user_id = user.get("id")

    tem_id = list(mongo.db.users.find({"id": id_user_troca}))

    if not str(id_user_troca).isdigit():
        bot.send_message(user_id, "Por favor, envie apenas o ID do usuário que você deseja trocar as cartas. Exemplo: "
                                  "123456789")
        return
    elif str(id_user_troca) == str(user.get("id")):
        bot.send_message(user_id, "Você não pode trocar cartas com você mesmo.")
        return

    elif tem_id == vetor_vazio:
        bot.send_message(user_id, "O ID que você digitou não pertence a nenhum usuário.")
        return

    else:
        carta1 = mongo.db.cards.find_one({"id": id1})
        carta2 = mongo.db.cards.find_one({"id": id2})

        try:
            bot.send_message(user_id, "Solicitação de troca enviada.")
            bot.send_message(id_user_troca, f"O usuário {user.get('name')} deseja trocar cartas com você.\n"
                                            f"Ele oferece a carta:\n\nNome:{carta2.get('nome')}\nID:{carta2.get('id')}\n\nEm "
                                            f"troca "
                                            f"da sua carta:\n\nNome:{carta1.get('nome')}\nID:{carta1.get('id')}.\n")
            msg = bot.send_message(id_user_troca, "Você aceita a troca? (Sim/Não)")
            bot.register_next_step_handler(msg, aceitar_troca, user_id, id1, id2)
        except telebot.apihelper.ApiTelegramException as e:
            # Aqui você lida com a exceção
            print(
                f"Erro ao enviar mensagem para o usuário {id_user_troca}: ELe não deu um start na conversa com o bot{e}")
            bot.send_message(user_id, "O usuário não deu um start na conversa com o bot, por esse motivo não consigo "
                                      "enviar uma mensagem para ele.\nA troca foi cancelada.")


def aceitar_troca(mensagem, id_user_troca, id1, id2):
    user_id = mensagem.from_user.id
    texto = mensagem.text
    if texto == "Sim" or texto == "sim" or texto == "SIM" or texto == "s" or texto == "S" or texto == "y" or texto == "Y" or texto == "yes" or texto == "Yes" or texto == "YES" or texto == "yep" or texto == "Yep" or texto == "YEP":
        user1 = mongo.db.users.find_one({"id": user_id})
        user2 = mongo.db.users.find_one({"id": id_user_troca})
        user1_colecao = user1.get("colecao")
        user2_colecao = user2.get("colecao")
        user1_colecao.remove(id1)
        user1_colecao.append(id2)
        user2_colecao.remove(id2)
        user2_colecao.append(id1)
        mongo.db.users.update_one({"id": user_id}, {"$set": {"colecao": user1_colecao}})
        mongo.db.users.update_one({"id": id_user_troca}, {"$set": {"colecao": user2_colecao}})
        bot.send_message(user_id, "Troca efetuada com sucesso.")
        bot.send_message(id_user_troca, "Troca efetuada com sucesso.")


@bot.message_handler(commands=["colec"])
def colec(mensagem):
    verificar = verificacao(mensagem)
    if not verificar:
        return
    else:
        user = mongo.db.users.find_one({"id": mensagem.from_user.id})
        colecao = user.get("colecao")
        if colecao:
            for i in colecao:
                card = mongo.db.cards.find_one({"id": i})
                bot.send_photo(mensagem.chat.id, card.get("link"))
                bot.send_message(mensagem.chat.id,
                                 f"Obra: {card.get('obra')}\nPersonagem: {card.get('nome')}\nID: {card.get('id')}")
        else:
            bot.send_message(mensagem.chat.id, "Você não possui cartas.")



def verificar(mensagem):
    return True


bot.polling()
