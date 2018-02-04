# Setup manual
Clone this repository, then enter your bot token to file `config.json`, example:
```
{
    "bot_token": "489090212:AAFhh9Ip3Ss2V3TAkedw8-AtYktgmYBgvR4",
    "chat_ids": [
    ]
}
```


Change default history file default values in source or create file `history.json` with current data in seconds, example:
```
{
    "reactosrss_last_post": "1465283242",
    "rectosrss_last_posts": []
}
```
Install `telepot` for telegram bot api:
```
pip install telepot
```
And run:
```
python bot.py
```
