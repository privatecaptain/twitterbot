import tornado.escape
import tornado.ioloop
import tornado.web
import sqlite3
import tweepy

conn = sqlite3.connect("twitter_data.db")



callback_url = "http://127.0.0.1:8888/addfinal"

consumer_key = "4kTL89hW5YqX4GPUUpzJ6lYbF"
consumer_secret = "uEAmYCALLO5CSKlm0Yql39RTeF8PeRByYt3G8kASM8JjVRzrS1"

access_token = "3024584890-Q5ioenppb3YkulE1Tl4cqdhD4l4B1uEv8KdlBsL"
access_token_secret = "AKY6dEaAZYgwx91Op4lZor4kjQBVYB5j8VfMsuSpq99pE"



# api = tweepy.API(auth)
temp = {}

def generate_tokens():
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	try:
		redirect_url = auth.get_authorization_url()
	except tweepy.TweepError,e:
		print e
	# with conn:
	# 	t = (auth.request_token,)
	# 	print t
	# 	cur = conn.cursor()
	# 	cur.execute("INSERT INTO ACCOUNTS(request_token) VALUES(?);",t)
	return (redirect_url,auth.request_token)


def authenticate(access_token,access_token_secret):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token,access_token_secret)
	return tweepy.API(auth)


def adduser(screen_name):
	user = None
	try:
		user =  api.get_user(screen_name)
		latest_tweet = api.me().timeline()[0].id
		timeline = user.timeline()
		if timeline:
			latest_tweet = timeline[0].id
		with conn:
			cur = conn.cursor()
			t = (screen_name,latest_tweet)
			cur.execute("INSERT INTO USERS(user_name,latest_tweet) VALUES (?,?);",t)
			return	"User Added ;)"
	except tweepy.error.TweepError:
		return "Incorrect username!!!"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
    	self.write(r'''<HTML><body>
					<h1>Welcome to Twitter Bot !!!</h1>
					<p1>Add a new User for Auto-ReTweeting</p1>
					<form action="add_user">
					<input type="text" name="user_name"><br>
					<input type="submit" name="Submit"><br>
					</form>
					<a href="/listusers">List Users</a>
					<a href="/listacc">List Accounts</a>
					<a href="/add">Add Twitter Account </a>
					</body>
					</HTML>
    			''')
        


class AddUser(tornado.web.RequestHandler):
	
	def get(self):
		user_name = self.get_query_argument('user_name')
		self.write(adduser(user_name))
		self.write(''' <a href="/">Back</a>''')



class AddAccount(tornado.web.RequestHandler):

	def get(self):
		t = generate_tokens()
		self.set_cookie('request_token',str(t[1]))
		self.redirect(t[0])

class AccountFinal(tornado.web.RequestHandler):

	def get(self):
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret,callback_url)
		verifier = self.get_argument('oauth_verifier')
		try:
			# with conn:
			# 	cur = conn.cursor()
			# 	lid = cur.lastrowid
			# 	cur.execute("SELECT request_token FROM ACCOUNTS WHERE id=?",lid)
			# 	row = cur.fetchone()
			auth.request_token = dict(self.get_cookie('request_token'))
			print auth.request_token

			try:
				auth.get_access_token(verifier)
				api = authenticate(auth.access_token,auth.access_token_secret)
				name = api.me().name
				with conn:
					cur = conn.cursor()
					lid = cur.lastrowid
					t = (name, auth.access_token,auth.access_token_secret,lid)
					cur.execute("UPDATE ACCOUNTS SET Name=?, access_token=? , secret=? WHERE id=?",t)
				self.write("Account Created")
				self.write(''' <a href="/">Back</a>''')
			except tweepy.TweepError,e:
			    print e
		except:
			print "Error"




class ListUsers(tornado.web.RequestHandler):

	def get(self):
		with conn:
			cur = conn.cursor()
			cur.execute("SELECT * FROM USERS")
			rows = cur.fetchall()
			self.write("USER NAME         latest_tweet<br>")
			self.write("<br>")
			for i in rows:
				self.write("{0}         {1}<br>".format(i[1],i[2]))
		self.write(''' <a href="/">Back</a>''')


class ListAccounts(tornado.web.RequestHandler):

	def get(self):
		with conn:
			cur = conn.cursor()
			cur.execute("SELECT Name FROM ACCOUNTS")
			rows = cur.fetchall()
			self.write("NAME<br>")
			for i in rows:
				self.write(i[0])
		self.write(''' <a href="/">Back</a>''')



application = tornado.web.Application([
	(r'/',MainHandler),
	(r'/add_user',AddUser),
	(r'/listusers',ListUsers),
	(r'/listacc',ListAccounts),
	(r'/add',AddAccount),
	(r'/addfinal',AccountFinal),
	])

print "Server Running..."

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()