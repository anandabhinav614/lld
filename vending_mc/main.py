from uuid import uuid4
from abc import ABC, abstractmethod
from enum import Enum

class Denomination(Enum):
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10
    TWENTY = 20
    FIFTY = 50
    HUNDRED = 100

class Product:
    def __init__(self, name:str, price:int):
        self.product_id = str(uuid4())
        self.product_name = name
        self.product_price = price

class Inventory:
    def __init__(self):
        self.products:dict[str, Product] = {} # product_id->Product
        self.quantities:dict[str, int] = {} 
    
    def add_product(self, product_name, product_price, quantity):
        new_product = Product(product_name, product_price)
        self.products[new_product.product_id] = new_product
        self.quantities[new_product.product_id] = quantity

    def print_inventory(self):
        # product id, product name. product price, product qty
        print("name, price, qty")
        for prd in self.products.values():
            print(f"{prd.product_name} {prd.product_price} {self.quantities[prd.product_id]}")
    
    def get_product(self, product_id:str):
        req_product =  self.products.get(product_id, None)
        if req_product is None:
            raise ValueError("Invalid product id")
        return req_product
    
    def get_product_qty(self, product_id:str):
        qty =  self.quantities.get(product_id, None)
        if qty is None:
            raise ValueError("Invalid product id")
        return qty
    
    def reduce_quantity(self, product_id):
        if self.quantities[product_id]<=0:
            raise ValueError("Out of stock")
        self.quantities[product_id]-=1

    def restock(self, product_id, qty):
        self.quantities[product_id]+=qty

class State(ABC):
    @abstractmethod
    def select_product(self, vm:"VendingMachine", product_id:str):
        pass
    @abstractmethod
    def insert_amount(self,vm:"VendingMachine", denom:Denomination, ):
        pass
    @abstractmethod
    def dispense(self, vm:"VendingMachine"):
        pass

class IdleState(State):
    def select_product(self, vm:"VendingMachine", product_id:str):
        if vm.selected_product_id is not None:
            raise RuntimeError("Invalid product is selected, pls reset()")
        if vm.inventory.get_product_qty(product_id)<=0:
            raise ValueError("Product unavailable, select another product")
        vm.selected_product_id = product_id
        vm.current_state = ProductSelectedState()
        
    def insert_amount(self, vm, denom):
        raise RuntimeError("Select product first")
        
    def dispense(self, vm):
        raise RuntimeError("Pls insert Money")

class ProductSelectedState(State):
    def select_product(self, vm, product_id):
        raise RuntimeError("Product already selected")
    
    def insert_amount(self, vm, denom):
        if vm.selected_product_id is None:
            raise RuntimeError("Select product first")
        vm.inserted_amount += denom.value

    def dispense(self, vm):
        if vm.selected_product_id is None:
            raise RuntimeError("Select product first")
        product = vm.inventory.get_product(vm.selected_product_id)
        if vm.inserted_amount< product.product_price:
            raise ValueError("Insufficient funds")
        vm.inventory.reduce_quantity(product.product_id)
        change = vm.inserted_amount - product.product_price
        vm.balance+=product.product_price
        vm.reset()
        return product, change



class VendingMachine:
    def __init__(self):
        self.inventory = Inventory()
        self.balance = 0
        self.current_state = IdleState()
        self.selected_product_id = None
        self.inserted_amount = 0
    
    def add_cash_balance(self, amount:int):
        self.balance+=amount
    
    def add_product(self, product_name, product_price, quantity):
        self.inventory.add_product(product_name, product_price, quantity)

    def select_product(self, product_id):
        self.current_state.select_product(self, product_id)
    
    def insert_amount(self, denom:Denomination):
        self.current_state.insert_amount(self, denom)

    def dispense_product(self):
        product, change = self.current_state.dispense(self)
        print(f"Take your product:{product.product_name}, change:{change}")

    def cancel_transaction(self):
        refund = self.inserted_amount
        self.reset()
        return refund
    
    def reset(self):
        self.inserted_amount = 0
        self.selected_product_id = None
        self.current_state = IdleState()

    def restock_product(self, product_id, qty):
        self.inventory.restock(product_id, qty)
    
