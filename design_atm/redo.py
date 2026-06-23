from uuid import uuid4
from abc import ABC, abstractmethod

class Card:
    def __init__(self, account_id, name, pin):
        self.card_id = str(uuid4())
        self.account_id = account_id
        self.name = name
        self.pin = pin

class CashDispenser:
    def __init__(self, balance:int):
        self.balance = balance
    
    def add_balance(self, amount):
        if amount<=0:
            raise ValueError("Deposit anount to atm cannot be -ve/0")
        self.balance+=amount

    def withdraw_balance(self, amount):
        if amount<=0:
            raise ValueError("Deposit anount to atm cannot be -ve/0")
        if self.balance<amount:
            raise ValueError("Not enuf balance")
        self.balance-=amount

class BankAccount:
    def __init__(self, name:str, balance:float):
        self.account_id = str(uuid4())
        self.balance = balance

class BankService:
    def __init__(self):
        self.accounts:dict[str, BankAccount] = {}
    
    def verify_pin(self, curr_card_pin:int, pin:int):
        return curr_card_pin == pin
    
    def get_account(self, account_id:str):
        return self.accounts.get(account_id, None)

    def withdraw(self, amount:float, account_id:str):
        account = self.get_account(account_id)
        if account.balance < amount:
            raise RuntimeError("Insufficient balance")

        account.balance -= amount

    def deposit(self, amount:float, account_id:str):
        self.accounts[account_id].balance+=amount
        
    def get_balance(self, account_id:str):
        account = self.get_account(account_id)
        if account is None:
            raise ValueError("No account found")
        return account.balance


class Transaction(ABC):
    @abstractmethod
    def execute(self):
        pass

class DepositTxn(Transaction):
    def __init__(self, amount):
        self.amount = amount
        
    def execute(self, atm:"ATM"):
        if self.amount<0:
            raise ValueError("Amount should be +ve")
        atm.cash_dispenser.add_balance(self.amount)
        atm.bank_service.deposit(self.amount, atm.curr_card.account_id)
        
class WithdrawTxn(Transaction):
    def __init__(self, amount):
        self.amount = amount
    def execute(self, atm:"ATM"):
        if self.amount<0:
            raise ValueError("Amount should be +ve")
        atm.cash_dispenser.withdraw_balance(self.amount)
        atm.bank_service.withdraw(self.amount, atm.curr_card.account_id)
        

class BalanceInquiry(Transaction):
    def execute(self, atm:"ATM"):
        balance = atm.bank_service.get_balance(atm.curr_card.account_id)
        return balance
    
class State(ABC):
    @abstractmethod
    def insert_card(self):
        pass
    @abstractmethod
    def enter_pin(self):
        pass
    @abstractmethod
    def select_txn(self):
        pass

class IdleState(State):
    def insert_card(self, atm:"ATM", card:Card):
        atm.curr_card = card
        atm.state = CardInsertState()
    
    def enter_pin(self, atm:"ATM", pin:int):
        raise RuntimeError("Invalid stae")

    def select_txn(self, atm:"ATM", txn:Transaction):
        raise RuntimeError("Invalid State")

class CardInsertState(State):
    def insert_card(self, atm:"ATM", card:Card):
        raise RuntimeError("Invalid stae")
    
    def enter_pin(self, atm:"ATM", pin:int):
        if atm.bank_service.verify_pin(atm.curr_card.pin, pin) is False:
            raise ValueError("Invalid Pin")
        atm.state = TxnState()

    def select_txn(self):
        raise RuntimeError("Invalid State")

class TxnState(State):
    def insert_card(self, atm:"ATM", card:Card):
        raise RuntimeError("Invalid stae")
    
    def enter_pin(self, atm:"ATM", pin:int):
        raise RuntimeError("Invalid stae")

    def select_txn(self, atm:"ATM", txn:Transaction):
        txn.execute(atm)
        atm.state = IdleState()
        atm.curr_card = None


class ATM:
    def __init__(self, bank_service:BankService, cash_dispenser:CashDispenser):
        self.state:State = IdleState()
        self.curr_card:Card =  None
        self.bank_service = bank_service
        self.cash_dispenser = cash_dispenser

    def insert_card(self, card:Card):
        if self.curr_card != None:
            raise RuntimeError("Card is already present")
        self.state.insert_card(self, card)

    def enter_pin(self, pin):
        self.state.enter_pin(self, pin)
    
    def select_txn(self, txn:Transaction):
        self.state.select_txn(self, txn)
    



        