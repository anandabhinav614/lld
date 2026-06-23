from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4


class Card:
    def __init__(self, card_no:int,account_id, pin:int, expiry):
        self.card_no = card_no
        self.account_id = account_id
        self.pin = pin
        self.expiry = expiry

class CashDispenser:
    def __init__(self, balance):
        self.balance = balance

    def dispense(self, amount):
        if amount > self.balance:
            raise Exception("ATM out of cash")

        self.balance -= amount


class Transaction(ABC):
    @abstractmethod
    def execute(self, atm):
        pass

class WithdrawTxn(Transaction):
    def __init__(self, amount):
        self.amount = amount
    
    def execute(self, atm:"ATM"):
        account_id = atm.current_card.account_id
        atm.cash_dispenser.dispense(self.amount)
        atm.bank_service.withdraw(account_id, self.amount)
        print(f"Dispensed {self.amount}")

class BalanceInquiryTxn(Transaction):

    def execute(self, atm):

        account_id = atm.current_card.account_id

        balance = atm.bank_service.get_balance(
            account_id
        )

        print(f"Balance = {balance}")

class ATMState(ABC):

    @abstractmethod
    def insert_card(self, atm:"ATM", card:Card):
        pass
    @abstractmethod
    def enter_pin(self, atm:"ATM", pin):
        pass
    @abstractmethod
    def select_transaction(self, atm:"ATM", txn_type):
        pass

class IdleState(ATMState):
    def insert_card(self, atm:"ATM", card:Card):
        atm.current_card = card
        atm.set_state(CardInsertedState())

    def enter_pin(self, atm:"ATM", pin):
        raise Exception("Insert card first")

    def select_transaction(self, atm:"ATM", txn_type):
        raise Exception("Insert card first")

class CardInsertedState(ATMState):

    def insert_card(self, atm:"ATM", card:Card):
        raise Exception("Card already inserted")

    def enter_pin(self, atm:"ATM", pin):
        # validate pin
        if not atm.bank_service.validate_pin(atm.current_card,pin):
            raise Exception("Invalid PIN")
        atm.set_state(AuthenticatedState())

    def select_transaction(self, atm:"ATM", txn_type):
        raise Exception("Enter PIN first")

class AuthenticatedState(ATMState):
    def insert_card(self, atm:"ATM", card):
        raise Exception("Card already inserted")

    def enter_pin(self, atm:"ATM", pin):
        raise Exception("Already authenticated")

    def select_transaction(self, atm:"ATM", txn):
        txn.execute(atm)
        atm.current_card = None
        atm.set_state(IdleState())

class BankAccount:
    def __init__(self, customer_id, account_balance):
        self.account_id = str(uuid4())
        self.customer_id = customer_id
        self.account_balance = account_balance

class BankService:
    def __init__(self):
        self.accounts:dict[str, BankAccount] = {}

    def add_account(self, account:BankAccount):
        self.accounts[account.account_id] = account

    def get_account(self, account_id:str) -> BankAccount:
        if account_id not in self.accounts:
            raise Exception("Account not found")

        return self.accounts[account_id]

    def validate_pin(self, card:Card, pin:int) -> bool:
        return card.pin == pin

    def get_balance(self, account_id:str) -> int:
        account = self.get_account(account_id)
        return account.account_balance

    def withdraw(self, account_id:str, amount:int):
        account = self.get_account(account_id)

        if account.account_balance < amount:
            raise Exception("Insufficient funds")

        account.account_balance -= amount

class Customer:
    def __init__(self, name):
        self.customer_id = str(uuid4())
        self.name = name
        self.cards:list[Card] = []
        self.accounts:list[BankAccount] = []

class ATM:
    def __init__(self, bank_service:BankService, cash_dispenser:CashDispenser):
        self.current_card = None
        self.state = IdleState()
        self.bank_service = bank_service
        self.cash_dispenser = cash_dispenser
    
    def insert_card(self, card):
        self.state.insert_card(self, card)
    
    def enter_pin(self, pin):
        self.state.enter_pin(self, pin)
    
    def select_transaction(self, txn_type):
        self.state.select_transaction(self, txn_type)
    
    def eject_card(self):
        self.current_card = None
        self.state = IdleState()
    
    def set_state(self, state):
        self.state = state





        

    