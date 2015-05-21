import tweepy
import sqlite3
import time


conn = sqlite3.connect("twitter_data.db")


consumer_key = "4kTL89hW5YqX4GPUUpzJ6lYbF"
consumer_secret = "uEAmYCALLO5CSKlm0Yql39RTeF8PeRByYt3G8kASM8JjVRzrS1"


def authenticate(access_token,access_token_secret):
	try:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token,access_token_secret)
		return tweepy.API(auth)
	except:
		return None


def follow_back(api):
	for follower in tweepy.Cursor(api.followers).items():
		follower.follow()
		print "Followed {0}".format(follower.name)


def retrieve_users():
	with conn:
		cur = conn.cursor()
		cur.execute("SELECT user_name,latest_tweet FROM USERS")
		rows = cur.fetchall()

	return rows


def retweet(user_tup,api):
	user_name = user_tup[0]
	latest_tweet = user_tup[1]
	user = api.get_user(user_name)
	new_tweets = user.timeline(since_id=latest_tweet)
	if new_tweets:
		latest_tweet = new_tweets[0].id
		with conn:
			t = (latest_tweet,user_name)
			cur = conn.cursor()
			cur.execute("UPDATE USERS SET latest_tweet=? WHERE user_name=?",t)
	for i in new_tweets:
		try:
			api.retweet(i.id)
			print "ReTweeting.."
		except:
			print "RT Failed :("

def getapis():
	with conn:
		cur = conn.cursor()
		cur.execute("SELECT access_token,secret FROM ACCOUNTS")
		rows = cur.fetchall()
	apis = []
	for i in rows:
		apis.append(authenticate(i[0],i[1]))
	return apis


def main_procedure(api):
	try:
		follow_back(api)
	except 	Exception,e:
		print e
	try:
		users = retrieve_users()
	except Exception,e:
		print e
	if users:
		for i in users:
			try:
				retweet(i,api)
			except Exception,e:
				print e

while True:
	apis = getapis()
	for api in apis:
		main_procedure(api)
	print "Now Sleeping...."
	time.sleep(900)


