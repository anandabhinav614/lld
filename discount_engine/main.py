from uuid import uuid4
from abc import ABC, abstractmethod
from datetime import datetime


class Product:
    def __init__(self, name:str, price:int):
        self.id = str(uuid4())
        self.name = name
        self.price = price

class Cart:
    def __init__(self):
        self.id = str(uuid4())
        self.products:list[Product] = []
    
    def add_product(self, prdct:Product):
        self.products.append(prdct)
    def remove_product(self, prdct:Product) ->bool:
        for i in range(len(self.products)):
            if self.products[i].id == prdct.id:
                self.products.pop(i)
                return True
        return False

    def get_total(self)->float:
        total = 0.0
        for pr in self.products:
            total+=pr.price
        return total

class Coupon(ABC):
    def __init__(self, expiry, min_cart_val:int):
        self.id = str(uuid4())
        self.expiry = expiry
        self.is_active = True
        self.min_cart_val = min_cart_val

    def verify(self, cart_val):
        if not self.is_active:
            return False
        curr_time = datetime.now()
        if curr_time>=self.expiry:
            self.is_active = False
            return False
        elif cart_val<self.min_cart_val:return False
        return True

    @abstractmethod
    def calculate_discount(self, cart:Cart) -> float:
        pass

class FlatCoupon(Coupon):
    def __init__(self, discount_amount:int, expiry, min_cart_val:int):
        super().__init__(expiry, min_cart_val)
        self.discount_amount = discount_amount
    
    def calculate_discount(self, cart:Cart):
        total_cart_amount = cart.get_total()
        if not self.verify(total_cart_amount):
            return 0
        if total_cart_amount>self.discount_amount:
            return self.discount_amount
        return total_cart_amount
        
class PercentageCoupon(Coupon):
    def __init__(self, percentage:float, expiry, min_cart_val:int):
        super().__init__(expiry, min_cart_val)
        self.percentage = percentage
    
    def calculate_discount(self, cart:Cart) -> float:
        total_cart_amount = cart.get_total()
        if not self.verify(total_cart_amount):
            return 0
        return (total_cart_amount*self.percentage)/100
        
    
class PercentageWithCapCoupon(Coupon):
    def __init__(self, percentage:float, max_discount:int, expiry, min_cart_val:int):
        super().__init__(expiry, min_cart_val)
        self.percentage = percentage
        self.max_discount = max_discount

    def calculate_discount(self, cart:Cart) -> float:
        total_cart_amount = cart.get_total()
        if not self.verify(total_cart_amount):
            return 0
        discounted_amount = (total_cart_amount*self.percentage)/100
        if discounted_amount<=self.max_discount:
            return discounted_amount
        return self.max_discount

class Buy2Get1(Coupon):
    def __init__(self, expiry, min_cart_val, eligible_product:Product):
        super().__init__(expiry, min_cart_val)    
        self.eligible_product = eligible_product
    
    def calculate_discount(self, cart:Cart):
        total_cart_amount = cart.get_total()
        if not self.verify(total_cart_amount):
            return 0
        discounted_prdct_cnt = 0
        for prdct in cart.products:
            if prdct.id == self.eligible_product.id:
                discounted_prdct_cnt+=1
        free_item = discounted_prdct_cnt//3
        return free_item*self.eligible_product.price

class CheckoutService:
    def __init__(self):
        pass
    
    def calculate_final_price(self, cart:Cart, coupon:Coupon = None)->float:
        total = cart.get_total()
        if coupon is None:
            return total
        discount = coupon.calculate_discount(cart)
        return total-discount