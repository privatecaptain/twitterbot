import tweepy
import sqlite3
import time


conn = sqlite3.connect("twitter_data.db")


consumer_key = "4kTL89hW5YqX4GPUUpzJ6lYbF"
consumer_secret = "uEAmYCALLO5CSKlm0Yql39RTeF8PeRByYt3G8kASM8JjVRzrS1"

access_token = "3024584890-Q5ioenppb3YkulE1Tl4cqdhD4l4B1uEv8KdlBsL"
access_token_secret = "AKY6dEaAZYgwx91Op4lZor4kjQBVYB5j8VfMsuSpq99pE"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def follow_back():
	for follower in tweepy.Cursor(api.followers).items():
		follower.follow()
		print "Followed {0}".format(follower.name)


def retrieve_users():
	with conn:
		cur = conn.cursor()
		cur.execute("SELECT user_name,latest_tweet FROM USERS")
		rows = cur.fetchall()

	return rows


def retweet(user_tup):
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



while True:
	try:
		follow_back()
	except 	Exception,e:
		print e
	try:
		users = retrieve_users()
	except Exception,e:
		print e
	if users:
		for i in users:
			try:
				retweet(i)
			except Exception,e:
				print e
	print "Now Sleeping...."
	time.sleep(900)


