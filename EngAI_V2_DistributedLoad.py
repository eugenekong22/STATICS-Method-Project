import streamlit as st
import time
from datetime import timedelta

# Try to import drawable canvas
try:
    from streamlit_drawable_canvas import st_canvas
    _canvas_ok = True
except ImportError:
    _canvas_ok = False

st.set_page_config(page_title="STATICS Method — Canal Gate", page_icon="🌊", layout="centered")

# ==========================================
# 1. PROBLEM DEFINITION & DIAGRAM
# ==========================================
st.title("Structural Integrity of a Canal Turnout Gate")

PROBLEM_TEXT = (
    "**The Scenario:**\n"
    "You are tasked with verifying the support requirements for a new vertical 'overshot' slide gate at a Cal Poly irrigation research plot. "
    "The gate is designed to hold back a full head of water from the main supply canal. "
    "To ensure the gate doesn't 'blow out' or warp, we must determine the exact horizontal forces being pushed into the support frame at the top and bottom.\n\n"
    "**The System Specs:**\n"
    "* **Gate Dimensions:** 3.0 m tall and 1.5 m wide.\n"
    "* **Water Condition:** The canal is at maximum capacity, with the water level flush with the top of the gate (Point A).\n"
    "* **Supports:**\n"
    "  * **Point A (Top):** A horizontal guide rail (modeled as a **Pin** for horizontal and vertical stability).\n"
    "  * **Point B (Bottom):** A concrete sill (modeled as a **Roller** providing only horizontal resistance).\n"
    "* **Loading:** The water creates a triangular hydrostatic distributed load. The intensity at the surface (Point A) is 0 kN/m, and the intensity at the floor (Point B) is 45 kN/m.\n\n"
    "**The Objective:**\n"
    "1. Calculate the Equivalent Resultant Force ($F_R$) representing the total push of the water.\n"
    "2. Determine the Location ($\\bar{y}$) of this force.\n"
    "3. Solve for the Horizontal Reaction Forces ($A_x$ and $B_x$) to determine which part of the frame needs the strongest bolts."
)
st.markdown(PROBLEM_TEXT)
st.divider()

