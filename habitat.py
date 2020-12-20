from shapely import geometry

from road_distance import check_distances

if __name__ == "__main__":
    home = geometry.Point(-122.3250276, 47.6236637)
    try:
        check_distances(home)
    except AssertionError as e:
        print(e)
