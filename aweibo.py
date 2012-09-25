import sublime, sublime_plugin
import json, webbrowser, time, os
from weibosdk import APIClient, APIError

APP_KEY = '2596542044'
GET_CODE_URL = 'http://sublime.duapp.com/weibo/authorize_redirect.php'
CALLBACK_URL = 'http://sublime.duapp.com/weibo/callback.php'
ACCESS_TOKEN_FILE = os.path.join(os.getcwd(), 'access_token')

wb = APIClient(APP_KEY, None, CALLBACK_URL)

def do_weibo_error(weibo, errcode):
	if errcode == 21327 or errcode == 21501	or 21313 < errcode < 21318:
		if sublime.ok_cancel_dialog("ACCESS TOKEN error!\n(Error No. : " + str(errcode) + ")\nGet a new token?", 'yes'):
			self.get_token()
	else :
		sublime.error_message('Error No. :' + str(error_code))

class weibo:
	def __init__(self):

		access_token_file = open(ACCESS_TOKEN_FILE)
		token = access_token_file.read()
		access_token_file.close()

		if token:
			self.set_token(token)

	def set_token(self, token = ''):
		if not token:
			return

		try:
			access_token_file = open(ACCESS_TOKEN_FILE, 'w')
			access_token_file.write(token)
			access_token_file.close()
		except IOError:
			sublime.status_message("Write token_file error!")
		else:
			sublime.status_message("TOKEN Saved.")
		finally:
			wb.set_access_token(token, time.time() + 1209600)

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
		try:
			sublime.status_message("Sending...!")
			wb.post.statuses__update(status = text)
		except APIError,data:
			do_weibo_error(self, int(data.error_code))
				
		except:
			sublime.error_message("Unknow error!")
		else:
			sublime.status_message("Status has been sent!")
			return True

	def get_timlines(self, format = False):
		ret = {}
		try:
			ret = wb.get.statuses__home_timeline()

			if format :
				statuses = []
				for status in ret["statuses"]:
					status_obj = {
						"id" : status["id"],
						"user" : status["user"]["name"],
						"status" : status["text"]
					}
					statuses.append(status_obj)

				ret = statuses
		except APIError,data:
			do_weibo_error(self, int(data.error_code))
		except:
			sublime.error_message("Unknow error!")
		finally:
			return json.dumps(ret, sort_keys=True, indent=4, ensure_ascii=False)

