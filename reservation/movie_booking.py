
class MovieBookingApp:
    def __init__(self):
        self.movies = {
            1: {"title": "Avatar", "seats": 10, "price": 15},           
            2: {"title": "Titanic", "seats": 8, "price": 12},
            3: {"title": "Avengers: Endgame", "seats": 5, "price": 18},
            4: {"title": "The Dark Knight", "seats": 7, "price": 14}
        }
        self.bookings = {}    
    def show_movies(self):
        print("\nAvailable Movies:")
        for movie_id, movie_info in self.movies.items():
            print(f"{movie_id}, {movie_info['title']} - {movie_info['seats']} seats available - ${movie_info['price']}")
    def book_ticket(self):    
        movie_id = int(input("Enter the movie ID you want to book: "))
        if movie_id not in self.movies:
            print("Invalid movie ID.")
            return
        if self.movies[movie_id]["seats"] > 0:    
            name = input("Enter your name: ")
            # check if this person already has a booking
            if name in self.bookings:
                previous_movie_title = self.bookings[name]["movie"]
                # undo previous seat decrement
                for prev_id, movie in self.movies.items():
                    if movie["title"] == previous_movie_title:
                        movie["seats"] += 1
                        break
            # make a new booking
            self.movies[movie_id]["seats"] -= 1
            self.bookings[name] = {
                "movie": self.movies[movie_id]["title"],
                "seats_left": self.movies[movie_id]["seats"],
                "price": self.movies[movie_id]["price"]
            }
            print(f"Booking successful! {name}, you have booked a ticket for {self.movies[movie_id]['title']}!")
        else:
            print("Sorry, no seats available for this movie.")
    def view_bookings(self):    
        if not self.bookings:
            print("No bookings found.")
        else:
            print("\nBookings Summary:")
            for name, booking_info in self.bookings.items():
                print(f"{name} - Movie: {booking_info['movie']} - Seats left: {booking_info['seats_left']} - Price: ${booking_info['price']}")
    def run(self):
        while True:
            print("\n--- Movie Booking App ---\n1. View Available Movies\n2. Book a Ticket\n3. View Bookings\n4. Exit")
            choice = input("Enter your choice: ")
            actions = {
                "1": self.show_movies,
                "2": self.book_ticket,
                "3": self.view_bookings,
                "4": lambda: print("Thank you for using the Movie Booking App. Goodbye!") or exit()
            }
            action = actions.get(choice, lambda: print("Invalid choice, please try again."))
            action()
if __name__ == "__main__":
    app = MovieBookingApp()
    app.run()