import yaml

class MovieBookingApp:
    def __init__(self, config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
        self.theater_seats = {
            1: 30,
            2: 30,
            3: 30,
            4: 30,
            5: 30
        }
        self.pricing = config["pricing"]
        self.movies = {}
        self.bookings = {}
        self.load_movies(config["movies"])

    def load_movies(self, movies):
        movie_id = 1
        for date, movie_list in movies.items():
            for movie in movie_list:
                title = movie["title"]
                runtime = movie["runtime"]
                showtimes = movie["showtimes"]
                for showtime in showtimes:
                    start_time = showtime["start_time"]
                    theater = showtime["theater"]
                    seats = self.theater_seats.get(theater, 30)  # Default to 30 seats for invalid theater numbers
                    self.movies[movie_id] = {
                        "date": date,
                        "title": title,
                        "runtime": runtime,
                        "theater": theater,
                        "start_time": start_time,
                        "seats": seats
                    }
                    movie_id += 1
        print("Movies loaded successfully.")

    def is_matinee(self, showtime):
        hour = int(showtime.split(":")[0])
        return hour < 17

    def show_movies(self):
        """
        Display available movies and their details.
        """
        movies_by_date = {}
        # group movies by date using a dictionary
        for movie_id, movie_info in self.movies.items():
            date = movie_info["date"]
            title = movie_info["title"]
            runtime = movie_info["runtime"]
            start_time = movie_info["start_time"]

            if date not in movies_by_date:
                movies_by_date[date] = {}

            if title not in movies_by_date[date]:
                movies_by_date[date][title] = {
                    "runtime": runtime,
                    "showtimes": []
                }
            movies_by_date[date][title]["showtimes"].append(start_time)

        print("\nAvailable Movies:")
        for date, movies in movies_by_date.items():
            print(f"Date: {date}") # split by date
            for title, info in movies.items():
                showtimes = []
                for showtime in info["showtimes"]:
                    price = self.pricing["matinee"] if self.is_matinee(showtime) else self.pricing["adult"]
                    showtimes.append(f"{showtime} (${price:.2f})")
                showtimes_str = ", ".join(showtimes) # join showtimes on one line
                print(f"  {title} ({info['runtime']} mins) - Showtimes: {showtimes_str}")

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
                print(f"{name} - Movie: {booking_info['movie']} (Date: {booking_info['date']}, Time: {booking_info['start_time']})")
                print(f"   Theater: {booking_info['theater']}")

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
    app = MovieBookingApp("movies.yaml")
    app.run()