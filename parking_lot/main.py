from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4
import time
from collections import defaultdict
from threading import Lock

class VehicleSize(Enum):
    Small="Small"
    Medium="Medium"
    Large="Large"

class Vehicle(ABC):
    def __init__(self, licence_number, size:VehicleSize):
        self.licence_number = licence_number
        self.size = size
    
    def get_size(self):
        return self.size
    
    def get_licence_number(self):
        return self.licence_number

class Bike(Vehicle):
    def __init__(self, licence_number):
        super().__init__(licence_number, VehicleSize.Small)

class Car(Vehicle):
    def __init__(self, licence_number):
        super().__init__(licence_number, VehicleSize.Medium)

class Truck(Vehicle):
    def __init__(self, licence_number):
        super().__init__(licence_number, VehicleSize.Large)

class ParkingSpot:
    def __init__(self, spot_id:str, spot_size:VehicleSize):
        self.spot_id = spot_id
        self.spot_size = spot_size
        self.is_occupied = False
        self.parked_vehicle = None
        self.lock = Lock()
    
    def get_spot_size(self):
        return self.spot_size

    def is_spot_occupied(self):
        return self.is_occupied
    
    def can_fit(self, vehicle:Vehicle):
        if self.is_occupied: return False
        if vehicle.get_size() == VehicleSize.Small:
            return self.spot_size == VehicleSize.Small
        if vehicle.get_size() ==  VehicleSize.Medium:
            return self.spot_size == VehicleSize.Medium or self.spot_size == VehicleSize.Large
        if vehicle.get_size() ==  VehicleSize.Large:
            return self.spot_size == VehicleSize.Large 
        else:
            return False
    
    def park_vehicle(self, vehicle:Vehicle):
        with self.lock:
            if not self.can_fit(vehicle):
                raise ValueError("this vehicle cannot be parked here")
            self.parked_vehicle = vehicle
            self.is_occupied = True 

    def unpark_vehicle(self):
        with self.lock:
            if not self.is_occupied:
                raise ValueError("Spot is already unoccupied.")
            self.parked_vehicle = None
            self.is_occupied = False

class FeeStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, parking_ticket:"ParkingTicket") -> float:
        pass

class FlatRateFeeStrategy(FeeStrategy):
    RATE_PER_HOUR = 10.0
    def calculate_fee(self, parking_ticket):
        duration = parking_ticket.get_exit_time()-parking_ticket.get_entry_time()
        hours = (duration//(1000*60*60))+1
        return hours*self.RATE_PER_HOUR

class ParkingFloor:
    def __init__(self, floor_number:int):
        self.floor_number=floor_number
        self.spots:list[ParkingSpot] = []

    def add_spot(self, parking_spot:ParkingSpot):
        self.spots.append(parking_spot)
    
    def find_available_spot(self, vehicle:Vehicle):
        for spot in self.spots:
            if spot.can_fit(vehicle):
                return spot
        return None

    def display_available(self):
        availbe_spots = defaultdict(int)
        for spot in self.spots:
            if not spot.is_spot_occupied():
                availbe_spots[spot.get_spot_size()]+=1
        
        for spot, siz in availbe_spots.items():
            print(f"{spot.value}-> {siz}")

class ParkingTicket:
    def __init__(self, vehicle:Vehicle, spot:ParkingSpot):
        self.ticket_id = str(uuid4())
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = int(time.time()*1000)
        self.exit_time = 0
    
    def set_exit_timestamp(self):
        self.exit_time = int(time.time()*1000)
    
    def get_spot(self):
        return self.spot
    
    def get_entry_time(self):
        return self.entry_time
    
    def get_exit_time(self):
        return self.exit_time

class ParkingLot:
    def __init__(self):
        self.floors:list[ParkingFloor] = []
        self.active_tickets:dict[str, ParkingTicket] = {}
        self.fee_strategy = None
        self.lock = Lock()
    
    def set_fee_strategy(self, fee_strategy:FeeStrategy):
        self.fee_strategy = fee_strategy
    
    def add_floor(self, floor:ParkingFloor):
        self.floors.append(floor)
    
    def park_vehicle(self, vehicle:Vehicle):
        # first check is any spot is availabe in any 
        with self.lock:
            if vehicle.get_licence_number() in self.active_tickets:
                raise ValueError("Vehicle already parked.")
            self.active_tickets[vehicle.get_licence_number()] = None
        for floor in self.floors:
            while True:
                spot = floor.find_available_spot(vehicle)
                if spot is None:
                    break
            
                try:
                    spot.park_vehicle(vehicle)
                    ticket = ParkingTicket(vehicle, spot)
                    with self.lock:
                        self.active_tickets[vehicle.get_licence_number()] = ticket
                    return ticket
                except ValueError:
                    # Another thread occupied this spot.
                    continue
        with self.lock:
            self.active_tickets.pop(vehicle.get_licence_number(), None)
        return None

    def unpark_vehicle(self, licence_number:str):
        with self.lock:
            ticket = self.active_tickets.pop(licence_number, None)

        if ticket is None:
            raise ValueError("Invalid licence number")
        
        ticket.get_spot().unpark_vehicle()
        ticket.set_exit_timestamp()
        fee = self.fee_strategy.calculate_fee(ticket)
        return fee

def main():
    parking_lot = ParkingLot()
    parking_lot.set_fee_strategy(FlatRateFeeStrategy())
    floor1 = ParkingFloor(1)
    floor1.add_spot(ParkingSpot("F1-M1", VehicleSize.Medium))
    floor1.add_spot(ParkingSpot("F1-M2", VehicleSize.Medium))
    floor1.add_spot(ParkingSpot("F1-L1", VehicleSize.Small))
    floor1.add_spot(ParkingSpot("F1-H1", VehicleSize.Large))

    floor2 = ParkingFloor(2)
    floor2.add_spot(ParkingSpot("F2-M1", VehicleSize.Medium))
    floor2.add_spot(ParkingSpot("F2-M2", VehicleSize.Medium))
    floor2.add_spot(ParkingSpot("F2-L1", VehicleSize.Small))
    floor2.add_spot(ParkingSpot("F2-H1", VehicleSize.Large))

    parking_lot.add_floor(floor1)
    parking_lot.add_floor(floor2)
    
    bike = Bike("b-123")
    car = Car("C-123")
    truck = Truck("t-123")

    bike_ticket = parking_lot.park_vehicle(bike)
    car_ticket = parking_lot.park_vehicle(car)
    truck_ticket = parking_lot.park_vehicle(truck)

    floor1.display_available()
    floor2.display_available()

main()