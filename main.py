import sys

from data.business import find_businesses
from data.geocoder import get_coordinates
from data.mapapi_PG import show_map

toponym_to_find = " ".join(sys.argv[1:])

if toponym_to_find:
    toponym_lattitude, toponym_longitude = get_coordinates(toponym_to_find)
    address_ll = f"{toponym_lattitude},{toponym_longitude}"

    # Подбираем масштаб.
    delta = 0.01
    organizations = list()
    while delta < 100 and len(organizations) < 10:
        delta += 0.01
        spn = f"{delta},{delta}"
        organizations = find_businesses(address_ll, spn, "аптека")

    # Создаем список 10 аптек.
    pharmacies = list()
    for organization in organizations:
        point = organization["geometry"]["coordinates"]
        hours = organization["properties"]["CompanyMetaData"].get("Hours",
                                                                  None)
        if hours:
            available = hours["Availabilities"][0]
            around_the_clock = available.get(
                "Everyday", False) and available.get("TwentyFourHours", False)
        else:
            around_the_clock = None
        pharmacies.append((point, around_the_clock))

    # Добавляем на карту точки аптек.
    point_param = "pt=" + "~".join(
        [f'{point[0]},{point[1]},pm2'
         f'{"gn" if is_24x7 else ("lb" if not is_24x7 else "gr")}l'
         for point, is_24x7 in pharmacies])

    show_map(map_type="map", add_params=point_param)
