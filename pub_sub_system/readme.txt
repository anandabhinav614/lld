The Pub-Sub system should allow publishers to publish messages to specific topics.
Subscribers should be able to subscribe to topics of interest and receive messages published to those topics.
The system should support multiple publishers and subscribers.
Messages should be delivered to all subscribers of a topic in real-time.
The system should handle concurrent access and ensure thread safety.
The Pub-Sub system should be scalable and efficient in terms of message delivery.

flow:
publisher - > Topic ->Subscriber

Entities:
    Publisher
    Subscriber - subscribers are assigned into topics
               - A Subscriber should mainly know how to consume a message.
    Topic  - The topic should decide which subscribers get notified.
    Message
    PubSubSystem (or Broker)

Concurrency: What data can be modified by multiple threads?
    topcis, subscribers
    -------------------------------------------------------------
    Race Condition #1
        Thread A:
        subscribe(sub1, "sports")

        Thread B:
        unsubscribe(sub1, "sports")

        Both modify: -> topic.subscribers   simultaneously.

        Without synchronization:
            Lost updates
            Inconsistent state
            Runtime errors  
        can happen.
    -----------------------------------------------------------------
    Race Condition #2
        Thread A:
            create_topic("sports")
            and
        Thread B:
            create_topic("sports")
            at the same time.

        Both execute:
        if topic_name not in self.topics:
        before either inserts.
        Now both create the topic.
        Classic check-then-act race.
    -------------------------------------------------------------------
    Race Condition #3 (Most Interesting)
        Thread A:
            publish(message)
            Inside:
            for subscriber in self.subscribers.values():
            While simultaneously:

        Thread B:
            unsubscribe(...)
            removes a subscriber.
            Now you're modifying a dictionary while iterating over it.

        In Python you'll typically get:
        RuntimeError: dictionary changed size during iteration

To avoid blocking the publisher thread, I would introduce a shared ThreadPoolExecutor in PubSubService. 
Topic.publish() would submit delivery tasks to the executor instead of invoking subscribers synchronously. 
This allows publish() to return quickly while deliveries happen asynchronously.