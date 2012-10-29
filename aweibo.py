import sublime, sublime_plugin
import json, webbrowser, time, os, sys
from aaweibosdk import APIClient, APIError

APP_KEY = '2596542044'
GET_CODE_URL = 'http://sublime.duapp.com/weibo/authorize_redirect.php'
CALLBACK_URL = 'http://sublime.duapp.com/weibo/callback.php'
ACCESS_TOKEN_FILE = os.path.join(os.getcwd(), 'access_token')

#reload(sys) 
#sys.setdefaultencoding('utf8')

def do_weibo_error(weibo, errcode, recall = False):
	if errcode == 21327 or errcode == 21501	or 21313 < errcode < 21318:
		if sublime.ok_cancel_dialog("ACCESS TOKEN error!\n(Error No. : " + str(errcode) + ")\nGet a new token?", 'yes'):
			weibo.get_token()
	else :
		sublime.error_message('Error No. :' + str(error_code))

def format_statuses(source_statuses):
	statuses = []
	for status in source_statuses:
		if "deleted" in status and int(status["deleted"]) == 1:
			continue
		status_obj = {
			"id" : status["id"],
			"user" : status["user"]["name"],
			"status" : status["text"],
			"time" : status["created_at"]
		}
		if "retweeted_status" in status:
			if "deleted" in status["retweeted_status"] and int(status["retweeted_status"]["deleted"]) == 1:
				continue
			retweeted_status_obj = {
				"id" : status["retweeted_status"]["id"],
				"user" : status["retweeted_status"]["user"]["name"],
				"status" : status["retweeted_status"]["text"],
				"time" : status["retweeted_status"]["created_at"]
			}
			if "original_pic" in status["retweeted_status"]:
				retweeted_status_obj["with_pic"] = status["retweeted_status"]["original_pic"]
			
			status_obj["z"] = retweeted_status_obj

		if "status" in status:
			status_obj["z"] = status["status"]["text"]

		if "original_pic" in status:
				status_obj["with_pic"] = status["original_pic"]

		statuses.append(status_obj)
	return statuses

class weibo:
	def __init__(self):
		self.wb = APIClient(APP_KEY, None, CALLBACK_URL)
		self.get_local_token()
		self.get = self.wb.get
		self.post = self.wb.post

	def get_local_token(self):
		access_token_file = open(ACCESS_TOKEN_FILE)
		token = access_token_file.read()
		access_token_file.close()

		if token:
			self.set_token(token, False)

	def set_token(self, token = '', wtf = True):
		if not token:
			return

		if wtf:
			try:
				access_token_file = open(ACCESS_TOKEN_FILE, 'w')
				access_token_file.write(token)
				access_token_file.close()
			except IOError:
				sublime.status_message('Write token_file error!')
			else:
				sublime.status_message('TOKEN Saved.')
		
		self.wb.set_access_token(token, time.time() + 1209600)

	def get_token(self, open_browser = True):
		if open_browser:
			if sublime.ok_cancel_dialog("Open browser to get your ACCESS TOKEN?", "open"):
				webbrowser.open_new(GET_CODE_URL)

		sublime.active_window().show_input_panel("Input ACCESS TOKEN here: ", "", self.token_input_done, None, None)

	def token_input_done(self, text):
		if not text:
			self.get_token(False)
			sublime.message_dialog("Please input your Access TOKEN!")
		else :
			self.set_token(text)

	def send(self, text):
		if 0 < len(text) <= 140:
			try:
				sublime.status_message("Sending...!")
				self.wb.post.statuses__update(status = text)
			except APIError,data:
				do_weibo_error(self, int(data.error_code))					
			except Exception as e:
		 		sublime.error_message(str(e))
			else:
				sublime.status_message("Status has been sent!")
				return True

	def get_tweets(self, func, key, format, **kw):
		ret = {}
		sublime.status_message("Getting status...")
		try:
			ret = func(**kw)
			if format :
				ret = format_statuses(ret[key])
			return json.dumps(ret, sort_keys=True, indent=4, ensure_ascii=False)
		except APIError,data:
			do_weibo_error(self, int(data.error_code))
		except Exception as e:
		 	sublime.error_message(str(e))

	def get_timlines(self, format = False, **kw):
		return self.get_tweets(self.wb.get.statuses__home_timeline, "statuses", format, **kw)

	def get_at_me(self, format = False, **kw):
		return self.get_tweets(self.wb.get.statuses__mentions, "statuses", format, **kw)

	def get_to_me(self, format = False, **kw):
		return self.get_tweets(self.wb.get.comments__to_me, "comments", format, **kw)