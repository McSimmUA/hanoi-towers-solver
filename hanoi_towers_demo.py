from manim import *
from hanoi_towers_solver import hanoi_get_solution, SolutionStep

RODS_COUNT = 7
DISKS_COUNT = 14
DISK_HEIGHT = 0.2

# MOVING_TIME = 0.25
MOVING_TIME = 0.5
ORIGINAL_THETA = -5 * DEGREES

BREAK_AFTER_STEP = 0
RENDER_REVERSE = False

SKIP_ANIMATIONS = False
DRAFT = False

solution: list[SolutionStep] = hanoi_get_solution(RODS_COUNT, DISKS_COUNT)


class HanoiTowersDemo2D(Scene):
    def construct(self):
        rods = VGroup()
        for i in range(RODS_COUNT):
            r = Line(frame.bottom, DOWN)
            r.disks_count = 0
            rods.add(r)
        rods.arrange_in_grid(rows=1, cols=RODS_COUNT, col_alignments='c' * RODS_COUNT,
                             col_widths=[frame.frame_width / RODS_COUNT] * RODS_COUNT)

        self.add(rods)
        disks = VGroup()
        for s in range(DISKS_COUNT):
            w = s * .3 + .1
            c = (DISKS_COUNT - s - 1) * DISK_HEIGHT + DISK_HEIGHT / 2
            r = Rectangle(width=w, height=DISK_HEIGHT)
            r.move_to(rods[0])
            r.move_to(c * UP + frame.bottom, coor_mask=UP)
            disks.add(r)
        rods[0].disks_count = len(disks)

        self.add(disks)

        step_no = 0
        steps_count = len(solution)
        progress_lbl = None

        for d, f, t in solution:
            # d, f, t = solution_step.values()
            step_no += 1
            if progress_lbl is not None:
                self.remove(progress_lbl)
            progress_lbl = Text(f"{step_no} / {steps_count}", font_size=18).to_corner(UL)
            self.add(progress_lbl)

            disks[d].move_to(ORIGIN, coor_mask=UP)
            self.wait(0.5*MOVING_TIME)

            disks[d].move_to(rods[t], coor_mask=RIGHT)
            self.wait(0.5*MOVING_TIME)

            c = frame.bottom + (DISK_HEIGHT * rods[t].disks_count + DISK_HEIGHT / 2) * UP
            disks[d].move_to(c, coor_mask=UP)
            self.wait(2*MOVING_TIME)
            # self.wait(MOVING_TIME)
            # self.wait(1)

            rods[f].disks_count -= 1
            rods[t].disks_count += 1


