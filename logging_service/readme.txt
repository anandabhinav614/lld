A logger is the in-process library an application uses to record what's happening at runtime. 
Code calls logger.info("user signed in") from anywhere in the app, and the library timestamps the message, 
attaches the severity level, and writes it to one or more places like the console, a file, or both. 
Think Log4j, SLF4J, or Python's logging module. 
We're designing the library that lives inside one application, not a distributed log aggregation service.

REQ:
1.Log Levels -> DEBUG < INFO < WARN < ERROR < FATAL
    Why do they mention ordering? Because filtering will depend on it.  Suppose a destination accepts:WARN and above
    DEBUG -> ignore
    INFO  -> ignore
    WARN  -> write
    ERROR -> write
    FATAL -> write

2. Multiple Destinations: One logger can write to multiple destinations.
    logger.info("User created") ->should simultaneously go to:
                                 Console:   [INFO] User created
                                 File :  2026-06-20 INFO User created
     When log() is called:
    for destination in destinations:
        destination.write(record)      

3.  Per-Destination Filtering
    Console -> DEBUG
    File    -> WARN   

    and Log call: logger.info("User login")
    Console receives: INFO User login
    File receives: nothing  (because INFO < WARN.)

    means Filter belongs to destination.

4. Formatting
   Format and destination are independent.
   Console + Text,  Console + JSON,File + Text, File + JSON
   Separate the two dimensions.
   Dimension 1:Where to write?
   Dimension 2:How to format?

    Eg, How to format?: TextFormatter, JsonFormatter
        Compose them: ConsoleDestination(JsonFormatter()) ,FileDestination(TextFormatter())
    Whenever you hear:
    "A and B vary independently" start thinking composition.   

5. Thread Safety: Multiple threads can call log() simultaneously. 
                    Thread-1:logger.info("hello")
                    Thread-2:logger.info("world")
                    What must NOT happen: The bytes got interleaved.
                            hewo
                            llrld
                            o
                    What is allowed: 
                            hello
                            world
                    or
                            hello
                            world

                    No strict global ordering, one complete record is written atomically.
                    So every destination will probably have its own lock.

6. Static Configuration:Configured once at startup.
        logger = Logger(
        destinations=[
            ConsoleDestination(...),
            FileDestination(...)
        ]
    )

7. Future Extensibility:Design should not block adding remote destinations later.
    .'. Destination should be an interface
























