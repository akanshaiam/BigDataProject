from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka.producer import KafkaProducer

access_token = "1374576763-MJG1pBwCZllwGIoYQWw2XkNIEOtXcUgjp3mvA5t"
access_token_secret =  "zopeHyvzMASoZe6TcOBQjkKJSeozDtqGtwngeNX23hoUz"
consumer_key =  "0NrQhUvVSINGGg5Mi1vYlH4EG"
consumer_secret =  "wu56Si3w9wnW8PAJFUaHtMglh0nJE8o15kkEVJdZA2m48gMzUO"

class StdOutListener(StreamListener):
    def on_data(self, data):
        producer.send("COVID19", data.encode('utf-8'))
        print (data)
        return True
    def on_error(self, status):
        print (status)

producer = KafkaProducer(bootstrap_servers='localhost:9092')
listener = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, listener)
stream.filter(track="COVID19")