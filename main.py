from Bard import Chatbot
import os
import telebot
from dotenv import load_dotenv

load_dotenv('.env')

get_key = lambda key : os.environ.get(key)

bard = Chatbot(get_key('bard'))

bot = telebot.TeleBot(get_key('telebot'))

def generate_response(text):
	try:
		return bard.ask(text)
	except Exception as e:
		return e.args[1] if len(e.args) >1 else e
		
@bot.message_handler(commands=['start','help'])
def display_help(message):
	help_message=f"""
Hi **{message.from_user.first_name}**.
This bot will allow you to directly chat with [GoogleBard](https://bard.google.com).
Hope you will enjoy.
	"""
	bot.reply_to(message, help_message, parse_mode="Markdown")
	
@bot.message_handler(func = lambda m:True)
def chat_with_bard(message):
	bot.reply_to(message,generate_response(message.text), parse_mode="Markdown")
	
if __name__=="__main__":
	bot.infinity_polling()