from enum import Enum
from uuid import uuid4
from datetime import datetime
from collections import defaultdict
import threading

class TxnType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

class TxnStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Account:
    def __init__(self, name):
        self.id = str(uuid4())
        self.name = name
        self.balance = 0
        self._lock = threading.Lock()


class Transaction:
    def __init__(self, acc_id:str, amount:int, txn_type:TxnType, status:TxnStatus, transfer_id:str = None):
        self.txn_id = str(uuid4())
        self.account_id = acc_id
        self.amount = amount
        self.txn_type = txn_type
        self.status = status
        self.timestamp = datetime.now()
        self.transfer_id = transfer_id

class InMemoryTxnStore:
    def __init__(self):
        self.db:dict[str, list[Transaction]]  = defaultdict(list)
    
    def add_txn(self, txn:Transaction):
        if txn.status == TxnStatus.SUCCESS:
            acc_id = txn.account_id
            self.db[acc_id].append(txn)

    def get_history(self, acc_id, page, size) -> list[Transaction]:
        txn_history =  self.db.get(acc_id, None)
        if txn_history:
            st = (page-1)*size
            ed = st+size
            return txn_history[st:ed]
        return []
    
class InMemoryAccountStore:
    def __init__(self):
        self.accounts:dict[str, Account] = {}
    
    def create_acc(self, name)->Account:
        new_acc = Account(name)
        self.accounts[new_acc.id] =  new_acc
        return new_acc
    
    def update_acc(self, acc_id, balance:int)->bool:
        acc = self.accounts.get(acc_id, None)
        if not acc: return False
        acc.balance = balance
        return True
    
    def get_balance(self, acc_id)->int:
        acc = self.accounts.get(acc_id, None)
        if not acc: return None
        return acc.balance

    
    def get_acc(self, acc_id:str)->Account:
        return self.accounts.get(acc_id, None)

class AccountService:
    # _instance = None
    # _lock = threading.Lock()

    # txn_store:InMemoryTxnStore
    # acc_store:InMemoryAccountStore

    # def __new__(cls):
    #     if cls._instance is None:
    #         with cls._lock:
    #             if cls._instance is None:
    #                 instance = super().__new__(cls)
    #                 instance.txn_store = InMemoryTxnStore()
    #                 instance.acc_store = InMemoryAccountStore()
    #                 cls._instance = instance
    #     return cls._instance

    def __init__(self):
        self.txn_store = InMemoryTxnStore()
        self.acc_store = InMemoryAccountStore()
    
    def create_account(self, name:str)->Account:
        return self.acc_store.create_acc(name)
    
    def withdraw(self, acc_id:str, amount:int)->Transaction:
        acc = self.acc_store.get_acc(acc_id)
        if not acc:
            raise Exception("Account does not exist.")
        with acc._lock:
            if amount>0:
                new_balance = acc.balance - amount
                if new_balance>=0:
                    new_txn = Transaction(acc_id, amount, TxnType.WITHDRAWAL, TxnStatus.SUCCESS)
                    self.acc_store.update_acc(acc_id, new_balance)
                else:
                    new_txn = Transaction(acc_id, amount, TxnType.WITHDRAWAL, TxnStatus.FAILED)
                self.txn_store.add_txn(new_txn)
                return new_txn
            else:
                raise Exception("Amount should be > 0")
        
    def deposit(self, acc_id:str, amount:int)->Transaction:
        acc = self.acc_store.get_acc(acc_id)
        if not acc:
            raise Exception("Account does not exist.")
        with acc._lock:
            if amount>0:
                new_balance = acc.balance + amount
                new_txn = Transaction(acc_id, amount, TxnType.DEPOSIT, TxnStatus.SUCCESS)
                self.acc_store.update_acc(acc_id, new_balance)
                self.txn_store.add_txn(new_txn)
                return new_txn
            else:
                raise Exception("Amount should be > 0")
        
    def transfer(self, from_acc:str, to_acc:str, amount:int)->list[Transaction]:
        if amount<=0:
            raise Exception("Amount should be > 0")
        if from_acc == to_acc:
            raise Exception("Provided account are same")
        f_acc = self.acc_store.get_acc(from_acc)
        t_acc = self.acc_store.get_acc(to_acc)

        if not f_acc or not t_acc:
            raise Exception("Account does not exists.")
        first, sec = None, None
        if f_acc.id < t_acc.id:
            first, second = f_acc, t_acc
        else:
            first, second = t_acc, f_acc
        
        with first._lock:
            with second._lock:
                # validate transfer
                transfer_id = str(uuid4())
                new_from_acc_bal = self.acc_store.get_balance(from_acc) - amount
                new_to_acc_bal =  self.acc_store.get_balance(to_acc)+amount
                if new_from_acc_bal<0:
                    raise Exception("From acc does not have enough balance")
                self.acc_store.update_acc(from_acc, new_from_acc_bal)
                self.acc_store.update_acc(to_acc, new_to_acc_bal)
                new_from_acc_txn = Transaction(from_acc, amount, TxnType.WITHDRAWAL, TxnStatus.SUCCESS, transfer_id)
                new_to_acc_txn = Transaction(to_acc, amount, TxnType.DEPOSIT, TxnStatus.SUCCESS, transfer_id)
                self.txn_store.add_txn(new_from_acc_txn)
                self.txn_store.add_txn(new_to_acc_txn)

                return [new_from_acc_txn, new_to_acc_txn] 
    
    def get_history(self, acc_id:str, page:int, size:int)->list[Transaction]:
        return self.txn_store.get_history(acc_id, page, size)

    

        

        
        
    

    