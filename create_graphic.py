import subprocess

from util import find_min_dist_to_connect_without_overlapping
from rect import *


DISTRIBUTION_STRATEGY = force_strategy

BAR_TEMPLATE_PATH = 'bar.template.html'
OUT_PATH = 'bar.html'


def main():
    rects = DISTRIBUTION_STRATEGY()
    rects.sort(key=lambda x: (x.z, x.ty, x.lx))

    ascii_art = ''
    c = 0
    for y in range(CANVAS_HEIGHT):
        for x in range(CANVAS_WIDTH):
            occupied = max(e.contains_loc(x, y) for e in rects)
            ascii_art += ' .o0'[occupied] * 2
            c += int(bool(occupied))
        ascii_art += '\n'
    # print(ascii_art)
    coverage = c / (CANVAS_WIDTH * CANVAS_HEIGHT)
    print('Coverage: {}'.format(round(coverage * 100, 2)))

    light_length = sum(e.get_light_length() for e in rects)
    all_centers = sorted([(e.cx, e.cy) for e in rects])
    tl_center = all_centers.pop(0)
    light_length += find_min_dist_to_connect_without_overlapping(tl_center, all_centers)
    print('Lights (Squares Only): {}m'.format(round(light_length / 39.37, 2)))

    with open(BAR_TEMPLATE_PATH) as fin:
        bar_format = fin.read()
    rect_content = [e.as_html() for e in rects]
    rect_bg_content, rect_fg_content = zip(*rect_content)
    fcontent = bar_format.format(
        rect_bgs='\n'.join(rect_bg_content),
        rect_fgs='\n'.join(rect_fg_content),
        rects='\n'.join(f for e in rect_content for f in e)
    )
    with open(OUT_PATH, 'w+') as fout:
        fout.write(fcontent)
    subprocess.check_output('open {path}'.format(path=OUT_PATH), shell=True)


main()
