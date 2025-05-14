import telebot
from telebot import TeleBot, types
import random
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
bot = TeleBot(os.environ["BOT_TOKEN"])


# Lista de mensagens enviadas para limpeza
mensagens_enviadas = []
# Função para obter os jogos mais recentes ou próximos
def obter_jogos():
    url = "http://localhost:3000/api/findall"
    try:
        response = requests.get(url)
        response.raise_for_status()
        matches = response.json()
        furia_games = [
            match for match in matches
            if 'FURIA' in match.get('team1', '') or 'FURIA' in match.get('team2', '')
        ]
        return furia_games
    except Exception as e:
        return {"error": str(e)}
    
# Função de limpeza de mensagens antigas
def limpar_mensagens_antigas():
    agora = datetime.utcnow()
    novas_mensagens = []

    for chat_id, msg_id, timestamp in mensagens_enviadas:
        if (agora - timestamp) > timedelta(minutes=40):
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Erro ao deletar mensagem {msg_id}: {e}")
        else:
            novas_mensagens.append((chat_id, msg_id, timestamp))  # ainda não tem 40 min

    # Atualiza a lista removendo as mensagens apagadas
    mensagens_enviadas.clear()
    mensagens_enviadas.extend(novas_mensagens)

# Agendando a limpeza de mensagens
scheduler = BackgroundScheduler()
scheduler.add_job(limpar_mensagens_antigas, 'interval', minutes=5)

# Lista de chats que ativaram notificações
usuarios_notificacoes = set()

def checar_proximos_jogos():
    jogos = obter_jogos_filtrados("upcoming")
    print("Jogos encontrados:", jogos)  # Log para depuração
    if not jogos or isinstance(jogos, dict):
        return
    ...

    agora = datetime.utcnow()
    for jogo in jogos:
        try:
            horario_str = jogo['date']
            horario_jogo = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")

            if timedelta(minutes=59) < (horario_jogo - agora) < timedelta(minutes=61):
                texto = (
                    f"🚨 *Falta 1 hora para o jogo da FURIA!*\n\n"
                    f"📅 *Data:* {jogo['date']}\n"
                    f"🔥 *{jogo['team1']}* vs *{jogo['team2']}*\n"
                    f"🏆 *Evento:* {jogo['event']}"
                )
                for chat_id in usuarios_notificacoes:
                    msg = bot.send_message(chat_id, texto, parse_mode='Markdown')
                    mensagens_enviadas.append((chat_id, msg.message_id, datetime.utcnow()))
        except Exception as e:
            print("Erro ao processar jogo:", e)

scheduler.add_job(checar_proximos_jogos, 'interval', minutes=5)
scheduler.start()

# Função para obter jogos filtrados por tipo
def obter_jogos_filtrados(tipo):
    url = "http://localhost:3000/api/findall"
    try:
        response = requests.get(url)
        response.raise_for_status()
        jogos = response.json()
        return [j for j in jogos if j.get("type") == tipo]
    except Exception as e:
        return {"error": str(e)}

# Função para ativar notificações
@bot.message_handler(commands=['notificacoes_on'])
def ativar_notificacoes(message):
    usuarios_notificacoes.add(message.chat.id)
    bot.send_message(message.chat.id, "🔔 Notificações ativadas! Você será avisado 1 hora antes dos jogos da FURIA.")

# Função para desativar notificações
@bot.message_handler(commands=['notificacoes_off'])
def desativar_notificacoes(message):
    usuarios_notificacoes.discard(message.chat.id)
    bot.send_message(message.chat.id, "🔕 Notificações desativadas.")

# Função para criar o menu principal
def Menu_Principal():
    markup = types.InlineKeyboardMarkup()
    Button_Loja = types.InlineKeyboardButton('🛒 Loja', callback_data='Loja')
    Button_Redes = types.InlineKeyboardButton('🌐 Redes Sociais', callback_data='Redes Sociais')
    Button_Transmissoes = types.InlineKeyboardButton('📺 Transmissões', callback_data='Transmissoes')
    Button_Jogos = types.InlineKeyboardButton('🎮 Jogos', callback_data='Jogos')
    Button_Curiosidades = types.InlineKeyboardButton('❓ Curiosidades', callback_data='Curiosidades')
    Button_Campeonatos = types.InlineKeyboardButton('🏆 Campeonatos', callback_data='Campeonatos')
    Button_Elenco = types.InlineKeyboardButton('🧢 Elenco Atual', callback_data='Elenco')
    markup.add(Button_Loja)
    markup.add(Button_Redes)
    markup.add(Button_Transmissoes)
    markup.add(Button_Jogos)
    markup.add(Button_Curiosidades)
    markup.add(Button_Campeonatos)
    markup.add(Button_Elenco)
    return markup

# Função para voltar ao menu
def voltar_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💬 Voltar ao Menu', callback_data='VoltarMenu'))
    return markup

def submenu_jogos():
    markup = types.InlineKeyboardMarkup()
    Button_Ultimos_Jogos = types.InlineKeyboardButton('Últimos Jogos', callback_data='UltimosJogos')
    Button_Proximos_Jogos = types.InlineKeyboardButton('Próximos Jogos', callback_data='ProximosJogos')
    markup.add(Button_Ultimos_Jogos, Button_Proximos_Jogos)
    return markup


