from common import *

from analyze_photos import *
from pagerank import *

def get_top_cameras():
    camera_scores_combined = aggregate_camera_scores()
    top_cameras = {}
    for category, camera_scores in camera_scores_combined.iteritems():
        sorted_scores = sorted(camera_scores.items(), key = lambda x: x[1], reverse = True)
        top_cameras[category] = sorted_scores[:3]

    return top_cameras
