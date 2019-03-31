"""Template definitions"""

TEMPLATE_SQUARE = {
    'layout': [
        # ((size_x, size_y), (position_x, position_y)), position from top left
        [((660, 660), (40, 40))],
        [((660, 660), (740, 40))],
        [((660, 660), (40, 740))],
    ],
    'file': '4x4.png'
}

TEMPLATE_SIZE = (630, 465)
TEMPLATE_STRIPS = {
    'layout': [
        # ((size_x, size_y), (position_x, position_y)), position from top left
        [(TEMPLATE_SIZE, (45, 45)), (TEMPLATE_SIZE, (765, 45))],
        [(TEMPLATE_SIZE, (45, 555)), (TEMPLATE_SIZE, (765, 555))],
        [(TEMPLATE_SIZE, (45, 1065)), (TEMPLATE_SIZE, (765, 1065))],
    ],
    'file': '4x6.jpg'
}
