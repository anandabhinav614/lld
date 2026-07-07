from uuid import uuid4
from datetime import datetime
from threading import RLock

class Movie:
    def __init__(self, title:str):
        self.movie_id = str(uuid4())
        self.title = title
    
    def get_id(self) ->str:
        return self.movie_id
    
    def get_title(self)->str:
        return self.title
    
class Reservation:
    def __init__(self, showtime:"ShowTime", seat_ids:list[str]):
        self.reservation_id = str(uuid4())
        self.showtime = showtime
        self.seat_ids = seat_ids
    
    def get_seat_ids(self):
        return self.seat_ids

    def get_showtime(self):
        return self.showtime
    
    def get_confirmation_id(self):
        return self.reservation_id

class ShowTime:
    def __init__(self, theater:"Theater", movie:Movie, dt:datetime, screen_label:str):
        self.showtime_id = str(uuid4())
        self.theater = theater
        self.movie = movie
        self.date_time = dt
        self.screen_label = screen_label
        self.reservations:list[Reservation] = []
        self.booked_seats = set(str)
        self.lock = RLock()

    def is_available(self, seat_id:str):
        if seat_id in self.booked_seats:
            return False
        return True
    
    def get_available(self)->list[str]:
        booked:set[str] = set()
        for reservation in self.reservations:
            for seat in reservation.get_seat_ids():
                booked.add(seat)
        
        available_seats:list[str] = []
        for row in range(ord("A"), ord("Z")+1):
            for col in range(0, 21):
                seat_id = chr(row)+str(col)
                if seat_id not in booked:
                    available_seats.append(seat_id)
        return available_seats
    
    def get_datetime(self):
        return self.date_time

    def book(self, reservation:Reservation) -> None:
        with self.lock:
            seat_ids = reservation.get_seat_ids()
            if not seat_ids:
                raise ValueError("Must select atleast one seat")
            
            for seat_id in seat_ids:
                if not self.is_valid_seat_id(seat_id):
                    raise ValueError(f"invalid seat: {seat_id}")
            
            for seat_id in seat_ids:
                if self.is_available(seat_id):
                    self.reservations.append(reservation)
                    self.booked_seats.add(seat_id)
                else:
                    raise ValueError("seat is already booked")

    def cancel(self, reservation:Reservation) -> None:
        with self.lock:
            self.reservations.remove(reservation)
            for seat in reservation.seat_ids:
                self.booked_seats.remove(seat)

    def get_id(self):
        return self.showtime_id

    def get_movie(self):
        return self.movie
    
    @staticmethod
    def is_valid_seat_id(seat_id:str) -> bool:
        if not seat_id or len(seat_id)<2:
            return False
        row = seat_id[0]
        try:
            col = int(seat_id[1:])
            return "A"<=row<="Z" and 0<=col<=20
        except ValueError:
            return False

class Theater:
    def __init__(self, theatre_name:str):
        self.theater_id = str(uuid4())
        self.theatre_name = theatre_name
        self.showtimes:list[ShowTime] = []
    
    def get_showtimes_for_movie(self, movie:Movie) -> list[ShowTime]:
        res = []
        for showtime in self.showtimes:
            if showtime.get_movie().get_id() == movie.get_id():
                res.append(showtime)
        return res
    
    def get_showtimes(self)->list[ShowTime]:
        return self.showtimes
    
class BookingSystem:
    def __init__(self, theaters:list[Theater]):
        self.theaters = theaters
        self.movies_by_id:dict[str, Movie] = {}
        self.showtimes_by_movie_id:dict[str, list[ShowTime]] ={}
        self.showtime_by_id:dict[str, ShowTime] ={}
        self.reservation_by_id:dict[str, Reservation] = {}

        for theater in theaters:
            for showtime in theater.get_showtimes():
                movie = showtime.get_movie()
                self.movies_by_id[movie.get_id()] = movie
                self.showtime_by_id[showtime.get_id()] = showtime

                if movie.get_id() not in self.showtimes_by_movie_id:
                    self.showtimes_by_movie_id[movie.get_id()] = []
                self.showtimes_by_movie_id[movie.get_id()].append(showtime)
    
    def search_movies(self, title:str) -> list[ShowTime]:
        if not title:
            return []
        
        result:list[ShowTime] = []
        search_lower = title.lower()
        now  =  datetime.now()

        for movie in self.movies_by_id.values():
            if search_lower in movie.get_title().lower():
                movie_showtimes=self.showtimes_by_movie_id.get(movie.get_id(), [])
                for showtime in movie_showtimes:
                    if showtime.get_datetime()>now:
                        result.append(showtime)
        return result

    def get_showtime_at_theater(self, theater:Theater) ->list[ShowTime]:
        if not theater:
            return []
        result:list[ShowTime] = []
        now = datetime.now()

        for showtime in theater.get_showtimes():
            if showtime.get_datetime()>now:
                result.append(showtime)
        
        return result

    def book(self, showtime_id:str, seat_ids:list[str]) -> Reservation:
        if not showtime_id or not seat_ids:
            raise ValueError("Invalid booking Req")
        
        showtime = self.showtime_by_id.get(showtime_id)
        if showtime is None:
            raise ValueError(f"Showtime not found:{showtime_id}")
        
        reservation = Reservation(
            showtime=showtime,
            seat_ids=seat_ids
        )

        showtime.book(reservation)

        self.reservation_by_id[reservation.get_confirmation_id()] = reservation
        return reservation

    def cancel_reservation(self, confirmation_id:str):
        if not confirmation_id:
            raise ValueError("Invalid confirmation id")
        
        reservation = self.reservation_by_id.get(confirmation_id)
        if reservation is None:
            raise ValueError(F"reservation not found: {confirmation_id}")
        showtime = reservation.get_showtime()
        showtime.cancel(reservation)

        del self.reservation_by_id[confirmation_id]

        
    
    
