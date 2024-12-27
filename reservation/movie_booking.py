from movie_schedule import generate_schedule, load_config
from datetime import datetime, timedelta

class MovieBookingApp:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = load_config(config_file)
        self.schedule = self.load_schedule()
        print(self.schedule)
        self.bookings = {}
        self.auditorium_seats = {aud["room"]: aud["seats"] for aud in self.config["auditoriums"]}

    def load_schedule(self):
        """
        Generate the schedule for the next 3 days using the movie_schedule module.
        """
        try:
            days = 3  # Schedule for the next 3 days
            schedule = generate_schedule(self.config, days)
            if schedule is None:
                raise ValueError("Failed to generate schedule. Check your configuration.")
            return schedule
        except Exception as e:
            print(f"Error loading schedule: {e}")
            return {}

    def view_bookings(self):
        """
        View available showtimes for the next 3 days, including remaining seats.
        """
        if not self.schedule:
            print("No schedule available.")
            return

        print("\nAvailable Showtimes for the Next 3 Days:")
        for date, movies in self.schedule.items():
            print(f"Date: {date}")
            for movie, showings in movies.items():
                showtimes = []
                for showing in showings:
                    auditorium = showing['auditorium']
                    showtime = showing['showtime']
                    booked_seats = sum(
                        booking['tickets'] for booking in self.bookings.values()
                        if booking['auditorium'] == auditorium and booking['date'] == date and booking['showtime'] == showtime
                    )
                    remaining_seats = self.auditorium_seats[auditorium] - booked_seats
                    showtimes.append(f"{showtime} (Seats left: {remaining_seats})")
                showtimes_str = ", ".join(showtimes)
                print(f"  * {movie}: {showtimes_str}")

    def book_ticket(self):
        """
        Allow a user to book tickets for a selected movie and showtime.
        """
        day = int(input("Enter the day (1-3) you want to book: "))
        if day < 1 or day > 3:
            print("Invalid day. Please select between 1 and 3.")
            return

        date = (datetime.today().date() + timedelta(days=day - 1)).strftime("%Y-%m-%d")
        movies = list(self.schedule[date].keys())
        for idx, movie in enumerate(movies, start=1):
            print(f"{idx}. {movie}")
        movie_choice = int(input("Select a movie (1-{len(movies)}): "))
        if movie_choice < 1 or movie_choice > len(movies):
            print("Invalid movie selection.")
            return

        movie = movies[movie_choice - 1]
        showtimes = self.schedule[date][movie]
        for idx, showing in enumerate(showtimes, start=1):
            print(f"{idx}. {showing['showtime']} (Auditorium {showing['auditorium']})")
        showtime_choice = int(input(f"Select a showtime (1-{len(showtimes)}): "))
        if showtime_choice < 1 or showtime_choice > len(showtimes):
            print("Invalid showtime selection.")
            return

        showtime = showtimes[showtime_choice - 1]
        auditorium = showtime['auditorium']
        showtime_str = showtime['showtime']

        tickets_input = input("Enter the number of Adult, Child, Senior tickets (comma-separated): ")
        try:
            adult, child, senior = map(int, tickets_input.split(","))
        except ValueError:
            print("Invalid input. Please enter three comma-separated integers.")
            return

        matinee = int(showtime_str.split(":")[0]) < 17
        ticket_prices = self.config['pricing']
        total_price = (
            (adult * ticket_prices['matinee'] if matinee else adult * ticket_prices['adult']) +
            (child * ticket_prices['child']) +
            (senior * ticket_prices['senior'])
        )

        booked_seats = sum(
            booking['tickets'] for booking in self.bookings.values()
            if booking['auditorium'] == auditorium and booking['date'] == date and booking['showtime'] == showtime_str
        )
        remaining_seats = self.auditorium_seats[auditorium] - booked_seats

        total_tickets = adult + child + senior
        if total_tickets > remaining_seats:
            print(f"Not enough seats available. Only {remaining_seats} left.")
            return

        name = input("Enter your name to secure the booking: ")
        self.bookings[name] = {
            "date": date,
            "movie": movie,
            "showtime": showtime_str,
            "auditorium": auditorium,
            "tickets": total_tickets
        }

        print(f"Booking successful for {name}! Total price: ${total_price:.2f}")

    def view_individual_bookings(self):
        """
        View all individual bookings.
        """
        if not self.bookings:
            print("No bookings found.")
            return

        print("\nBookings Summary:")
        for name, booking in self.bookings.items():
            print(f"{name} - {booking['tickets']} tickets for {booking['movie']} on {booking['date']} at {booking['showtime']} (Auditorium {booking['auditorium']})")

    def run(self):
        while True:
            print("\n--- Movie Booking App ---\n1. View Available Showtimes\n2. Book a Ticket\n3. View Bookings\n4. Exit")
            choice = input("Enter your choice: ")
            actions = {
                "1": self.view_bookings,
                "2": self.book_ticket,
                "3": self.view_individual_bookings,
                "4": lambda: print("Thank you for using the Movie Booking App. Goodbye!") or exit()
            }
            action = actions.get(choice, lambda: print("Invalid choice, please try again."))
            action()

if __name__ == "__main__":
    app = MovieBookingApp("movies.yaml")
    app.run()
