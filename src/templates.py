"""Template definitions"""

import os

TEMPLATE_SQUARE = {
    'name': "square",
    'layout': [
        # ((size_x, size_y), (position_x, position_y)), position from top left
        [((660, 660), (40, 40))],
        [((660, 660), (740, 40))],
        [((660, 660), (40, 740))],
    ],
    'file': os.path.join(os.path.dirname(__file__), '../4x4.png')
}

TEMPLATE_SIZE = (535, 420)
TEMPLATE_STRIPS = {
    'name': "photo_strips",
    'layout': [
        # ((size_x, size_y), (position_x, position_y)), position from top left
        [(TEMPLATE_SIZE, (30, 30)), (TEMPLATE_SIZE, (625, 30))],
        [(TEMPLATE_SIZE, (30, 480)), (TEMPLATE_SIZE, (625, 480))],
        [(TEMPLATE_SIZE, (30, 930)), (TEMPLATE_SIZE, (625, 930))],
    ],
    'file': os.path.join(os.path.dirname(__file__), '../4x6.jpg')
}
