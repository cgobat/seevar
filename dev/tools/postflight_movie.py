#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ~/seevar/dev/tools/postflight_movie.py
Version: 1.0.1
Objective: Manim script visualizing the SeeVar Postflight pipeline: FITS ingestion, differential photometry, and AAVSO reporting.
"""

from manim import *
import random
import numpy as np

class PostflightScienceFlow(Scene):
    def construct(self):
        # 1. Setup the Night Sky Background
        stars = VGroup(*[
            Dot(
                point=[random.uniform(-7, 7), random.uniform(-4, 4), 0],
                radius=random.uniform(0.01, 0.03),
                color=WHITE,
                fill_opacity=random.uniform(0.2, 0.8)
            ) for _ in range(150)
        ])
        self.add(stars)

        # 2. Main Title
        title = Text("SeeVar: Postflight Science Engine", font_size=36, color=YELLOW).to_edge(UP)
        subtitle = Text("From RAW FITS to AAVSO Report", font_size=20, color=BLUE).next_to(title, DOWN)
        self.play(FadeIn(title), FadeIn(subtitle))

        # 3. Phase 1: Data Ingestion (Librarian)
        phase_text = Text("1. Secure Harvesting (librarian.py)", font_size=24, color=WHITE).to_edge(LEFT).shift(UP*1.5)
        self.play(FadeIn(phase_text))

        fits_file = Rectangle(height=1.0, width=0.8, color=BLUE_C, fill_opacity=0.5)
        fits_label = Text(".FIT", font_size=16).move_to(fits_file)
        fits_group = VGroup(fits_file, fits_label).move_to(LEFT * 4 + DOWN * 1)

        nas_drive = RoundedRectangle(height=1.5, width=2.0, corner_radius=0.2, color=GRAY, fill_opacity=0.8)
        nas_label = Text("RAID1 / NAS", font_size=16).move_to(nas_drive)
        nas_group = VGroup(nas_drive, nas_label).move_to(RIGHT * 4 + DOWN * 1)

        self.play(FadeIn(fits_group), FadeIn(nas_group))
        self.play(fits_group.animate.move_to(nas_group.get_center()), run_time=1.5)
        self.play(Indicate(nas_group, color=GREEN), FadeOut(fits_group))
        self.play(FadeOut(phase_text))

        # 4. Phase 2: Differential Photometry (Accountant)
        phase_text_2 = Text("2. Differential Photometry (bayer_photometry.py)", font_size=24, color=WHITE).to_edge(LEFT).shift(UP*1.5)
        self.play(FadeIn(phase_text_2))

        # Simulate a star field
        star_field = VGroup()
        target_star = Dot(point=LEFT*2 + DOWN*0.5, radius=0.08, color=YELLOW)
        comp_star_1 = Dot(point=LEFT*0.5 + UP*0.5, radius=0.06, color=WHITE)
        comp_star_2 = Dot(point=RIGHT*1.5 + DOWN*1.5, radius=0.07, color=WHITE)
        
        star_field.add(target_star, comp_star_1, comp_star_2)
        
        # Add background noise stars
        for _ in range(20):
            star_field.add(Dot(point=[random.uniform(-3, 3), random.uniform(-2, 1), 0], radius=random.uniform(0.01, 0.03), color=GRAY))
        
        self.play(FadeIn(star_field))

        # Draw Apertures
        t_aperture = Circle(radius=0.3, color=GREEN).move_to(target_star)
        c1_aperture = Circle(radius=0.3, color=RED).move_to(comp_star_1)
        c2_aperture = Circle(radius=0.3, color=RED).move_to(comp_star_2)

        t_label = Text("Target (V)", font_size=14, color=GREEN).next_to(t_aperture, DOWN)
        c1_label = Text("Comp 1", font_size=14, color=RED).next_to(c1_aperture, UP)
        c2_label = Text("Comp 2", font_size=14, color=RED).next_to(c2_aperture, UP)

        self.play(Create(t_aperture), Write(t_label))
        self.play(Create(c1_aperture), Write(c1_label), Create(c2_aperture), Write(c2_label))

        # Draw measurement lines indicating differential comparison
        line1 = DashedLine(target_star.get_center(), comp_star_1.get_center(), color=BLUE_A)
        line2 = DashedLine(target_star.get_center(), comp_star_2.get_center(), color=BLUE_A)
        self.play(Create(line1), Create(line2))
        self.wait(1)

        self.play(FadeOut(phase_text_2), FadeOut(star_field), FadeOut(t_aperture), FadeOut(c1_aperture), FadeOut(c2_aperture), FadeOut(t_label), FadeOut(c1_label), FadeOut(c2_label), FadeOut(line1), FadeOut(line2), FadeOut(nas_group))

        # 5. Phase 3: The Light Curve & Report Generation
        phase_text_3 = Text("3. Light Curve & AAVSO Report", font_size=24, color=WHITE).to_edge(LEFT).shift(UP*1.5)
        self.play(FadeIn(phase_text_3))

        # Create a simple graph (Removed the invalid string scaling parameter here)
        ax = Axes(
            x_range=[0, 10, 2],
            y_range=[8, 14, 2],
            x_length=6,
            y_length=3,
            axis_config={"color": GRAY, "include_tip": False},
            y_axis_config={"numbers_to_include": [8, 10, 12, 14]}
        ).move_to(DOWN*1)
        
        labels = ax.get_axis_labels(x_label=Text("JD", font_size=14), y_label=Text("Mag", font_size=14))
        
        self.play(Create(ax), Write(labels))

        # Plot synthetic variable star data (a dip in brightness)
        x_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y_vals = [9.5, 9.6, 10.2, 12.1, 12.8, 11.5, 10.1, 9.7, 9.5]
        
        dots = VGroup()
        for i in range(len(x_vals)):
            dot = Dot(point=ax.c2p(x_vals[i], y_vals[i]), color=YELLOW, radius=0.06)
            dots.add(dot)
            self.play(FadeIn(dot), run_time=0.1)
        
        # Connect the dots with a line
        curve = ax.plot_line_graph(x_vals, y_vals, line_color=BLUE, add_vertex_dots=False)
        self.play(Create(curve))
        self.wait(1)

        # Generate AAVSO Report Document
        report = Rectangle(height=2.0, width=1.5, color=WHITE, fill_opacity=0.1).to_edge(RIGHT).shift(UP*0.5)
        report_title = Text("AAVSO\nExtended\nFormat", font_size=14, color=WHITE).move_to(report).shift(UP*0.5)
        report_lines = VGroup(*[Line(LEFT*0.5, RIGHT*0.5, color=GRAY, stroke_width=2).move_to(report).shift(DOWN*(0.1 + i*0.2)) for i in range(4)])
        
        self.play(FadeIn(report), Write(report_title), Create(report_lines))

        # Stamp it "ACCEPTED"
        stamp = Text("SUBMITTED", font_size=18, color=GREEN).move_to(report).rotate(PI/6)
        self.play(Write(stamp), run_time=0.5)
        self.play(stamp.animate.scale(1.2), run_time=0.2)
        self.play(stamp.animate.scale(1/1.2), run_time=0.2)

        self.wait(2)

        # 6. Conclusion
        self.play(
            *[FadeOut(m) for m in self.mobjects if m not in [stars]]
        )
        
        final_text = Text("SeeVar: The Fully Automated Observatory", font_size=32, color=YELLOW)
        final_sub = Text("Sleep while it computes.", font_size=20, color=WHITE).next_to(final_text, DOWN)
        
        self.play(FadeIn(final_text), FadeIn(final_sub))
        self.wait(3)
