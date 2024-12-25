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

def get_days_until_expiration(movie_title, movies_config):
    """
    Calculate days until movie expiration.
    Returns negative number if expired.
    """
    movie = next((m for m in movies_config["movies"] if m["title"] == movie_title), None)
    if not movie:
        raise ValueError(f"Movie {movie_title} not found")
        
    release_date = movie["release_date"] if isinstance(movie["release_date"], datetime) else datetime.strptime(str(movie["release_date"]), "%Y-%m-%d")
    expiration_date = release_date + timedelta(days=movie["weeks"] * 7)
    days_remaining = (expiration_date - datetime.now()).days
    return days_remaining

def is_movie_expired(movie_title, movies_config):
    """Check if movie has expired based on release date and weeks running"""
    return get_days_until_expiration(movie_title, movies_config) < 0

def filter_active_movies(movies_config):
    """Return only non-expired movies"""
    return [m for m in movies_config["movies"] 
            if not is_movie_expired(m["title"], movies_config)]

def generate_schedule(config, days):
    today = datetime.today().date()
    schedule = {}
    
    for i in range(days):
        day = today + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        schedule[day_str] = {}
        
        day_name = day.strftime("%A")
        hours = next(h for h in config["hours"] if h["day"] == ("Weekday" if day_name in ["Monday", "Tuesday", "Wednesday", "Thursday"] else "Weekend"))
        
        open_time = datetime.strptime(hours["open"], "%H:%M").replace(year=day.year, month=day.month, day=day.day)
        close_time = datetime.strptime(hours["close"], "%H:%M").replace(year=day.year, month=day.month, day=day.day)
        
        # Filter for active and non-expired movies
        active_movies = [
            movie for movie in config["movies"]
            if (datetime.strptime(str(movie["release_date"]), "%Y-%m-%d").date() <= day <= 
                datetime.strptime(str(movie["release_date"]), "%Y-%m-%d").date() + timedelta(weeks=movie["weeks"]))
            and not is_movie_expired(movie["title"], config)
        ]
        
        # Sort by release date (newest first) and assign priorities
        active_movies.sort(key=lambda x: x["release_date"], reverse=True)
        
        # Group movies by release date to assign same priority
        priority_groups = {}
        current_priority = 1
        current_release_date = None
        
        for movie in active_movies:
            if movie["release_date"] != current_release_date:
                current_release_date = movie["release_date"]
                current_priority += 1
            priority_groups.setdefault(current_priority, []).append(movie)
        
        # Initialize auditorium schedules
        auditorium_schedules = {aud["room"]: [] for aud in config["auditoriums"]}
        
        # Schedule movies by priority until no more slots available
        while priority_groups:
            for priority in sorted(priority_groups.keys()):
                for movie in priority_groups[priority]:
                    title = movie["title"]
                    runtime = movie["runtime"]
                    
                    if title not in schedule[day_str]:
                        schedule[day_str][title] = []
                    
                    # Get possible showtimes
                    available_times = get_showtimes(runtime, open_time, close_time)
                    random.shuffle(available_times)
                    
                    # Try to schedule in any auditorium
                    scheduled = False
                    for showtime in available_times:
                        for auditorium in config["auditoriums"]:
                            room = auditorium["room"]
                            if is_timeslot_available(showtime, runtime, auditorium_schedules[room]):
                                auditorium_schedules[room].append(showtime)
                                schedule[day_str][title].append({
                                    "auditorium": room,
                                    "showtime": showtime.strftime("%H:%M")
                                })
                                scheduled = True
                                break
                        if scheduled:
                            break
                    
                    if not scheduled:  # No more slots available for this movie
                        priority_groups[priority].remove(movie)
                        if not priority_groups[priority]:
                            del priority_groups[priority]
                
            # Remove lowest priority after each round
            if priority_groups:
                max_priority = max(priority_groups.keys())
                del priority_groups[max_priority]
    
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