import tornado.escape
import tornado.ioloop
import tornado.web
import sqlite3
import tweepy

conn = sqlite3.connect("twitter_data.db")

consumer_key = "4kTL89hW5YqX4GPUUpzJ6lYbF"
consumer_secret = "uEAmYCALLO5CSKlm0Yql39RTeF8PeRByYt3G8kASM8JjVRzrS1"



def authenticate(access_token,access_token_secret):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token,access_token_secret)
	return tweepy.API(auth)


def generate_tokens():
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	try:
		redirect_url = auth.get_authorization_url()
	except tweepy.TweepError,e:
		print e
	return (redirect_url,auth.request_token)




def adduser(screen_name,api):
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
	except tweepy.error.TweepError,e:
		print e
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
		try:
			with conn:
				cur = conn.cursor()
				cur.execute("SELECT access_token,secret FROM ACCOUNTS")
				row = cur.fetchone()
		except:
			self.write("No Account Added :(")
		if row != None:
			api = authenticate(row[0],row[1])
			user_name = self.get_query_argument('user_name')
			self.write(adduser(user_name,api))
		else:
			self.write("No Account Added :(")
		self.write(''' <a href="/">Back</a>''')



class AddAccount(tornado.web.RequestHandler):

	def get(self):
		t = generate_tokens()
		self.set_cookie('oauth_token',t[1]['oauth_token'])
		self.set_cookie('oauth_token_secret',t[1]['oauth_token_secret'])
		self.redirect(t[0])

class AccountFinal(tornado.web.RequestHandler):

	def get(self):
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		verifier = self.get_argument('oauth_verifier')
		try:
			# with conn:
			# 	cur = conn.cursor()
			# 	lid = cur.lastrowid
			# 	cur.execute("SELECT request_token FROM ACCOUNTS WHERE id=?",lid)
			# 	row = cur.fetchone()
			rt = {}
			rt['oauth_token'] = self.get_cookie('oauth_token')
			rt['oauth_token_secret'] = self.get_cookie('oauth_token_secret')
			rt['oauth_callback_confirmed'] = 'true'
			auth.request_token = rt
			print auth.request_token

			try:
				auth.get_access_token(verifier)
				api = authenticate(auth.access_token,auth.access_token_secret)
				name = api.me().name
				with conn:
					cur = conn.cursor()
					t = (name, auth.access_token,auth.access_token_secret)
					cur.execute("INSERT INTO ACCOUNTS(Name, access_token, secret) VALUES(?,?,?)",t)
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
				self.write('''{0}         {1}    <a href="/removeuser?uid={2}">Remove</a><br>'''.format(i[1],i[2],i[0]))
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

class RemoveUser(tornado.web.RequestHandler):

	def get(self):
		uid = self.get_query_argument('uid')
		try:
			with conn:
				t = (uid,)
				cur = conn.cursor()
				cur.execute("DELETE FROM USERS WHERE id=?",t)
		except:
			self.write("Unable to delete user :(")
		self.write(''' <a href="/">Back</a>''')



application = tornado.web.Application([
	(r'/',MainHandler),
	(r'/add_user',AddUser),
	(r'/listusers',ListUsers),
	(r'/listacc',ListAccounts),
	(r'/add',AddAccount),
	(r'/addfinal',AccountFinal),
	(r'/removeuser',RemoveUser),
	])

print "Server Running..."

if __name__ == "__main__":
    application.listen(5000)
    tornado.ioloop.IOLoop.instance().start()