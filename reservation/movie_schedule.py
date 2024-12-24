import yaml
from datetime import datetime, timedelta

def load_config(config_file):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def get_showtimes(runtime, open_time, close_time, frequency):
    showtimes = []
    current_time = open_time
    while current_time + timedelta(minutes=runtime) <= close_time:
        showtimes.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=runtime + 10)  # 10 minutes break between showings
    return showtimes[:frequency]

def generate_schedule(config):
    today = datetime.today()
    schedule = {}

    for movie in config["movies"]:
        title = movie["title"]
        release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d")
        weeks_count = movie["weeks"]
        runtime = movie["runtime"]

        if today < release_date or today > release_date + timedelta(weeks=weeks_count):
            continue

        schedule[title] = {}
        for i in range(7):
            day = today + timedelta(days=i)
            day_name = day.strftime("%A")
            if day_name in ["Monday", "Tuesday", "Wednesday", "Thursday"]:
                hours = next(h for h in config["hours"] if h["day"] == "Weekday")
            else:
                hours = next(h for h in config["hours"] if h["day"] == "Weekend")

            open_time = datetime.strptime(hours["open"], "%H:%M").replace(year=day.year, month=day.month, day=day.day)
            close_time = datetime.strptime(hours["close"], "%H:%M").replace(year=day.year, month=day.month, day=day.day)

            weeks_since_release = (day - release_date).days // 7 + 1
            if weeks_since_release <= 2:
                frequency = len(config["auditoriums"]) * 3  # As often as possible
            elif weeks_since_release <= 4:
                frequency = 3  # Minimum 3 times each day
            else:
                frequency = 1  # Only once per day

            showtimes = get_showtimes(runtime, open_time, close_time, frequency)
            schedule[title][day.strftime("%Y-%m-%d")] = {
                "auditorium": [aud["room"] for aud in config["auditoriums"]],
                "showtimes": showtimes
            }

    return schedule

if __name__ == "__main__":
    config = load_config("movies.yaml")
    schedule = generate_schedule(config)
    for movie, days in schedule.items():
        print(f"Movie: {movie}")
        for day, info in days.items():
            print(f"  Date: {day}")
            print(f"  Auditorium: {info['auditorium']}")
            print(f"  Showtimes: {', '.join(info['showtimes'])}")