class HanoiTowersDemo(ThreeDScene):
    current_theta = 0.
    total_time = 1.

    def rotate_compensation(self, animation_time: float):
        self.current_theta += TAU * animation_time / self.total_time
        self.set_camera_orientation(theta=self.current_theta)

    def wait_with_rotating_compensation(self, wait_time: float):
        self.wait(wait_time)
        self.rotate_compensation(wait_time)

    def construct(self):
        stars_field = VGroup()
        rng = np.random.default_rng()
        for i in range(200):
            xyz = ORIGIN
            while xyz[0]**2 + xyz[1]**2 < 32:
                xyz = np.array((60*(rng.random() - .5), 60*(rng.random() - .5), 30*(rng.random() - .5)))
            c = (BLUE, BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E)[i % 6]
            stars_field.add(Dot3D(xyz, color=c, radius=0.04))
        rods = VGroup()
        rods_on_circle = RODS_COUNT - 1 if RODS_COUNT > 3 else RODS_COUNT
        for s in range(rods_on_circle):
            x = 4 * np.sin(s * TAU / rods_on_circle)
            y = 4 * np.cos(s * TAU / rods_on_circle)
            rod = Line3D(start=np.array((x, y, 0)), end=np.array((x, y, 3)), color=DARK_GREY)
            rod.disks_count = 0
            rods.add(rod)
        if RODS_COUNT > 3:
            rod = Line3D(start=ORIGIN, end=ORIGIN + OUT * 3, color=DARK_GREY)
            rod.disks_count = 0
            rods.add(rod)

        disks = VGroup()
        for s in range(DISKS_COUNT):
            r = s * 1.5 / DISKS_COUNT + 0.5
            z = (DISKS_COUNT - s - 1) * DISK_HEIGHT + DISK_HEIGHT / 2
            resolution = (1, 4) if DRAFT else (1, 48)
            d = Cylinder(radius=r, height=DISK_HEIGHT, stroke_color=DARK_BLUE, fill_color=DARK_BLUE,
                         resolution=resolution, checkerboard_colors=[DARK_BLUE])

            # d = Cylinder(radius=r, height=DISK_HEIGHT, stroke_color=YELLOW, fill_color=DARK_BLUE, resolution=(1, 48))
            d.move_to(rods[0].start + OUT * z)
            disks.add(d)
        rods[0].disks_count = len(disks)

        self.add(stars_field, disks, rods)

        self.current_theta = ORIGINAL_THETA

        self.set_camera_orientation(phi=75 * DEGREES, theta=self.current_theta, frame_center=OUT)

        steps_count = len(solution)

        self.total_time = MOVING_TIME * (steps_count * 2 * 3 + 2)
        self.begin_ambient_camera_rotation(rate=TAU / self.total_time)

        # a pause for fade in
        self.wait_with_rotating_compensation(1)

        reverse = False
        progress_lbl = None

        render_list = list(range(len(solution)))
        if RENDER_REVERSE:
            render_list.extend(range(len(solution)-1, -1, -1))

        rods[0].set_color(DARK_BLUE)
        rods[-1].set_color(GREEN_E)

        for step_no in render_list:
            if 0 < BREAK_AFTER_STEP < step_no:
                break
            solution_step = solution[step_no]
            if reverse:
                d, t, f = solution_step
            else:
                d, f, t = solution_step
            if progress_lbl is not None:
                self.remove(progress_lbl)
            progress_lbl = Text(f"{step_no+1} / {steps_count}", font_size=18).to_corner(UL)
            self.add_fixed_in_frame_mobjects(progress_lbl)
            progress_lbl.to_corner(UL)

            if SKIP_ANIMATIONS:
                if not DRAFT:
                    disks[d].move_to(rods[f].start + OUT * 4)
                # self.wait_with_rotating_compensation(MOVING_TIME)
                self.wait_with_rotating_compensation(MOVING_TIME * 0.5)

                if not DRAFT:
                    disks[d].move_to(rods[t].start + OUT * 4)
                # self.wait_with_rotating_compensation(MOVING_TIME)
                self.wait_with_rotating_compensation(MOVING_TIME * 0.5)

                disks[d].move_to(rods[t].start + OUT * (DISK_HEIGHT * rods[t].disks_count + DISK_HEIGHT / 2))
                # self.wait_with_rotating_compensation(MOVING_TIME)
                self.wait_with_rotating_compensation(MOVING_TIME * 2)

            else:
                self.play(disks[d].animate().move_to(rods[f].start + OUT * 4), run_time=MOVING_TIME * 0.5)
                self.rotate_compensation(MOVING_TIME * 0.5)

                self.play(disks[d].animate().move_to(rods[t].start + OUT * 4), run_time=MOVING_TIME * 0.5)
                self.rotate_compensation(MOVING_TIME * 0.5)

                self.play(
                    disks[d].animate().move_to(
                        rods[t].start + OUT * (DISK_HEIGHT * rods[t].disks_count + DISK_HEIGHT / 2)),
                    run_time=MOVING_TIME * 0.5
                )
                self.rotate_compensation(MOVING_TIME * 0.5)
                self.wait_with_rotating_compensation(MOVING_TIME * 1.5)

                # self.rotate_compensation(MOVING_TIME * 2)

            rods[t].disks_count += 1
            rods[f].disks_count -= 1

            if not reverse and step_no == len(solution) - 1:
                self.wait_with_rotating_compensation(MOVING_TIME)
                rods[-1].set_color(DARK_BLUE)
                rods[0].set_color(GREEN_E)
                reverse = True

        # a pause for fade out
        self.wait_with_rotating_compensation(1)
        # self.wait_with_rotating_compensation(MOVING_TIME)

        self.stop_ambient_camera_rotation()
        self.set_camera_orientation(theta=ORIGINAL_THETA)


with tempconfig({"background_color": BLACK,
                 # "quality": "high_quality",
                 "quality": "medium_quality",
                 # "quality": "low_quality",
                 # "preview": True,
                 "disable_caching": True,
                 # "format": 'gif',
                 "dry_run": False}):
    scene = HanoiTowersDemo()
    # scene = HanoiTowersDemo2D()
    scene.render()
