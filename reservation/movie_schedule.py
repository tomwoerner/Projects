import yaml
from datetime import datetime, timedelta
import random
import math

def load_config(config_file):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def round_to_next_5min(dt):
    minutes = dt.minute
    rounded_minutes = math.ceil(minutes / 5) * 5
    
    if rounded_minutes == 60:
        return dt.replace(minute=0) + timedelta(hours=1)
    return dt.replace(minute=rounded_minutes)

def get_showtimes(runtime, open_time, close_time):
    showtimes = []
    # Add 5 minutes padding before showtime and round to next 5 min interval
    current_time = round_to_next_5min(open_time + timedelta(minutes=5))
    
    while current_time + timedelta(minutes=runtime) <= close_time:
        showtimes.append(current_time)
        # Move to next potential showtime and round up
        next_time = round_to_next_5min(current_time + timedelta(minutes=runtime))
        if next_time <= current_time:  # Prevent infinite loop
            current_time = next_time + timedelta(minutes=5)
        else:
            current_time = next_time
    return showtimes

def is_timeslot_available(showtime, runtime, auditorium_schedule):
    for scheduled_time in auditorium_schedule:
        movie_end_time = showtime + timedelta(minutes=runtime)
        scheduled_end_time = scheduled_time + timedelta(minutes=runtime)
        if not (movie_end_time <= scheduled_time or showtime >= scheduled_end_time):
            return False
    return True

# Rest of the code remains exactly the same from here...

def generate_schedule(config, days):
    today = datetime.today().date()
    schedule = {}

    # Initialize schedule structure
    for i in range(days):
        day = today + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        schedule[day_str] = {}

    # Track auditorium schedules across all movies
    auditorium_schedules = {day_str: {aud["room"]: [] for aud in config["auditoriums"]} 
                           for day_str in schedule.keys()}

    for day_str in schedule.keys():
        day = datetime.strptime(day_str, "%Y-%m-%d").date()
        
        # Get operating hours for the day
        day_name = day.strftime("%A")
        if day_name in ["Monday", "Tuesday", "Wednesday", "Thursday"]:
            hours = next(h for h in config["hours"] if h["day"] == "Weekday")
        else:
            hours = next(h for h in config["hours"] if h["day"] == "Weekend")

        open_time = datetime.strptime(hours["open"], "%H:%M").replace(year=day.year, month=day.month, day=day.day)
        close_time = datetime.strptime(hours["close"], "%H:%M").replace(year=day.year, month=day.month, day=day.day)

        # Group movies by their release window
        movies_by_window = {"0-2": [], "3-4": [], "5+": []}
        
        for movie in config["movies"]:
            release_date = datetime.strptime(str(movie["release_date"]), "%Y-%m-%d").date()
            weeks_count = movie["weeks"]
            
            if day < release_date or day > release_date + timedelta(weeks=weeks_count):
                continue
                
            weeks_since_release = (day - release_date).days // 7 + 1
            
            if weeks_since_release <= 2:
                movies_by_window["0-2"].append(movie)
            elif weeks_since_release <= 4:
                movies_by_window["3-4"].append(movie)
            else:
                movies_by_window["5+"].append(movie)

        # Schedule minimum required showings for each movie
        for window, movies in movies_by_window.items():
            if not movies:
                continue

            # Sort movies by release date (newest first)
            movies.sort(key=lambda x: datetime.strptime(str(x["release_date"]), "%Y-%m-%d").date(), reverse=True)
            
            for movie in movies:
                title = movie["title"]
                runtime = movie["runtime"]
                
                if title not in schedule[day_str]:
                    schedule[day_str][title] = []

                all_showtimes = get_showtimes(runtime, open_time, close_time)
                random.shuffle(all_showtimes)

                # Set minimum required showings based on release window
                min_showings = 1  # For 5+ weeks
                if window == "0-2":
                    min_showings = 3
                elif window == "3-4":
                    min_showings = 2

                # Schedule minimum required showings
                showings_scheduled = 0
                for showtime in all_showtimes:
                    if showings_scheduled >= min_showings:
                        break

                    for auditorium in config["auditoriums"]:
                        room = auditorium["room"]
                        if is_timeslot_available(showtime, runtime, auditorium_schedules[day_str][room]):
                            auditorium_schedules[day_str][room].append(showtime)
                            schedule[day_str][title].append({
                                "auditorium": room,
                                "showtime": showtime.strftime("%H:%M")
                            })
                            showings_scheduled += 1
                            break

                # If we couldn't schedule minimum required showings, return None
                if showings_scheduled < min_showings:
                    print(f"Could not schedule minimum required showings for {title} on {day_str}")
                    return None

        # After meeting minimum requirements, fill remaining slots with priority order:
        # 1. Get week 3-4 movies to 3 showings if possible
        # 2. Then prioritize week 0-2 movies for remaining slots
        
        # First, try to get week 3-4 movies to 3 showings
        if movies_by_window["3-4"]:
            for movie in movies_by_window["3-4"]:
                title = movie["title"]
                runtime = movie["runtime"]
                current_showings = len(schedule[day_str][title])
                
                if current_showings < 3:  # Try to get to 3 showings
                    remaining_showtimes = get_showtimes(runtime, open_time, close_time)
                    random.shuffle(remaining_showtimes)

                    for showtime in remaining_showtimes:
                        if len(schedule[day_str][title]) >= 3:
                            break
                            
                        for auditorium in config["auditoriums"]:
                            room = auditorium["room"]
                            if is_timeslot_available(showtime, runtime, auditorium_schedules[day_str][room]):
                                auditorium_schedules[day_str][room].append(showtime)
                                schedule[day_str][title].append({
                                    "auditorium": room,
                                    "showtime": showtime.strftime("%H:%M")
                                })
                                break

        # Then fill remaining slots with week 0-2 releases
        if movies_by_window["0-2"]:
            for movie in movies_by_window["0-2"]:
                title = movie["title"]
                runtime = movie["runtime"]
                
                remaining_showtimes = get_showtimes(runtime, open_time, close_time)
                random.shuffle(remaining_showtimes)

                for showtime in remaining_showtimes:
                    for auditorium in config["auditoriums"]:
                        room = auditorium["room"]
                        if is_timeslot_available(showtime, runtime, auditorium_schedules[day_str][room]):
                            auditorium_schedules[day_str][room].append(showtime)
                            schedule[day_str][title].append({
                                "auditorium": room,
                                "showtime": showtime.strftime("%H:%M")
                            })
                            break

    return schedule

if __name__ == "__main__":
    config = load_config("movies.yaml")
    while True:
        try:
            days = int(input("Enter the number of days to generate the schedule for: "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    schedule = None
    while schedule is None:
        schedule = generate_schedule(config, days)

    # Print schedule organized by date, then movies
    for date, movies in schedule.items():
        print(f"\nDate: {date}")
        for movie, showings in movies.items():
            print(f"  Movie: {movie}")
            # Sort showings by time
            sorted_showings = sorted(showings, key=lambda x: x['showtime'])
            for showing in sorted_showings:
                print(f"    Auditorium: {showing['auditorium']}, Showtime: {showing['showtime']}")