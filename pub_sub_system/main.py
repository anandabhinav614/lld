from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

class Message:
    def __init__(self, payload):
        self.msg_id = str(uuid4())
        self.payload = payload
        self.timestamp = datetime.now()
        
class Subscriber(ABC):
    def __init__(self, name):
        self.subscriber_id = str(uuid4())
        self.name = name

    @abstractmethod
    def receive_message(self, message:Message):
        pass


class Topic:
    def __init__(self, name):
        self.name = name
        self.subscribers:dict[str, Subscriber] = {}
        self.lock = Lock()

    def add_subscriber(self, subscriber:Subscriber):
        with self.lock:
            self.subscribers[subscriber.subscriber_id] = subscriber

    def publish(self, message:Message, executor:ThreadPoolExecutor):
        with self.lock:
            subscribers_snapshot = list(self.subscribers.values())
        for subs in subscribers_snapshot:
            # subs.receive_message(message)
            executor.submit(self._deliver_message, subs, message)
        
    def _deliver_message(self, subscriber:Subscriber, message):
        try:
            subscriber.receive_message(message)
        except Exception as e:
            print(f"Delivery failed: {e}")
        
    def unsubscribe(self, subscriber_id):
        with self.lock:
            if subscriber_id in self.subscribers:
                del self.subscribers[subscriber_id]
                return True
        return False

class PubSubService:

    def __init__(self):
        self.topics:dict[str, Topic] = {}
        self.lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=10)
        

    def create_topic(self, topic_name) -> Topic:
        with self.lock:
            if topic_name in self.topics:
                raise ValueError("topic name already exists.")
            new_topic = Topic(topic_name)
            self.topics[new_topic.name] = new_topic
            return new_topic
        

    def subscribe(self, subscriber:Subscriber, topic_name:str):
        with self.lock:
            topic = self.topics.get(topic_name, None)
        if topic is None:
            raise ValueError("No topic found")
        topic.add_subscriber(subscriber)
        

    def unsubscribe(self, subscriber_id, topic_name) -> bool:
        with self.lock:
            topic = self.topics.get(topic_name, None)
        if topic is None:
            raise ValueError("No topic found")
        return topic.unsubscribe(subscriber_id)
        
    def publish(self, topic_name, message:Message):
        with self.lock:
            topic = self.topics.get(topic_name, None)
        if topic is None:
            raise ValueError("Incorrect topic name")
        topic.publish(message, self.executor)



def main():
    pub_sub_service = PubSubService()
    new_topic = pub_sub_service.create_topic("new_topic")

main()