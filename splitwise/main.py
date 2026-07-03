from __future__ import annotations
from uuid import uuid4
from random import random
from typing import Optional, Any
from abc import ABC, abstractmethod
from collections import defaultdict
import heapq
import threading


class SplitStrategy(ABC):
   @abstractmethod
   def calculate_expense(self, group:Group, expense: Expense)->dict[User, float]:
       pass
   
class EqualSplitStrategy(SplitStrategy):
    def calculate_expense(self, group:Group, expense: Expense)->dict[User, float]:
        members = group.get_members()
        paid_by = expense._paid_by
        amount = expense._amount
        if amount<= 0.0:
            raise ValueError("Amount should be positive.")
        split_amount = amount/len(members)
        user_map = {}
        for user in members:
            if user._id != paid_by._id:
                user_map[user] = split_amount
        return user_map

class ExactSplitStrategy(SplitStrategy):
    def calculate_expense(self, group:Group, expense: Expense)->dict[User, float]:
        user_map = {}
        paid_by = expense._paid_by
        splits = expense._splits
        total_split_amount = 0
        for split in splits:
            total_split_amount+=split.share
            if paid_by._id!=split.user._id:
                user_map[split.user] = split.share
        if total_split_amount!=expense._amount:
            raise ValueError("Paid amount and split amount mismatched")
        return user_map

    
class PercentageSplitStrategy(SplitStrategy):
    def calculate_expense(self, group:Group, expense: Expense)->dict[User, float]:
        paid_by = expense._paid_by
        amount = expense._amount
        splits = expense._splits
        user_map = {}
        total_percentage = 0
        for split in splits:
            total_percentage+=split.share
            if paid_by._id!=split.user._id:
                user_map[split.user] = (amount * split.share)/100
        if total_percentage!=100:
            raise ValueError("Incorrect percentage split.")
        return user_map
        
class Split:

    def __init__(self, user: User, share:float = 0.0):
        self.user:User= user
        self.share = share 

class Group:
    def __init__(self, name:str, userlist:list[User]):
        self._id = str(uuid4())
        self._name = name
        self._lock = threading.Lock()
        self.member_map:dict[str, User] = {}
        for user in userlist:
            self.member_map[user._id] = user

    def get_members(self) -> list[User]:
        return list(self.member_map.values())
    def is_member(self, user_id:str) ->bool:
        return user_id in self.member_map


class User:
    def __init__(self, name:str):
        self._id:str = str(uuid4())
        self._name = name

class Expense:
    def __init__(self, title:str, paid_by:User, amount:float,splits:list[Split], split_strategy:SplitStrategy):
        self._id = str(uuid4())
        self._title:str = title
        self._paid_by:User = paid_by
        self._amount:float = amount
        self._splits:Optional[list[Split]] = splits
        self._split_strategy:SplitStrategy = split_strategy


class SplitwiseService:
    def __init__(self):
        self.group_map:dict[str, Group] = {}
        self.user_map:dict[str, User] = {}
        self.balance_sheet:dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.expenses:dict[str, list[Expense]] = defaultdict(list)

    def create_group(self, group_name:str, user_list:list[User]):
        group = Group(group_name, user_list)
        self.group_map[group._id]=group

        for user in user_list:
            self.user_map[user._id] = user

        return group._id

    def create_expense(self, title:str, group_id:str, paid_by:User, amount:float,splits:list[Split], 
                       split_strategy:SplitStrategy):
        target_group = self.group_map.get(group_id)
        if not target_group:
            raise ValueError(f"Group id {group_id} does not exist.")
        if not target_group.is_member(paid_by._id):
            raise ValueError(f"User {paid_by._name} is not a member of a group {target_group._name}")
        
        for split in splits:
            if not target_group.is_member(split.user._id):
                raise ValueError(f"User {split.user._name} cannot be part of the split; they are not in the group.")

        expense  = Expense(title=title, paid_by=paid_by, amount=amount,splits=splits, split_strategy=split_strategy)
        
        with target_group._lock:
            self.expenses[group_id].append(expense)
            user_map:dict[User, float] = split_strategy.calculate_expense(self.group_map[group_id], expense)
            self.update_balance_sheet(paid_by, user_map)

    def update_balance_sheet(self, paid_by:User, user_map:dict[User, float]):
        for user, amount in user_map.items():
            self.balance_sheet[paid_by._id][user._id] += amount  # A owes B 200
            self.balance_sheet[user._id][paid_by._id] -= amount  # B owes A -200

    def settle(self):
        # need to right simplify logic here

        net_balance: dict[User, float] = defaultdict(float)

        for user, balances_with_other in self.balance_sheet.items():
            net_balance[user] = sum(balances_with_other.values())

        debtors = []
        creditors= []

        for user, balance in net_balance.items():
            if balance<-0.01:
                heapq.heappush(debtors, (balance, user))
            elif balance>0.01:
                heapq.heappush(creditors, (-balance, user))
        
        while debtors and creditors:
            debt_val, debtor_id = heapq.heappop(debtors)
            cred_val, creditor_id = heapq.heappop(creditors)
            debt_val, cred_val = abs(debt_val), abs(cred_val)
            settle_amount = min(cred_val,debt_val)

            debtor_name = self.user_map[debtor_id]._name
            creditor_name = self.user_map[creditor_id]._name
            print(f"{debtor_name} must pay {creditor_name} {settle_amount:.2f}")

            if debt_val > settle_amount: # If someone still owes or is owed money, push them back into the heap
                heapq.heappush(debtors, (-(debt_val - settle_amount), debtor_id))
            elif cred_val > settle_amount:
                heapq.heappush(creditors, (-(cred_val - settle_amount), creditor_id))

def main():
    sp_service = SplitwiseService()
    user_a = User("a")
    user_b = User("b")
    user_c = User("c")
    
    # 1. Create the Group
    gp_id = sp_service.create_group("Trip", [user_a, user_b, user_c])
    
    # 2. Add Expense 1: Lunch (Equal Split)
    # user_a pays 600. Everyone owes 200.
    sp_service.create_expense(
        title="Lunch", 
        group_id=gp_id, 
        paid_by=user_a, 
        amount=600.0, 
        splits=[], 
        split_strategy=EqualSplitStrategy()
    )
    
    # 3. Add Expense 2: Cab Ride (Exact Split)
    # user_b pays 300. user_a owes 100, user_c owes 200.
    exact_splits = [Split(user_a, 100.0), Split(user_c, 200.0)]
    sp_service.create_expense(
        title="Cab Ride", 
        group_id=gp_id, 
        paid_by=user_b, 
        amount=300.0, 
        splits=exact_splits, 
        split_strategy=ExactSplitStrategy()
    )
    
    # 4. Add Expense 3: Dinner (Equal Split)
    # user_c pays 300. Everyone owes 100.
    sp_service.create_expense(
        title="Dinner", 
        group_id=gp_id, 
        paid_by=user_c, 
        amount=300.0, 
        splits=[], 
        split_strategy=EqualSplitStrategy()
    )
    
    # 5. Process all expenses in the group and update the balance sheet
    print("Processing expenses...")
    
    # 6. Run the Greedy Settlement Algorithm
    sp_service.settle()

if __name__ == "__main__":
    main()


        



        
