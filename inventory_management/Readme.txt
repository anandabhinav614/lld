An inventory management system tracks product stock across multiple warehouse locations. 
When inventory arrives, the system records it. When orders ship, the system deducts stock. 
The system can also transfer inventory between locations and alert managers when stock runs low.

fix set of warehouses

low-stock aleart->It should be per product per warehouse. 
    Different warehouses might need different thresholds for the same product. 
    When stock drops below the threshold, trigger a notification.

Alerts are warehouse-specific, not global. A product could be low in Warehouse A but fine in Warehouse B.

keep notification strategy:
     Are we sending emails, calling a webhook, or just returning something to the caller?
     Let's keep it pluggable. 
     The system should call some callback interface when stock is low. 
     What happens after that - email, webhook, logging - is someone else's problem.
     We're building the alert mechanism, not the notification delivery

Stock can't go negative

Multiple operations could be happening simultaneously 
    - one warehouse receiving a shipment 
    while another is fulfilling an order for the same product. 
    Make sure operations are thread-safe.

Are we managing product catalogs, handling orders, that kind of thing?
Yes. Products exist externally


Final FR:
Requirements:
1. Track inventory for products across multiple warehouses
2. Add stock to a specific warehouse (receiving shipments)
3. Remove stock from a specific warehouse (fulfilling orders)
4. Check availability: given a product and quantity, return which warehouses can fulfill it
5. Transfer stock between warehouses
6. Low-stock alerts
7. Reject operations that would result in negative inventory
8. System must be thread-safe to handle concurrent operations

Out of Scope:
- Product catalog management (products exist externally)
- Order processing / payment / serviceability
- Persistence

Entites:
Product- how many units of product X are in warehouse Y.
        Product is a key (string or integer) that identifies what we're counting, not a class with behavior

Warehouse - This is definitely an entity. 
            A warehouse holds inventory for multiple products, 
            tracks how many units of each product it has, 
            and knows when to fire alerts. 
            It needs to enforce the "no negative stock" rule to prevent operations that would leave quantities below zero. 
            It also needs to check its alert configurations after every stock change 
            and fire notifications when thresholds are crossed.

InventoryManager - Something needs to orchestrate the whole system.
                    transfer 50 units of product X from Warehouse A to Warehouse B
                    which warehouses can fulfill an order for 100 units of product Y

AlertConfig - When we configure a low-stock alert, we're defining two pieces of information: 
                a threshold (when should we alert?) and a callback (what should we do?). 
                This combination is worth modeling as a small value object rather than storing the pieces separately. 

AlertListener - The "what to do when stock is low" part. 
                This should be an interface so different implementations can handle notifications in different ways. 
                One implementation might send email. 
                Another might call a webhook. 
                A third might just log to a file. 
                The inventory system doesn't know or care which notification mechanism gets used. 
                It just calls the interface method when stock drops below a threshold.


You usually fire alert logic on both add and remove because both operations can change whether an alert should fire, 
but the actual low stock notification only fires on the downward crossing.

So your instinct is mostly right. A low stock alert should not fire just because you added stock. 
But addStock should still call getAlertsToFire(previousQty, newQty) so the same threshold crossing 
logic stays centralized and resettable. If stock goes from 5 to 15, no alert fires, 
but now the system is reset so a later drop from 15 to 9 can fire again. 
The alerts_to_fire variable is just collecting any alerts after the update. 


AlertListener is the interface with something like onLowStock(...). It defines what to call when an alert happens.
AlertConfig is the stored setup for a product. It usually holds the threshold plus the listener. You can think of it as the rule you registered.

