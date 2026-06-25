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
