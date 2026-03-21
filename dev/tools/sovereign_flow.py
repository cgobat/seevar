#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ~/seevar/dev/tools/sovereign_flow.py
Version: 2.0.0
Objective: Manim visualization of a 3-target JSON-RPC TCP sequence with an animated Seestar model and 12-second integration.
"""

from manim import *
import random

class SovereignCommunicationFlow(Scene):
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
        title = Text("SeeVar: Sovereign Command Sequence", font_size=36, color=YELLOW).to_edge(UP)
        target_display = Text("Initializing...", font_size=20, color=BLUE).next_to(title, DOWN)
        self.play(FadeIn(title), FadeIn(target_display))

        # 3. Define the Nodes
        engine_box = RoundedRectangle(height=1.2, width=2.5, corner_radius=0.2, color=YELLOW, fill_opacity=0.2)
        engine_box.move_to(RIGHT * 3.5 + UP * 2.0)
        engine_text = Text("SeeVar\nOrchestrator", font_size=20, color=WHITE).move_to(engine_box)
        
        hardware_box = RoundedRectangle(height=1.2, width=2.5, corner_radius=0.2, color=BLUE, fill_opacity=0.2)
        hardware_box.move_to(RIGHT * 3.5 + DOWN * 2.0)
        hardware_text = Text("S30-Pro\nPort 4700", font_size=20, color=WHITE).move_to(hardware_box)

        self.play(Create(engine_box), Write(engine_text), Create(hardware_box), Write(hardware_text))

        # 4. Geometric Seestar Model
        seestar_group = VGroup()
        base = RoundedRectangle(height=0.4, width=1.5, corner_radius=0.1, color=GRAY, fill_opacity=0.8)
        arm = RoundedRectangle(height=1.2, width=0.4, corner_radius=0.1, color=DARK_GRAY, fill_opacity=0.8).next_to(base, UP, buff=0).align_to(base, RIGHT).shift(LEFT*0.2)
        
        # The tube will pivot around its center
        tube = RoundedRectangle(height=1.5, width=0.5, corner_radius=0.1, color=WHITE, fill_opacity=0.9)
        tube.move_to(arm.get_center() + LEFT*0.3)
        
        seestar_group.add(base, arm, tube)
        seestar_group.next_to(hardware_box, LEFT, buff=0.8)
        self.play(FadeIn(seestar_group))

        current_angle = 0 # Track telescope elevation

        # 5. UI Setup for the scrolling log
        log_title = Text("Sovereign Sequence Log", font_size=20, color=WHITE).to_edge(LEFT, buff=0.5).shift(UP * 2.5)
        self.play(FadeIn(log_title))
        
        # 6. Target Loop
        targets = ["CH Cyg", "V404 Cyg", "SS Cyg"]
        
        for target_idx, current_target in enumerate(targets):
            # Update Header
            new_target_display = Text(f"Current Target: {current_target} ({target_idx + 1}/3)", font_size=20, color=GREEN).next_to(title, DOWN)
            self.play(Transform(target_display, new_target_display))

            log_group = VGroup()
            current_y = 1.8
            
            steps = [
                ("1. Preflight Auth", "pi_is_verified", "true"),
                ("2. Hardware Audit", "get_device_state", "idle"),
                ("3. Target Slew", f"scope_goto({current_target})", "slewing"),
                ("4. Confirm Coord", "scope_get_equ_coord", "arrived"),
                ("5. Master Analyst", "start_solve", "solving"),
                ("6. Solve Confirm", "get_solve_result", "success"),
                ("7. Sync Mount", "scope_sync", "synced"),
                ("8. Start Tracking", "scope_set_track_state", "OK"),
                ("9. Autofocus", "start_auto_focuse", "running"),
                ("10. Focus Lock", "get_focuser_position", "1307"),
                ("11. Start Science", "start_exposure", "exposing"),
                ("12. Integration", f"12s Exposure", "idle"), 
                ("13. FITS Harvest", "SMB //WORKGROUP/Seestar", "Received"),
                ("14. Accountant QC", "Bayer Photometry", "Valid"),
                ("15. Ledger Commit", "ledger_manager.py", "Complete")
            ]

            for i, (action, cmd, resp) in enumerate(steps):
                # Color coding
                if "Poll" in action or "Confirm" in action: color = GRAY
                elif i >= 12: color = ORANGE 
                else: color = GREEN
                if i == 14: color = YELLOW
                
                # Log scrolling logic
                log_entry = Text(action, font_size=14, color=color).to_edge(LEFT, buff=0.5).shift(UP * current_y)
                log_group.add(log_entry)
                
                if len(log_group) > 10:
                    self.play(
                        log_group.animate.shift(UP * 0.4),
                        FadeOut(log_group[0]),
                        FadeIn(log_entry),
                        run_time=0.3
                    )
                    log_group.remove(log_group[0])
                else:
                    self.play(FadeIn(log_entry), run_time=0.3)
                    current_y -= 0.4

                # Transmit Request (Half-speed: run_time=0.8)
                req_text = Text(cmd, font_size=12, color=YELLOW).next_to(engine_box, DOWN)
                self.play(req_text.animate.next_to(hardware_box, UP), run_time=0.8)
                self.play(FadeOut(req_text), run_time=0.1)

                # Execute Hardware Animations
                if action == "3. Target Slew":
                    target_angle = random.uniform(20, 70) * DEGREES
                    rotation_diff = target_angle - current_angle
                    self.play(Rotate(tube, angle=rotation_diff, about_point=tube.get_center()), run_time=1.5)
                    current_angle = target_angle
                
                elif action == "12. Integration":
                    # 12-second progress bar for exposure
                    bar_bg = Rectangle(height=0.2, width=2.5, color=DARK_GRAY, fill_opacity=0.5).next_to(hardware_box, UP)
                    bar_fill = Rectangle(height=0.2, width=0.01, color=RED, fill_opacity=0.8).align_to(bar_bg, LEFT).align_to(bar_bg, DOWN)
                    
                    timer_text = Text("EXPOSING...", font_size=12, color=RED).next_to(bar_bg, UP)
                    
                    self.play(FadeIn(bar_bg), FadeIn(bar_fill), FadeIn(timer_text), run_time=0.5)
                    
                    # Lock the simulation for 12 seconds
                    self.play(bar_fill.animate.stretch_to_fit_width(2.5).align_to(bar_bg, LEFT), run_time=12.0, rate_func=linear)
                    
                    self.play(FadeOut(bar_bg), FadeOut(bar_fill), FadeOut(timer_text), run_time=0.5)

                # Transmit Response (Half-speed: run_time=0.8)
                resp_color = GREEN if resp in ["OK", "true", "success", "arrived", "1307", "idle", "synced", "Received", "Valid", "Complete"] else WHITE
                resp_text = Text(resp, font_size=12, color=resp_color).next_to(hardware_box, UP)
                self.play(resp_text.animate.next_to(engine_box, DOWN), run_time=0.8)
                self.play(FadeOut(resp_text), run_time=0.1)

            # Clear log for next target
            if target_idx < len(targets) - 1:
                self.play(FadeOut(log_group))
                self.wait(0.5)

        # 7. Final Sequence Complete
        self.wait(1)
        complete_text = Text("Nightly Plan Completed", font_size=32, color=GREEN).move_to(RIGHT * 3.5)
        
        self.play(
            FadeOut(engine_box), FadeOut(engine_text), 
            FadeOut(hardware_box), FadeOut(hardware_text),
            FadeOut(seestar_group), FadeOut(log_group),
            FadeIn(complete_text)
        )
        self.wait(3)
