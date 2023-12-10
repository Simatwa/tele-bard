<h1 align="center"> Tele-Bard </h1>

<p align="center">
<a href="https://wakatime.com/badge/github/Simatwa/tele-bard"><img src="https://wakatime.com/badge/github/Simatwa/tele-bard.svg" alt="wakatime"></a>


</p>

> Interact with [Bard](https://bard.google.com) on [Telegram](https://telegram.org)

## Installation & Usage

### Installation

[Python](https://python.org) >= 3.10 is required.


```
git clone https://github.com/Simatwa/tele-bard.git
cd tele-bard
pip install -r requirements.txt
```

## Usage

Get bard session from https://bard.google.com as detailed in [GoogleBard](https://github.com/acheong08/bard).

Create a Telegram bot using [BotFather](https://telegram.me/BotFather) in order to obtain a **Bot Token**.

Use those credentials to fill the [env](env) file and rename the file to `.env`

Start the bot `python main.py` and then start new chat with the app.

Send `/myId` for the bot to reply you with your **user_id** and then include the Id to the `.env` file.

> **Note** : If you want the bot to be accessed by multiple users. Include their `user_id` to the `.env` file separated by comma (`,`)

## Conclusion

- For hosting I recommend hosting with [pythonanywhere.com](https://pythonanywhere.com)

<p align="center">
Made with ❤️
</p>