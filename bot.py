import telepot, time, json, os, datetime, threading, logging, sys
from reactosrss import ReactosRss
from telepot.loop import MessageLoop
from telepot.exception import BotWasKickedError, BotWasBlockedError

logging.basicConfig(
    filename="jirainformer.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

histfilename = 'history.json'
configfilename = 'config.json'



def save_setts():
    with open(configfilename, 'w') as f:
        txt = json.dumps(settings, indent=4, sort_keys=True)
        f.write(txt)
        
def save_history():
	with open(histfilename, 'w') as f:
		txt = json.dumps(history, indent=4, sort_keys=True)
		f.write(txt)

def create_settings():
	settings = { 'bot_token':'', 'chat_ids':[] }
	settings['bot_token'] = input("Enter bot token:")
	save_setts()

if os.path.isfile(configfilename): 
	with open(configfilename) as config:    
	    settings = json.load(config)
else:
	create_settings()

if os.path.isfile(histfilename): 	
	with open(histfilename) as histconfig:
		history = json.load(histconfig)
else:
	history = { 'reactosrss_last_post':1503447411.0 }
	save_history()


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    logging.info("Handled {0} message from {1} chat with id: {2};".format(content_type, chat_type, chat_id))
    if content_type == 'text':
    	if msg['text'] == '/start' or msg['text'] == '/start@reactosspamerbot':
    		if not(chat_id in settings['chat_ids']):
    			bot.sendMessage(chat_id, "Now I'm working here!")
	    		settings['chat_ids'].append(chat_id)
	    		save_setts()
	    		logging.info('Bot was started in {0} chat with id: {1}'.format(chat_type, chat_id))
	    	else:
	    		bot.sendMessage(chat_id, "I'm already working!")
    	elif msg['text'] == '/help' or msg['text'] == '/help@reactosspamerbot':
    		bot.sendMessage(chat_id, "Спасибо за то, что открыли помощь!")
    	elif msg['text'] == '/stop' or msg['text'] == '/stop@reactosspamerbot':
    		settings['chat_ids'].remove(chat_id)
    		bot.sendMessage(chat_id, "Good bye!")
    		save_setts()
    		logging.info('Bot was stopped in {0} chat with id: {1}'.format(chat_type, chat_id))
    	elif chat_type == 'private':
    		bot.sendMessage(chat_id, "Неправильная команда!\nВот правильные:\n/help - открыть помощь.")

bot = telepot.Bot(settings['bot_token'])
bot.sendMessage(56801774, "говно залупа пенис хер давалка")
me = bot.getMe()
print(me)

MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

def reactosrss_posting_thread():
	while True:
		try:
			els = ReactosRss.get()
		except Exception as e:
			logging.error("Error while receiving RSS from Jira: {0}".format(e))
			time.sleep(10)
		else:
			for el in reversed(els):
				postdatetime = datetime.datetime.strptime(el['pubDate'], "%a, %d %b %Y %H:%M:%S %z")
				postunixtime = time.mktime(postdatetime.timetuple())
				if postunixtime < (history['reactosrss_last_post'] +1):
					continue
				else:
					history['reactosrss_last_post'] = postunixtime
					save_history()
					
				if el['fixversion'] != '':
					post = '*{0}*\nwas resolved as *{1}* by [{2}]({3}) and will be merged in *{4}*\n{5}'.format(el['title'], el['status'],el['resolver'], el['resolverlink'], el['fixversion'], el['link'])
				else:
					post = '*{0}*\nwas resolved as *{1}* by [{2}]({3})\n{4}'.format(el['title'], el['status'],el['resolver'], el['resolverlink'],  el['link'])
				
				for cid in settings['chat_ids'][:]:
					for _ in range(3):
						try:
							bot.sendMessage(cid, post, parse_mode='Markdown')
						except (BotWasKickedError, BotWasBlockedError) as e:
							settings['chat_ids'].remove(cid)
							save_setts()
							logging.info("Bot was kicked or blocked from chat with id: {0}".format(cid))
						except Exception as e:
							logging.error("Unknown error while sending message: {0}; {1}".format(e, sys.exc_info()[0]))
							continue
						else:
							break
		time.sleep(60)


t = threading.Thread(target=reactosrss_posting_thread)
t.daemon = True
t.start()
while 1:
	time.sleep(1000)
