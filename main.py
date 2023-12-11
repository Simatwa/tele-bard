from Bard import Chatbot
import os
import telebot
from telebot import types
from dotenv import load_dotenv
from BingImageCreator import ImageGen
from io import BytesIO
import requests

load_dotenv(".env")

get_key = lambda key: os.environ.get(key)

bard = Chatbot(get_key("bard"))

bot = telebot.TeleBot(get_key("telebot"))

allowed_user_ids = get_key("userId").split(',')

bing = ImageGen(get_key('bing'))

format_exception = lambda e:e.args[1] if len(e.args)>1 else str(e)

def is_verified(message):
    """Ensures it serves the right user"""
    for id in allowed_user_ids:
        if str(message.from_user.id) == id:
            return True


def anonymous_user(message):
    """Generate message for strange user"""
    response = f"""
	Hi **{message.from_user.first_name}**.
	You are not authorised to use this Bot.
	I recommmend setting up your own bot like this.
	Get the sourcecodes from [github](https://github.com/Simatwa/tele-bard).
	"""
    return response.strip()


def generate_response(text):
    """Fetches response from Bard"""
    try:
        return bard.ask(text).get("content")
    except Exception as e:
        return e.args[1] if len(e.args) > 1 else e


@bot.message_handler(commands=["start", "help"])
def display_help(message):
    sender = message.from_user.first_name
    help_message = (
        f"""
	Hi **{sender}**.This bot will allow you to directly chat with **GoogleBard**.
	Hope you will enjoy.
	
	> Available commands
	
	/start or /help : Show this messsage
	
	/myId : Check your Telegram's ID
	/reset : Start new conversation
	
	Any other text interacts with Bard.
   
   """.strip()
        if is_verified(message)
        else anonymous_user(message)
    )
    bot.reply_to(message, help_message, parse_mode="Markdown")


@bot.message_handler(commands=["reset"])
def reset_conversation(message):
    if is_verified(message):
        markup = types.InlineKeyboardMarkup()
        yes_btn = types.InlineKeyboardButton("Yes!", callback_data="yes")
        no_btn = types.InlineKeyboardButton("No!", callback_data="no")
        markup.add(yes_btn, no_btn)
        bot.send_message(
            message.chat.id,
            text="Are you sure to reset conversation",
            reply_markup=markup,
        )
    else:
        bot.reply_to(message, anonymous_user(message), parse_mode="Markdown")


@bot.message_handler(commands=["myId"])
def user_id(message):
    """Get to know your id"""
    bot.reply_to(
        message,
        text=f"Your Telegram ID is **{message.from_user.id}**",
        parse_mode="Markdown",
    )


@bot.message_handler(func=lambda m: True)
def chat_with_bard(message):
    """Generate response with Bard"""
    if is_verified(message):
        bot.reply_to(message, generate_response(message.text), parse_mode="Markdown")
    else:
        bot.reply_to(message, anonymous_user(message), parse_mode="Markdown")


@bot.message_handler(commands=['img_link'])
def generate_image_with_bing(message):
    if not is_verified:
        bot.reply_to(message, anonymous_user(message))
        return 
    
    try:
        image_links = bing.get_images(message.text)
        if isinstance(list, image_links):
            #Image generated
            for count, link in enumerate(image_links):
                bot.send_message(message.chat.id, f"{count+1}. {link}",)
        else:
            bot.reply_to(message, 'Failed to generate images')
    except Exception as e:

        bot.reply_to(message, f"Failed - {format_exception(e)}")

@bot.message_handler(commands=['img'])
def generate_image_with_bing(message):
    if not is_verified:
        bot.reply_to(message, anonymous_user(message))
        return 
    
    try:
        image_links = bing.get_images(message.text)
        if isinstance(list, image_links):
            #Image generated
            for img_url in image_links:
                with open(BytesIO(),"wb") as buffer:
                    try:
                        img_content = bing.session.get(img_url).content
                        buffer.write(img_content)
                        bot.send_photo(message.chat.id, buffer,img_url,)
                    except requests.exceptions.MissingSchema:
                        bot.reply_to(message, "Inappropriate contents found in the generated images. Please try again or try another prompt.")
                        break
                    except Exception as e:
                        bot.reply_to(message, format_exception(e))

        else:
            bot.reply_to(message, 'Failed to generate images')
    except Exception as e:
        bot.reply_to(message, "Failed - %s"%(format_exception(e)))

@bot.callback_query_handler(func=lambda message: True)
def callback_query(call):
    if call.data == "yes":
        global bard
        bard = Chatbot(get_key("bard"))
        bot.send_message(call.message.chat.id, "Conversation reset successfully.")
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Conversation retained.")

    else:
        bot.send_message(call.message.chat.id, f"Unrecognized command - {call.data}")


if __name__ == "__main__":
    bot.infinity_polling()
