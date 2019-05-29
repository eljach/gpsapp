from .models import Position, Building
from geopy import distance

def FindVisits():
    for employee in Employee.objects.all():
        for building in Building.objects.all():
            positions_queryset = Position.objects.all(already_analyzed=False, employee=employee).order_by("date")
            building_location = building.get_location()
            start_at = 0

            while start_at <= positions_queryset.count():
                initial_position = positions_queryset[start_at]
                if distance.distance(initial_position.get_location(), building_location).feet < 300:
                    initial_position.already_analyzed = True
                    initial_position.save()
                    matching_position_arrival = start_at
                    counter = matching_position_arrival
                    distance_delta = 0
                    while distance_delta < 300:
                        counter += 1
                        position = positions_queryset[counter]
                        position_location = position.get_location()
                        distance_delta = distance.distance(position_location, building_location).feet
                        position.already_analyzed = True
                        position.save()

                    matching_position_departure = counter
                    arrival = positions_queryset[matching_position_arrival]
                    departure = positions_queryset[matching_position_departure]
                    time_on_site = departure - arrival
                    visit, created = Visit.objects.get_or_create(
                        building=building,
                        employee=employee,
                        arrival_time=arrival,
                        departure_time=departure,
                        time_on_site = time_on_site
                    )

                    start_at = matching_position_departure
                else:
                    start_at += 1