# ----------------------------
# 2. STATE MANAGEMENT
# ----------------------------
def init_state():
    defaults = {
        "step_idx": 0,
        "start_time": None,
        "timer_finished": False,
        "fr_correct": False,
        "loc_correct": False,
        "ax_correct": False,
        "bx_correct": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
STUDY_DURATION = 180 

# ----------------------------
# 3. SIDEBAR RESET
# ----------------------------
if st.sidebar.button("🔄 Reset Problem"):
    st.session_state.clear()
    st.rerun()

# ----------------------------
# STEP 0: START
# ----------------------------
if st.session_state.step_idx == 0:
    if st.button("▶️ Begin S.T.A.T.I.C.S. Method"):
        st.session_state.step_idx = 1
        st.session_state.start_time = time.time()
        st.rerun()
    st.stop()

# ======================================================
# S — STUDY (Step 1)
# ======================================================
if st.session_state.step_idx >= 1:
    st.header("S — Study the Problem")
    st.caption("Read carefully and extract the physical parameters.")
    
    timer_placeholder = st.empty()
    if not st.session_state.timer_finished:
        elapsed = time.time() - st.session_state.start_time
        remaining = STUDY_DURATION - int(elapsed)
        if remaining <= 0:
            st.session_state.timer_finished = True
            st.rerun()
        timer_placeholder.warning(f"⏳ **Focus Period:** {str(timedelta(seconds=remaining))[2:7]} remaining.")
        if st.button("⏭️ Skip Timer"):
            st.session_state.timer_finished = True
            st.rerun()
        time.sleep(1)
        st.rerun()
    else:
        timer_placeholder.success("✅ Study time complete!")

    st.write("#### Extract Key Parameters")
    st.write("Prove you understand the physical setup by entering the correct values from the prompt.")
    
    col1, col2 = st.columns(2)
    with col1:
        gate_h = st.number_input("Gate Height (m):", min_value=0.0, step=0.1)
        max_load = st.number_input("Max Load Intensity at bottom (kN/m):", min_value=0.0, step=1.0)
    with col2:
        support_a = st.selectbox("Support A (Pin) restricts movement in:", ["Select...", "X only", "Y only", "Both X and Y"])
        support_b = st.selectbox("Support B (Roller on vertical wall) restricts movement in:", ["Select...", "X only", "Y only", "Both X and Y"])

    if st.session_state.step_idx == 1 and st.session_state.timer_finished:
        if st.button("Check Givens & Continue"):
            if gate_h == 3.0 and max_load == 45.0 and support_a == "Both X and Y" and support_b == "X only":
                st.success("Correct! Understanding the specific restrictions of Pins vs Rollers is crucial.")
                st.session_state.step_idx = 2
                st.rerun()
            else:
                st.error("Review the problem text. Check your dimensions, load intensities, and what axes a roller on a vertical wall actually restricts.")

# ======================================================
# T — TRANSLATE TO DIAGRAM (Step 2: FBD)
# ======================================================
if st.session_state.step_idx >= 2:
    st.divider()
    st.header("T — Translate to a Diagram (FBD)")

    st.write("Simplify the distributed water load into a **single Equivalent Resultant Force** for our Free Body Diagram.")
    
    with st.expander("Need a hint?"):
        st.write("How many reaction forces do we have for a pin type connection and a roller type connection?")
        st.write("Youtube (Different Connection Types): https://www.youtube.com/watch?v=Ez98UYAQyLo")
    
    st.info("Using the canvas toolbar (Line Tool), draw the simplified FBD of the gate.")
    st.caption("Draw the Gate as a vertical line. Draw the Equivalent Water Force as a horizontal arrow pushing on the gate. Finally, draw the reaction force vectors at supports A and B.")
    
    if _canvas_ok:
        canvas_fbd = st_canvas(
            stroke_width=3, stroke_color="#000", background_color="#fff",
            height=300, width=500, drawing_mode="line", display_toolbar=True, key="canvas_fbd_gate"
        )

        if st.button("Check FBD"):
            num_lines = len(canvas_fbd.json_data["objects"]) if canvas_fbd.json_data else 0
            if 4 <= num_lines <= 8:
                st.success("FBD looks populated. Proceed to Assign.")
                st.session_state.step_idx = 3
                st.rerun()
            else:
                st.error(f"Detected {num_lines} lines. Think about the gate itself, the single water force arrow, and the reaction arrows at A and B.")

# ======================================================
# A — ASSIGN (Step 3: Coordinates & Assumptions)
# ======================================================
if st.session_state.step_idx >= 3:
    st.divider()
    st.header("A — Assign Coordinates and Assumptions")
    
    st.write("Set up your coordinate system.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Positive X Direction:", ["Right (+)", "Left (+)"])
    with col2:
        st.selectbox("Positive Y Direction:", ["Up (+)", "Down (+)"])
    with col3:
        st.selectbox("Positive Moment:", ["Counter-Clockwise (+)", "Clockwise (+)"])
    
    st.markdown("**Assumption Strategy:**")
    st.info("Assume the reaction forces at A and B push *against* the water to keep the gate in place (Leftward / Negative X direction). If your math yields a negative number later, it means your assumption was backward.")
    
    if st.button("Acknowledge Assumptions"):
        st.session_state.step_idx = 4
        st.rerun()

# ======================================================
# T — TRANSLATE TO COMPONENTS (Step 4: Breakdown)
# ======================================================
if st.session_state.step_idx >= 4:
    st.divider()
    st.header("T — Translate Forces to Components")
    st.caption("Verify the active directions for each force before writing equilibrium equations.")
    
    st.write("In this specific problem, our forces align perfectly with the X and Y axes, so trigonometry isn't required. Identify the active forces:")

    q_water = st.checkbox("The Equivalent Water Force has an X-component.", value=False)
    q_pin_x = st.checkbox("The Pin at A has an X-component.", value=False)
    q_pin_y = st.checkbox("The Pin at A has a Y-component.", value=False)
    q_roller_x = st.checkbox("The Roller at B has an X-component.", value=False)
    q_roller_y = st.checkbox("The Roller at B has a Y-component.", value=False)

    if st.button("Verify Components"):
        if q_water and q_pin_x and q_pin_y and q_roller_x and not q_roller_y:
            st.success("Correct! Water and the Roller act purely horizontally. The Pin acts in both directions.")
            st.session_state.step_idx = 5
            st.rerun()
        else:
            st.error("Review the support types. A roller on a vertical wall provides NO vertical friction or support.")

# ======================================================
# I — IMPLEMENT (Step 5: Equilibrium Strategy & Equations)
# ======================================================
if st.session_state.step_idx >= 5:
    st.divider()
    st.header("I — Implement Equilibrium Equations")
    st.caption("Map out your strategy and identify the equilibrium conditions needed.")
    
    st.write("1. To find the magnitude of the equivalent resultant force from a distributed load, we calculate the mathematical ________ of the load shape.")
    mag_ans = st.text_input("Concept 1:", key="mag_input").strip().lower()
    
    st.write("2. The resultant force acts perfectly through the geometric ________ of the triangle.")
    loc_ans = st.text_input("Concept 2:", key="loc_input").strip().lower()
                      
    st.write("3. If you sum forces in the X direction first, you will have one equation but two unknowns ($A_x$ and $B_x$). Which point should you sum moments around to completely eliminate the Pin unknowns?")
    pivot_ans = st.selectbox("Pivot Point:", ["Select...", "Point A", "Point B", "Center of Gate"])
    
    with st.expander("Need a hint on the strategy?"):
        st.write("A distributed load on a graph represents an amount of force over a distance.")
        st.write("Concept 1: What geometric calculation gives you total amount?")
        st.write("Concept 2: What is the 'center of mass' of a 2D shape called?")
        st.write("Concept 3: How many unknowns do we have at Pin A and how many unknowns do we have at Pin B?")
        st.write("Youtube (Distributed Load): https://www.youtube.com/watch?v=_K-3hUyoqOw")

    st.markdown("#### 4. Acknowledge Required Equilibrium Equations")
    st.caption("To solve for the unknowns, you must apply the conditions for rigid body equilibrium. Check the equations needed to solve this problem:")
    
    chk_fx = st.checkbox("We must use **$\\sum F_x = 0$** to balance the horizontal water push against the horizontal support reactions.", key="I_chk_fx")
    chk_fy = st.checkbox("We must use **$\\sum F_y = 0$** to balance vertical forces (Note: the problem simplifies vertical weight/friction, but it remains a core condition).", key="I_chk_fy")
    chk_m = st.checkbox("We must use **$\\sum M_A = 0$** (Sum of Moments) to mathematically isolate and solve for $B_x$.", key="I_chk_m")
    
    if st.button("Validate Logic & Equations"):
        if "area" in mag_ans and "centroid" in loc_ans and pivot_ans == "Point A":
            if not (chk_fx and chk_m):
                st.warning("Please acknowledge the core equilibrium equations needed ($\\sum F_x = 0$ and $\\sum M = 0$) to proceed.")
            else:
                st.success("Excellent! Strategy is sound. You are ready to compute.")
                st.session_state.step_idx = 6
                st.rerun()
        else:
            st.error("Review your strategy concepts above. What is the center of a shape called? Which support has the most unknown forces to eliminate?")

# ======================================================
# C — COMPUTE (Step 6: Guided Math)
# ======================================================
if st.session_state.step_idx >= 6:
    st.divider()
    st.header("C — Compute Results")
    st.caption("Solve algebraically for unknown magnitudes and locations.")

    # --- Part 1: Resultant Force ---
    st.subheader("Part 1: Calculate the Resultant Force ($F_R$)")
    with st.expander("Need a hint?"):
        st.write("Apply your strategy: Calculate the area of a triangle. What is the base intensity? What is the height?")
        st.write("Youtube (Area of Triangle): https://www.youtube.com/watch?v=pvMuDPVOm7Y")

    fr_val = st.number_input("Resultant Force $F_R$ (kN):", min_value=0.0, format="%.1f")
    
    if st.button("Check F_R"):
        if abs(fr_val - 67.5) < 0.5:
            st.success("Correct! $F_R$ = 67.5 kN.")
            st.session_state.fr_correct = True
        else:
            st.error("Check your math. Did you remember the 1/2 in the triangle area formula?")

    # --- Part 2: Centroid Location ---
    if st.session_state.get("fr_correct"):
        st.divider()
        st.subheader("Part 2: Calculate Force Location ($\\bar{y}$)")
        st.write("Enter the distance from **Point A (Top)** to the line of action.")
        
        with st.expander("Need a hint?"):
            st.write("The centroid of a right triangle is located 1/3 of the distance from the heavy flat base. Since Point A is at the pointy tip, how far is it from the top?")
            st.write("Youtube (Centroid of Right Triangle): https://www.youtube.com/watch?v=BT5dbFATUnQ")
        
        loc_val = st.number_input("Distance from Point A (meters):", min_value=0.0, max_value=3.0, format="%.2f")
        
        if st.button("Check Location"):
            if abs(loc_val - 2.0) < 0.1:
                st.success("Correct! The force acts 2.0 m down from Point A.")
                st.session_state.loc_correct = True
            else:
                st.error("Calculate 2/3 of the total height of the gate.")

    # --- Part 3: Reactions ---
    if st.session_state.get("loc_correct"):
        st.divider()
        st.subheader("Part 3: Solve for Reactions ($A_x$ and $B_x$)")
        
        st.write("**Step A: Find $B_x$**")
        with st.expander("Need a hint for B_x?"):
            st.write("Apply $\\sum M_A = 0$. The water force creates a moment, and $B_x$ resists it. Multiply each force by its perpendicular distance to Point A.")
            st.write("Youtube (Solving Reaction with Moment Equation): https://www.youtube.com/watch?v=sxkEgZ9IueQ")
        bx_val = st.number_input("Calculate $B_x$ (kN):", min_value=0.0, format="%.1f")
        
        st.write("**Step B: Find $A_x$**")
        with st.expander("Need a hint for A_x?"):
            st.write("Apply $\\sum F_x = 0$. Now that you know $F_R$ and $B_x$, balance the leftward and rightward forces.")
            st.write("Youtube (Solving Reaction with Force Equation): https://www.youtube.com/watch?v=sxkEgZ9IueQ")
        ax_val = st.number_input("Calculate $A_x$ (kN):", min_value=0.0, format="%.1f")
        
        if st.button("Check Reactions and Finish"):
            ok_bx = abs(bx_val - 45.0) < 0.5
            ok_ax = abs(ax_val - 22.5) < 0.5
            
            if ok_bx and ok_ax:
                st.balloons()
                st.session_state.step_idx = 7
                st.rerun()
            else:
                if not ok_bx:
                    st.error("Check $B_x$. Set up your moment equation: $(F_R \\times \\text{distance to A}) = (B_x \\times \\text{total height})$.")
                if not ok_ax:
                    st.error("Check $A_x$. Ensure that $A_x + B_x$ exactly equals the total water force.")

# ======================================================
# S — SANITY CHECK (Step 7)
# ======================================================
if st.session_state.step_idx >= 7:
    st.divider()
    st.header("S — Sanity Check")
    
    st.success("Calculations Complete!")
    
    st.markdown("### Final Support Forces:")
    st.write("- **Top Reaction ($A_x$)**: 22.5 kN")
    st.write("- **Bottom Reaction ($B_x$)**: 45.0 kN")
    st.write("- **Total Water Force**: 67.5 kN")
    
    st.markdown("### Reflection")
    st.write("Think about your final results and check the boxes if they make physical sense:")
    
    check1 = st.checkbox("The total push of the water (67.5 kN) perfectly equals the sum of the supports (22.5 + 45.0). This satisfies $\\sum F_x = 0$.")
    check2 = st.checkbox("The bottom support ($B_x$) is exactly twice as large as the top support ($A_x$) because the water pressure is heavier at the bottom, shifting the centroid downward.")
    check3 = st.checkbox("Based on these results, the bottom concrete sill requires significantly stronger anchoring bolts than the top guide rail.")
    
    if check1 and check2 and check3:
        st.info("You have successfully applied the S.T.A.T.I.C.S. approach to a distributed loading problem. Great job!")
        
        if st.button("Start New Problem"):
            st.session_state.clear()
            st.rerun()