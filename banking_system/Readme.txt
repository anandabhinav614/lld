Creating accounts.
Depositing money into an account.
Withdrawing money from an account.
Transferring money between accounts.
Checking account balance.
Viewing transaction history.

Constraints
Every account has a unique account number.
Balance can never go negative.
Transfer should be atomic.
Every successful operation should create a transaction record.
System is single-node and in-memory for now.


1. Enums
TxnType: DEPOSIT, WITHDRAWAL, TRANSFER
TxnStatus: SUCCESS, FAILED

2. Entities (Data Models)
Account
- id, - user_id, - currency: str
- balance: decimal/int
- status: AccountState

Transaction
- txn_id, - from_acc_id, - to_acc_id: str
- amount: float
- type: TxnType
- status: TxnStatus
- timestamp: datetime

3. Storage Layer (Repository)
InMemoryTxnStore
- _db: Dict[str, List[Transaction]]
+ add_transaction(txn: Transaction)
+ get_history(acc_id: str, limit: int, offset: int) -> List[Transaction]

InMemoryAccountStore
- accounts: Dict[str, Account]
+ create_account()
+ get_account()
+ update_account()

4. Service Layer (Business Logic)
AccountService
- _txn_store: InMemoryTxnStore
- _account_store:InMemoryAccountStore
create_account()
+ withdraw(acc_id: str, amount: float) -> Transaction
+ deposit(acc_id: str, amount: float) -> Transaction
+ transfer(from_acc_id: str, to_acc_id: str, amount: float) -> Transaction
+ get_history(acc_id: str, page: int, size: int) -> List[Transaction]