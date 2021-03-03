import math
import random

from const import *
from util import weighted_choice, calc_dist_between


RECT_BG_TEMPLATE_PATH = 'rect_bg.template.html'
RECT_FG_TEMPLATE_PATH = 'rect_fg.template.html'


grid = [(x, y) for x in range(1, CANVAS_WIDTH) for y in range(1, CANVAS_HEIGHT)]


class Rect:
    with open(RECT_BG_TEMPLATE_PATH) as fin:
        rect_bg_format = fin.read()
    with open(RECT_FG_TEMPLATE_PATH) as fin:
        rect_fg_format = fin.read()

    def __init__(self, cx, cy, radius, crop=True):
        self.cx, self.cy, self.radius = cx, cy, radius
        self.w = self.h = self.radius * 2
        self.z = random.randint(1, 3)

        self.lx = self.rx = self.ty = self.by = None
        self.update_derived_vals()

        if crop:
            self.crop_to_canvas_borders()

    def update_derived_vals(self):
        self.lx = self.cx - self.radius
        self.rx = self.cx + self.radius
        self.ty = self.cy - self.radius
        self.by = self.cy + self.radius

    def crop_to_canvas_borders(self):
        if self.lx < 0:
            self.w += self.lx
            self.lx = 0
        if self.rx > CANVAS_WIDTH:
            self.w += CANVAS_WIDTH - self.rx
            self.rx = CANVAS_WIDTH
        if self.ty < 0:
            self.h += self.ty
            self.ty = 0
        if self.by > CANVAS_HEIGHT:
            self.h += CANVAS_HEIGHT - self.by
            self.by = CANVAS_HEIGHT

    @property
    def c(self):
        return self.cx, self.cy

    def contains_loc(self, x, y):
        return self.z if self.lx <= x <= self.rx and self.ty <= y <= self.by else 0

    def collides_with(self, other):
        if self.cx == other.cx and self.cy == other.cy:
            return True
        if self.z != other.z:
            return False
        return not (self.by <= other.ty or other.by <= self.ty or self.lx >= other.rx or other.lx >= self.rx)

    def force(self, dx, dy):
        self.cx += dx
        self.cx = max(min(self.cx, CANVAS_WIDTH), 1)
        self.cy += dy
        self.cy = max(min(self.cy, CANVAS_HEIGHT), 1)
        self.update_derived_vals()

    def snap_to_grid(self):
        self.cx, self.cy = round(self.cx), round(self.cy)
        self.update_derived_vals()

    def as_html(self):
        return (
            Rect.rect_bg_format.format(
                x=self.lx * 8 - self.z + 6,
                y=self.ty * 8 - self.z + 8,
                w=self.w * 8 + self.z * 2,
                h=self.h * 8 + self.z * 2,
                color='blue',
                shadow='shadow' + str(self.z)
            ),
            Rect.rect_fg_format.format(
                x=self.lx * 8 + 6,
                y=self.ty * 8 + 8,
                w=self.w * 8,
                h=self.h * 8
            )
        )

    def get_light_length(self):
        return (self.w + self.h + min(self.w, self.h) + self.z) * 2


def default_strategy(crop=True):
    rects = []
    for i in range(N_RECTS):
        while True:
            cx = random.randint(1, CANVAS_WIDTH)
            cy = random.randint(1, CANVAS_HEIGHT)
            radius = random.randint(MIN_RECT_RADIUS, MAX_RECT_RADIUS)
            rect = Rect(cx, cy, radius, crop=crop)
            if any(rect.collides_with(e) for e in rects):
                continue
            rects.append(rect)
            break
    return rects


def distance_strategy():
    rects = []
    for i in range(N_RECTS):
        while True:
            weights = [
                sum(((x - e.cx) ** 2 + (y - e.cy) ** 2) ** .5 for e in rects) + 1
                for x, y in grid
            ]
            cx, cy = weighted_choice(grid, weights)
            radius = random.randint(MIN_RECT_RADIUS, MAX_RECT_RADIUS)
            rect = Rect(cx, cy, radius)
            if any(rect.collides_with(e) for e in rects):
                continue
            rects.append(rect)
            break
    return rects


def jitter_strategy():
    print('Jitter Desired Num: {}\nJitter Actual Num: {}'.format(N_RECTS, JITTER_HORIZ_SECTIONS * JITTER_VERT_SECTIONS))
    jit_sec_w, jit_sec_h = CANVAS_WIDTH / JITTER_HORIZ_SECTIONS, CANVAS_HEIGHT / JITTER_VERT_SECTIONS
    jitter_imperfection = abs(jit_sec_w - jit_sec_h) / min(jit_sec_w, jit_sec_h)
    print('Jitter Square Imperfection: {}%'.format(round(jitter_imperfection * 100, 2)))

    def _partition_list(l, n):
        part_size, part_mod = len(l) // n, len(l) % n
        part_sizes = [part_size + 1] * part_mod + [part_size] * (n - part_mod)
        random.shuffle(part_sizes)
        cumu_part = 0
        res = []
        for curr_part in part_sizes:
            res.append(l[cumu_part:cumu_part + curr_part])
            cumu_part += curr_part
        return res

    rects = []
    for horiz_opts in _partition_list(range(1, CANVAS_WIDTH), JITTER_HORIZ_SECTIONS):
        for vert_opts in _partition_list(range(1, CANVAS_HEIGHT), JITTER_VERT_SECTIONS):
            while True:
                cx = random.choice(horiz_opts)
                cy = random.choice(vert_opts)
                radius = random.randint(MIN_RECT_RADIUS, MAX_RECT_RADIUS)
                rect = Rect(cx, cy, radius)
                if any(rect.collides_with(e) for e in rects):
                    continue
                rects.append(rect)
                break
    return rects


def force_strategy():
    while True:
        rects = default_strategy(crop=False)
        print(len(rects))
        for i in range(FORCE_ITERS):
            # print(i)
            for j, rect in enumerate(rects):
                # print('', j)
                # todo calc dx and dy correctly
                dx = 1 / rect.cx - 1 / (CANVAS_WIDTH - rect.cx)
                dy = 1 / rect.cy - 1 / (CANVAS_HEIGHT - rect.cy)
                for k, o_rect in enumerate(rects):
                    # print(' ', k)
                    if o_rect == rect:
                        continue
                    f = 1. / calc_dist_between(rect.c, o_rect.c)
                    a, o = o_rect.cx - rect.cx, o_rect.cy - rect.cy
                    theta = 0 if a == 0 else math.atan(o / a)
                    dx += - f * math.cos(theta)
                    dy += - f * math.sin(theta)
                rect.force(dx, dy)

        for rect in rects:
            rect.snap_to_grid()
            rect.crop_to_canvas_borders()
        if not any(
            any(e.collides_with(f) for f in rects[i + 1:])
            for i, e in enumerate(rects)
        ):
            return rects


def poisson_strategy():
    #todo implement
    return []
