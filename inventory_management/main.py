from collections import defaultdict
import threading
from abc import ABC, abstractmethod

class AlterListener(ABC):
   @abstractmethod
   def on_low_stock(self, warehouse_id:str, product_id:str, current_qty:int) -> None:
       pass

class EmailListener(AlterListener):
    def on_low_stock(self, warehouse_id, product_id, current_qty):
        subject = ""
        body = ""
        print(subject+'/n'+body)
        
class AlertConfig:
    def __init__(self, threshold:int, listener: AlterListener):
        self.threshold = threshold
        self.listener = listener

class AlertToFire:
    def __init__(self, listener: AlterListener, product_id:str, quantity:int):
        self.listener = listener
        self.product_id = product_id
        self.quantity = quantity
         

# Track inventory for products
# Low-stock alerts per product per warehouse
class Warehouse:
    def __init__(self, warehouse_id:str):
        self.warehouse_id = warehouse_id
        self.inventory:dict[str, int] = {}  #product_id:qty
        self.lock = threading.RLock()

        '''
        A product can have multiple alert configurations with different thresholds and different listeners.
        Maybe you want one alert at 50 units to send an email saying "order more soon," and 
        another alert at 10 units to page someone saying "critical shortage." 
        Storing a list of configurations per product supports this naturally.
        '''
        self.alert_configs:dict[str, list[AlertConfig]] = defaultdict(list)  # maps product IDs to lists of AlertConfig objects
        self.thresholds = {} # product_id -> threshold
    
    def add_stock(self, product_id:str, quantity:int):
        if quantity<=0:
            raise ValueError("Qty must be +ve.")
        alerts_to_fire:list[AlertToFire] = None
        with self.lock:
            prev_qty = self.inventory.get(product_id, 0)
            new_qty = prev_qty + quantity
            self.inventory[product_id] = new_qty
            alerts_to_fire = self._get_alerts_to_fire(product_id, prev_qty, new_qty)
        
        if alerts_to_fire:
            for alert in alerts_to_fire:
                alert.listener.on_low_stock(self.id, alert.product_id, alert.quantity)

    def remove_stock(self, product_id:str, quantity:int) -> bool:
        if quantity<=0:
            return False
        alerts_to_fire:list[AlertToFire] = None
        with self.lock:
            current_qty = self.inventory.get(product_id, 0)
            if current_qty < quantity:
                return False
            new_qty = current_qty - quantity
            self.inventory[product_id] = new_qty
            alerts_to_fire = self._get_alerts_to_fire(product_id, current_qty, new_qty)
        
        if alerts_to_fire:
            for alert in alerts_to_fire:
                alert.listener.on_low_stock(self.id, alert.product_id, alert.quantity)
        return True

    def get_stock(self, product_id:str) -> int:
        with self.lock:
            return self.inventory.get(product_id, 0)

    def check_availability(self, product_id:str, quantity:int) -> bool:
        if quantity<= 0:
            return False
        with self.lock:
            curr_qty = self.inventory.get(product_id, 0)
            return curr_qty >= quantity

    def set_low_stock_alert(self, product_id:str, threshold:int, listener:AlterListener):
        if threshold<= 0  or listener is None:
            raise ValueError("Invalid Params")
        
        with self.lock:
            self.alert_configs[product_id].append(AlertConfig(threshold, listener))

    # you need previous if you want to alert only when the threshold is crossed, not every time the stock is low
    def _get_alerts_to_fire(self, product_id:str, prev_qty:int, new_qty:int) ->list[AlertToFire]:
        configs = self.alert_configs.get(product_id, None)
        if configs == None:
            return None
        alerts_to_fire = []

        for config in configs:
            if prev_qty>=config.threshold and config.threshold>new_qty:
                alerts_to_fire.append(AlertToFire(config.listener, product_id, new_qty))
        
        if len(alerts_to_fire)==0:
            return None
        return alerts_to_fire

# Track inventory for products across multiple warehouses
# Add stock to a specific warehouse
# Transfer stock between warehouses
class InventoryManager:
    def __init__(self):
        self.warehouses:dict[str, Warehouse] = {}

    def add_stock(self, warehouse_id:str, product_id:str, quantity:int):
        if warehouse_id not in self.warehouses:
            raise ValueError("Warehouse Id not found")
        self.warehouses[warehouse_id].add_stock(product_id, quantity)

    def remove_stock(self, warehouse_id:str, product_id:str, quantity: str) -> bool:
        if warehouse_id not in self.warehouses:
            return False
        return self.warehouses[warehouse_id].remove_stock(product_id, quantity)

    def getWarehousesWithAvailability(self, product_id:str, quantity) ->list[str]:  # check availability across wahrehouses
        valid_warehouses = []
        for wh in self.warehouses.values():
            if wh.check_availability(product_id, quantity):
                valid_warehouses.append(wh.warehouse_id)
        return valid_warehouses

    def transfer(self, product_id, from_warehouse_id:str, to_warehouse_id:str, quantity) -> bool:
        if from_warehouse_id not in self.warehouses or to_warehouse_id not in self.warehouses:
            return False
        from_warehouse = self.warehouses[from_warehouse_id]
        to_warehouse = self.warehouses[to_warehouse_id]

        first_lock = min(from_warehouse_id, to_warehouse_id)
        second_lock = max(from_warehouse_id, to_warehouse_id)

        with self.warehouses[first_lock].lock:
            with self.warehouses[second_lock].lock:

                if not from_warehouse.check_availability(product_id, quantity):
                    return False
                # remove form from_warehouse
                if not from_warehouse.remove_stock(product_id, quantity):
                    return False
                to_warehouse.add_stock(product_id, quantity)
                return True
        
    def set_low_stock_alert(self, warehouse_id:str, product_id:str, threshold:int, listener:AlterListener):
        if warehouse_id not in self.warehouses:
            raise ValueError("Warehouse id not found")
        self.warehouses[warehouse_id].set_low_stock_alert(product_id, threshold, listener)

