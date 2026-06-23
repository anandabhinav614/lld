Requirements
    Functional
        Insert card
        Authenticate using PIN
        Withdraw cash
        Check balance
        Deposit cash
        Transfer money
        Print receipt
        Eject card

    Non Functional
        Consistent account balance
        No double withdrawal
        Extensible for new transaction types
        Thread-safe cash inventory

Core Entities:
    ATM side
        ATM
        CashSlot / CashDispenser
        Card
        Screen
        Keypad

    Banking side
        BankAccount
        Customer
        BankService (validates card, updates balance)

    Transactions
        Withdraw
        Deposit
        BalanceInquiry

    State Management
        IdleState
        CardInsertedState
        AuthenticatedState
        TransactionState


