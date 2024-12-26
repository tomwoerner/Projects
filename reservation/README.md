The booking part is relatively easy. The scheduling is challenging based on getting the desired outcomes.

compiling my rules to reference later

movie scheduling rules:
* If start_date=none then use today
* If days=none or less than 1 or non numeric character then use =1
* If days=decimal then round up or down
* assign priority to each movie with priority=1 being highest priority, newest release. 
* If more than one movie share the same release date, then use greater budget as the tie-breaker.
* Compare auditorium count to movie count. If equal, assign each movie an auditorium, with highest priority getting largest auditorium determined by size_rank.
* If auditorium count less than movie count then:
  * if auditorium count 1 less than movie count, then two lowest priority movies share smallest auditorium.
  * if auditorium count 2 less than movie count, then next two lowest priority movies share second smallest auditorium.
* If auditorium count more than movie count then:
  * if auditorium count 1 more than movie count, then assign highest priority movie two largest auditoriums.
  * if auditorium count 2 more than movie count, then assign second highest priority movie next two largest auditoriums.
* if movie and auditorium count differ by more then 2, then leave some auditoriums empty or some movies without a showtime.
* Otherwise, each movie, regardless of priority, must receive a minimum of one showtime in the day.

Overall rules:
* there must be 5-minute break before the start of each showtime, including between open time and first showtime of the day.
* after 5 minute break has been added to each showtime, they must be rounded up to nearest 5 minute interval. such as :05, :10 ... through :55 :00
* if a movie is shown in two or more auditoriums, the spacing between showtimes must be at least 15 minutes. this may mean adding extra padding (break time).
* movies can start up until 5 minutes before closing time.
* Besides the spacing rule and breaktimes, the auditoriums must remain utilized, with scheduled showtimes.
* Obviously, movie showtimes (rounded(breaktime) + start_time + runtime) cannot overlap with each other.