import math
from datetime import datetime, timedelta
import yaml
from itertools import cycle

def load_config(config_file):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def round_to_next_5min(dt):
    minutes = dt.minute
    rounded_minutes = math.ceil(minutes / 5) * 5
    if rounded_minutes == 60:
        return dt.replace(minute=0) + timedelta(hours=1)
    return dt.replace(minute=rounded_minutes)

def is_weekend(day):
    return day.weekday() >= 5

def filter_active_movies(movies, start_date):
    active_movies = []
    for movie in movies:
        release_date = movie['release_date']
        # Handle both string and date object inputs
        if isinstance(release_date, str):
            release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
        end_date = release_date + timedelta(weeks=movie['weeks'])
        if release_date <= start_date and end_date > start_date:
            movie_copy = movie.copy()
            movie_copy['release_date'] = release_date
            active_movies.append(movie_copy)
    return active_movies

def assign_auditoriums(movies, auditoriums):
    # Sort movies by release date (newest first) and runtime (longer first) for tiebreaker
    movies.sort(key=lambda x: (x["release_date"], x["runtime"]), reverse=True)
    # Sort auditoriums by size rank (largest first)
    auditoriums.sort(key=lambda x: x["size_rank"])

    assignments = {movie["title"]: [] for movie in movies}
    
    # Assign dedicated auditoriums to all but the last two movies
    for i, movie in enumerate(movies[:-2]):
        assignments[movie["title"]].append(auditoriums[i]["room"])
    
    # Last two movies share the smallest auditorium
    if len(movies) >= 2:
        for movie in movies[-2:]:
            assignments[movie["title"]].append(auditoriums[-1]["room"])
    
    return assignments, movies[-2:] if len(movies) >= 2 else []

def generate_schedule(config, days=1, start_date=None):
    if not start_date:
        start_date = datetime.today().date()
    if not isinstance(days, int) or days < 1:
        days = 1

    schedule = {}
    pricing = config["pricing"]
    hours = config["hours"]
    auditoriums = config["auditoriums"]
    movies = filter_active_movies(config["movies"], start_date)

    # Get auditorium assignments and shared movies
    auditorium_assignments, shared_movies = assign_auditoriums(movies, auditoriums)
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        day_key = current_date.strftime("%Y-%m-%d")
        schedule[day_key] = []

        # Get operating hours
        is_weekend_day = is_weekend(current_date)
        open_time_str = next(h["open"] for h in hours if h["day"] == ("Weekend" if is_weekend_day else "Weekday"))
        close_time_str = next(h["close"] for h in hours if h["day"] == ("Weekend" if is_weekend_day else "Weekday"))
        
        # Add 5 minutes to opening time before first showing
        open_time = datetime.strptime(f"{day_key} {open_time_str}", "%Y-%m-%d %H:%M") + timedelta(minutes=5)
        close_time = datetime.strptime(f"{day_key} {close_time_str}", "%Y-%m-%d %H:%M")
        
        # Initialize all auditoriums to start at the rounded opening time
        first_showing = round_to_next_5min(open_time)
        auditorium_end_times = {aud["room"]: first_showing for aud in auditoriums}
        shared_auditorium = auditoriums[-1]["room"]
        current_shared_movie_index = 0

        # Keep scheduling until we can't fit any more movies
        while True:
            scheduled_any = False
            
            for movie in movies:
                title = movie["title"]
                runtime = timedelta(minutes=movie["runtime"])
                
                # For movies sharing an auditorium
                if movie in shared_movies:
                    # Skip if it's not this movie's turn
                    if movie != shared_movies[current_shared_movie_index]:
                        continue
                    
                    # Find next available start time in shared auditorium
                    next_start = round_to_next_5min(auditorium_end_times[shared_auditorium])
                    
                    # Check if we can schedule another showing (allowing it to start up to 5 min before close)
                    if next_start <= close_time - timedelta(minutes=5):
                        pricing_type = "matinee" if next_start.time() < datetime.strptime("18:00", "%H:%M").time() else "adult"
                        schedule[day_key].append({
                            "movie": title,
                            "auditorium": shared_auditorium,
                            "start_time": next_start.strftime("%H:%M"),
                            "pricing": pricing[pricing_type]
                        })
                        auditorium_end_times[shared_auditorium] = next_start + runtime + timedelta(minutes=5)
                        scheduled_any = True
                        
                        # Switch to the other shared movie
                        current_shared_movie_index = (current_shared_movie_index + 1) % len(shared_movies)
                
                # For movies with dedicated auditoriums
                else:
                    for auditorium in auditorium_assignments[title]:
                        next_start = round_to_next_5min(auditorium_end_times[auditorium])
                        
                        # Check if we can schedule another showing (allowing it to start up to 5 min before close)
                        if next_start <= close_time - timedelta(minutes=5):
                            pricing_type = "matinee" if next_start.time() < datetime.strptime("18:00", "%H:%M").time() else "adult"
                            schedule[day_key].append({
                                "movie": title,
                                "auditorium": auditorium,
                                "start_time": next_start.strftime("%H:%M"),
                                "pricing": pricing[pricing_type]
                            })
                            auditorium_end_times[auditorium] = next_start + runtime + timedelta(minutes=5)
                            scheduled_any = True
            
            # If we couldn't schedule any more movies, we're done for the day
            if not scheduled_any:
                break

    return schedule

def print_schedule(schedule):
    for date, shows in sorted(schedule.items()):
        print(f"Date: {date}")
        movies_schedule = {}
        
        # Group showtimes by movie
        for show in sorted(shows, key=lambda x: (x['movie'], x['start_time'])):
            movie = show['movie']
            if movie not in movies_schedule:
                movies_schedule[movie] = []
            movies_schedule[movie].append((show['auditorium'], show['start_time']))
        
        # Print grouped schedule
        for movie in sorted(movies_schedule.keys()):
            print(f"  Movie: {movie}")
            for auditorium, start_time in sorted(movies_schedule[movie], key=lambda x: x[1]):
                print(f"    Auditorium: {auditorium}, Showtime: {start_time}")

# Load configuration and generate schedule
config = load_config("movies.yaml")
schedule = generate_schedule(config, days=3, start_date=datetime(2024, 12, 25).date())

# Print the schedule in the desired format
print_schedule(schedule)

# Print the schedule
#import pprint
#pprint.pprint(schedule)
