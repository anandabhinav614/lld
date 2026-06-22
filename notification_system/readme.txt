Design Notification System
    Design a Notification Service that supports:
        Multiple Clients (Amazon Shopping, AWS, etc.)
        Each client has multiple Subscribers
        Notifications have three urgency levels: HIGH, MEDIUM, LOW
        Each Subscriber can configure a custom delivery strategy per urgency level per client
        Notification channels: PHONE, SMS, EMAIL (extensible)
    System should:
        Accept notifications from clients
        Resolve subscriber-specific strategies
        Deliver notifications via configured channels

