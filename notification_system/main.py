from abc import ABC, abstractmethod
from uuid import uuid4
from datetime import datetime
from enum import Enum
from collections import defaultdict

class UrgencyLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class ChannelType(Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    PHONE = "PHONE"

class Client:
    def __init__(self, name):
        self.client_id = str(uuid4())
        self.name = name

class Notification:
    def __init__(self, message:str, urgency_level:UrgencyLevel, client:Client):
        self.message = message
        self.urgency = urgency_level
        self.client = client

class Subscriber:
    def __init__(self,name):
        self.subscriber_id = str(uuid4())
        self.name = name


class Channel(ABC):
    @abstractmethod
    def send(self, subscriber:Subscriber, notification:Notification):
        pass

class Phone(Channel):
    def send(self, subscriber, notification):
        print(f"Dear {subscriber.name} \n from {notification.client.name} \n Source:Phone \n Msg:{notification.message}.")
class Sms(Channel):
    def send(self, subscriber, notification):
        print(f"Dear {subscriber.name} \n from {notification.client.name} \n Source:Sms \n Msg:{notification.message}.")
class Email(Channel):
    def send(self, subscriber, notification):
        print(f"Dear {subscriber.name} \n from {notification.client.name} \n Source:Email \n Msg:{notification.message}.")

class ChannelFactory:
    def __init__(self):
        self.channels = {
            ChannelType.SMS:Sms(),
            ChannelType.PHONE:Phone(),
            ChannelType.EMAIL:Email()
        }
    # Since channels are stateless strategies, I keep singleton instances inside the factory. If they become stateful later, the factory can create new instances on demand.
    def get_channel(self, channel_type:ChannelType):
        return self.channels[channel_type]

class Subscription:
    def __init__(self, subscriber:Subscriber, client:Client):
        self.subscriber = subscriber
        self.client = client
        self.preferences:dict[
            UrgencyLevel,
            list[ChannelType]
        ] = {}
        
    def configure_strategy(self, urgency_lvl:UrgencyLevel, channel_types: list[ChannelType]):
        self.preferences[urgency_lvl] = channel_types
    
    def get_channels(self, urgency_lvl:UrgencyLevel):
        return self.preferences.get(urgency_lvl, [])

# Each Subscriber can configure a custom delivery strategy per urgency level per client
# where should the list of subscribers for a client live?
class SubscriptionManager:
    def __init__(self):
        # self.subscriber_preferences:dict[
        #     str,  # subscriber_id
        #     dict[str, # client_id 
        #          dict[UrgencyLevel,  
        #               list[Channel]
        #               ]
        #         ]
        #     ] = defaultdict()

        # Whenever a subscription is removed in the future, you'll need to update both.
        self.subscriptions:dict[
                tuple[str, str], # (subscriber_id, client_id)
                Subscription
                ] = {}
        
        self.cl_subs_map:dict[str, set[Subscriber]] = defaultdict(set)
    
    def add_to_cl_sub_map(self, client:Client, subscriber:Subscriber):
        self.cl_subs_map[client.client_id].add(subscriber)

    def add_subscriber(self, subscriber:Subscriber, client:Client):
        sub_id, cl_id = subscriber.subscriber_id, client.client_id
        if (sub_id, cl_id) not in self.subscriptions:
            self.subscriptions[(sub_id, cl_id)] = Subscription(subscriber, client)
            self.add_to_cl_sub_map(client, subscriber)
        else:
            print("Subscription is already created")

    def configure_strategy(self, subscriber:Subscriber, client:Client, urgency_lvl:UrgencyLevel, channels:list[ChannelType]):
        sub_id, cl_id = subscriber.subscriber_id, client.client_id
        if (sub_id, cl_id) not in self.subscriptions:
            raise ValueError("Create subscription first")
        self.subscriptions[(sub_id, cl_id)].configure_strategy(urgency_lvl, channels)

    def get_channels(self, subscriber:Subscriber, client:Client, urgency_lvl:UrgencyLevel) ->list[ChannelType]:
        key = (subscriber.subscriber_id, client.client_id)
        if key not in self.subscriptions:
            raise ValueError("Create subscription first")
        return self.subscriptions[key].get_channels(urgency_lvl)

    def get_subscribers(self, client:Client) -> list[Subscriber]:
        # for (_, cl_id), subs in self.subscriptions.items():
        #     if cl_id == client.client_id:
        #         all_subscribers.append(subs.subscriber)
        all_subscribers = list(self.cl_subs_map[client.client_id])
        return all_subscribers

class NotificationService:  # It is an orchestrator.
    # Receive notification -> Find subscribers ->Resolve channels ->Send notification

    def __init__(self, subscription_manager:SubscriptionManager, channel_factory:ChannelFactory):
        self.subscription_manager = subscription_manager
        self.channel_factory = channel_factory

    def send_notification(self, notification:Notification):
        # get all subscribers of this client
        all_subscribers = self.subscription_manager.get_subscribers(notification.client)
        for sub in all_subscribers:
            # then get all the channel for that urgency lvl
            channel_types = self.subscription_manager.get_channels(sub, notification.client, notification.urgency)
            # call the Channel to send notification
            for channel_type in channel_types:
                channel = self.channel_factory.get_channel(channel_type)
                channel.send(sub, notification)
        

def main():
    channel_factory = ChannelFactory()
    subscription_manager = SubscriptionManager()
    notification_service = NotificationService(subscription_manager, channel_factory)
    amazon = Client("Amazon Shopping")
    john = Subscriber("John")
    alice = Subscriber("Alice")
    subscription_manager.add_subscriber(john, amazon)
    subscription_manager.add_subscriber(alice, amazon)

    subscription_manager.configure_strategy(
        john, 
        amazon,
        UrgencyLevel.HIGH,
        [ChannelType.SMS, ChannelType.PHONE]
    )

    subscription_manager.configure_strategy(
        alice,
        amazon,
        UrgencyLevel.HIGH,
        [ChannelType.EMAIL]
    )

    notification1 = Notification("notification1", UrgencyLevel.HIGH, amazon)
    notification_service.send_notification(notification1)

main()