@bot.callback_query_handler(func=lambda call: True)
def tratar_botoes(call):
    data = call.data
    print(f'Botão pressionado: {data}')
    
    if data == 'Jogos':
        bot.edit_message_text(
            "Escolha uma opção abaixo:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=submenu_jogos()
        )

    elif data == 'UltimosJogos':
        jogos = obter_jogos_filtrados("finished")
        if jogos and not isinstance(jogos, dict):
            texto = "*Últimos Jogos da FURIA:*\n\n"
            for jogo in jogos:
                texto += f"📅 *Data:* {jogo['date']}\n"
                texto += f"🔥 *{jogo['team1']}* vs *{jogo['team2']}*\n"
                texto += f"🏆 *Evento:* {jogo['event']}\n\n"
            bot.send_message(call.message.chat.id, texto, parse_mode='Markdown', reply_markup=voltar_menu())
        else:
            bot.send_message(call.message.chat.id, "📭 Nenhum jogo finalizado encontrado.", reply_markup=voltar_menu())

    elif data == 'ProximosJogos':
        jogos = obter_jogos_filtrados("upcoming")
        if jogos and not isinstance(jogos, dict):
            texto = "*Próximos Jogos da FURIA:*\n\n"
            for jogo in jogos:
                texto += f"📅 *Data:* {jogo['date']}\n"
                texto += f"🔥 *{jogo['team1']}* vs *{jogo['team2']}*\n"
                texto += f"🏆 *Evento:* {jogo['event']}\n\n"
            bot.send_message(call.message.chat.id, texto, parse_mode='Markdown', reply_markup=voltar_menu())
        else:
            bot.send_message(call.message.chat.id, "📭 Nenhum jogo encontrado.", reply_markup=voltar_menu())

    elif data == 'VoltarMenu':
        bot.edit_message_text(
            '🔙 Voltando ao menu principal...',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=Menu_Principal()
        )

    elif data == 'Loja':
        bot.send_message(
            call.message.chat.id,
            "*🛒 Nossa Loja:* [furia.gg](https://www.furia.gg)",
            parse_mode='Markdown',
            reply_markup=voltar_menu()
        )

    elif data == 'Redes Sociais':
        texto = (
            "🌐 *Siga a FURIA nas redes sociais:*\n\n"
            "📸 Instagram: [@furiagg](https://www.instagram.com/furiagg)\n"
            "🐦 (X): [@FURIA](https://x.com/FURIA)\n"
            "🎬 Tik Tok: https://www.tiktok.com/@furia\n"
        )
        bot.send_message(
            call.message.chat.id,
            texto,
            parse_mode='Markdown',
            reply_markup=voltar_menu()
        )

    elif data == 'Transmissoes':
        bot.send_message(
            call.message.chat.id,
            "📺 *Transmissões ao vivo em:* [Twitch.tv/furiagg](https://www.twitch.tv/furiatv)",
            parse_mode='Markdown',
            reply_markup=voltar_menu()
        )

    elif data == 'Curiosidades':
        curiosidades = [
    "A FURIA foi fundada em agosto de 2017 por Jaime 'raizen' Pádua e André Akkari.",
    "O nome 'FURIA' representa agressividade e determinação — uma marca registrada do estilo de jogo do time.",
    "A organização é brasileira, mas tem sede em Miami, nos Estados Unidos.",
    "A FURIA ficou conhecida internacionalmente pelo seu estilo de jogo rápido e ousado no CS:GO.",
    "A equipe já participou de vários Majors e chegou às semifinais do PGL Antwerp Major 2022.",
    "A organização também investe em outros jogos como League of Legends, Valorant, PUBG e Apex Legends.",
    "Eles têm uma linha de roupas própria — a FURIA Wear — com coleções exclusivas.",
    "FalleN entrou para a FURIA em 2023, formando o projeto com o objetivo de criar um time brasileiro forte internacionalmente.",
    "A torcida da FURIA é uma das mais apaixonadas do cenário de esports brasileiro.",
    "Além dos jogos, a FURIA trabalha com educação e performance através do projeto FURIA Academy."
    ]

    
        texto = "*❓ Curiosidades sobre a FURIA:*\n\n" + "\n".join([f"• {c}" for c in curiosidades])
        bot.send_message(
            call.message.chat.id,
            texto,
            parse_mode='Markdown',
            reply_markup=voltar_menu()
        )

    elif data == 'Campeonatos':
        texto = (
            "🏆 *Campeonatos recentes da FURIA:*\n\n"
            "• PGL Major\n"
            "• ESL Pro League\n"
            "• IEM Dallas"
        )
        bot.send_message(
            call.message.chat.id,
            texto,
            parse_mode='Markdown',
            reply_markup=voltar_menu()
        )

    elif data == 'Elenco':
        texto = (
        "🧢 *Elenco atual da FURIA (CS2 - 2025):*\n\n"
        "• FalleN (IGL & AWP)\n"
        "• KSCERATO\n"
        "• YEKINDAR\n"
        "• Molodoy\n"
        "• yuurih"
    )
    bot.send_message(
        call.message.chat.id,
        texto,
        parse_mode='Markdown',
        reply_markup=voltar_menu()
    )


    
# Outras funções e botões, como Campeonatos, Curiosidades, etc.

print("🤖 Bot rodando...")
bot.infinity_polling()