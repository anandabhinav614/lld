Designing a Vending Machine

Requirements
    The vending machine should support multiple products with different prices and quantities.
    The machine should accept coins and notes of different denominations.
    The machine should dispense the selected product and return change if necessary.
    The machine should keep track of the available products and their quantities.
    The machine should handle multiple transactions concurrently and ensure data consistency.
    The machine should provide an interface for restocking products and collecting money.
    The machine should handle exceptional scenarios, such as insufficient funds or out-of-stock products.

Core Entitites
    Vending Machine
    Product
    Inventory
    Transaction
    Money(Coin/Note)

For simplicity I'm assuming unlimited change is available. 
If needed, I can extend this by maintaining denomination-wise inventory and implementing a change-dispensing algorithm.

Concurrency:
    If they confirm it's a single physical machine, then I'd say:
    "In that case, there is no user-level concurrency.
    The machine processes one transaction at a time, so I don't need synchronization around purchase flow."

    A physical vending machine processes one customer at a time, so I don't see customer-level concurrency. 
    The only synchronization I'd consider is between customer operations and administrative operations like restocking or collecting cash.

    Scenario 1: Last Coke
        Suppose inventory is: Coke -> 1
            Thread A: get_product_qty() -> 1
            Before it reduces quantity...
            Thread B: get_product_qty() -> 1
            Now both execute:reduce_quantity()
        Result: Coke -> -1
        or both users receive the same last product.
        This is the classic race condition.

    Scenario 2: Money
        Imagine:balance = 100
        Two successful purchases execute:
        vm.balance += product_price,  at the same time.
        Without synchronization, one update can be lost.

    What should we lock?
        Option A: Lock entire VendingMachine (Even buying different products blocks each other.)
        Option B: Inventory lock
        Option C: Lock per product -> Each product has its own lock.

    
    For your current design, if we assume a single customer at a time, I would not add any locks around:
        select_product()
        insert_amount()
        dispense_product()

        Those methods are effectively serialized by the hardware.

        The only places I'd consider synchronization are admin operations.

        For example:

        Customer                  Admin
        ---------                 ----------
        dispense_product()   ||   restock()

        Both modify: Inventory.quantities

        or

        Customer                  Admin
        ---------                 ----------
        dispense_product()   ||   collect_cash()

        Both modify: balance

        So the shared mutable resources are:
            Inventory
            Cash balance











