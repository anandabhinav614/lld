Requirements:
    1. Users can search for movies by title
    2. Users can browse movies playing at a given theater
    3. Theaters have multiple screens; all screens share the same seat layout (rows A-Z, seats 0-20)
    4. Users can view available seats for a showtime and select specific ones
    5. Users can book multiple seats in a single reservation; booking returns a confirmation ID
    6. Concurrent booking of the same seat: exactly one succeeds
    7. Users can cancel a reservation by confirmation ID, releasing the seats

Entites:
Theater, Movie, Screen, Showtime, Reservation, Seat, BookingSystem 