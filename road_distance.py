import math
from pykml import parser as kml_parser
from pykml.factory import nsmap
from shapely import geometry

namespace = {"ns": nsmap[None]}

EARTH_EQUITORIAL_RADIUS_METERS = 6378137
MIN_DISTANCE_ARTERIAL_M = 30
MIN_DISTANCE_HIGHWAY_M = 210


def process_line_string(coordinates: str) -> geometry.LineString:
    coord = []
    for raw in coordinates.split(' '):
        point = geometry.Point([float(i) for i in raw.split(',')])
        coord.append(point)

    return geometry.LineString(coord)


def load_line_strings_from_kml(filename: str) -> [geometry.LineString]:
    root = kml_parser.parse(filename).getroot()
    ls = []
    for elem in root.findall(".//ns:LineString", namespaces=namespace):
        ls.append(process_line_string(str(elem.coordinates)))
    return ls


def simple_deg_delta_to_distance(deg_distance: float, latitude_of_point: float, equitorial_radius: float) -> float:
    # https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
    skew = 0.99664719 * math.tan(latitude_of_point)
    return math.radians(deg_distance) * equitorial_radius * skew


def deg_to_closest_line(line_strings: [geometry.LineString], point: geometry.Point):
    shortest_deg = math.inf

    for ls in line_strings:
        distance_deg = ls.distance(point)
        if distance_deg < shortest_deg:
            shortest_deg = distance_deg

    return shortest_deg


def distance_to_closest_line_m(line_strings: [geometry.LineString], point: geometry.Point):
    return simple_deg_delta_to_distance(deg_to_closest_line(line_strings, point), point.y, EARTH_EQUITORIAL_RADIUS_METERS)


HIGHWAY_LINE_STRINGS = load_line_strings_from_kml("geodata/Highways/WSDOT_-_Functional_Class_Data_for_State_Routes.kml")
ARTERIAL_LINE_STRINGS = load_line_strings_from_kml("geodata/Arterials/WSDOT_-_Functional_Class_Data_for_Non-State_Routes.kml")


def check_distances(point: geometry.Point):
    distance_to_closest_highway = distance_to_closest_line_m(HIGHWAY_LINE_STRINGS, point)
    distance_to_closest_arterial = distance_to_closest_line_m(ARTERIAL_LINE_STRINGS, point)

    assert distance_to_closest_highway > MIN_DISTANCE_HIGHWAY_M, \
        f"closest highway is too close: {distance_to_closest_highway}m, minimum: {MIN_DISTANCE_HIGHWAY_M}"
    assert distance_to_closest_arterial > MIN_DISTANCE_ARTERIAL_M, \
        f"closest arterial is too close: {distance_to_closest_arterial}m, minimum: {MIN_DISTANCE_ARTERIAL_M}"


if __name__ == "__main__":
    home = geometry.Point(-122.3250276, 47.6236637)
    try:
        check_distances(home)
    except AssertionError as e:
        print(e)
