import streamlit as st
import time
from datetime import timedelta
import math

# Try to import drawable canvas
try:
    from streamlit_drawable_canvas import st_canvas
    _canvas_ok = True
except ImportError:
    _canvas_ok = False

st.set_page_config(page_title="STATICS Method — Internal Forces", page_icon="🔧", layout="centered")

# ==========================================
# 1. PROBLEM DEFINITION & DIAGRAM
# ==========================================
st.title("Internal Forces in a Frame")

# Replace this URL with your local file path or hosted image link for image_582b06.png
PROBLEM_IMAGE_URL = "https://i.imgur.com/ZMe9g04.png"

try:
    st.image(PROBLEM_IMAGE_URL, caption="Problem Diagram", use_container_width=True)
except Exception:
    st.error("Could not load image. Please check the PROBLEM_IMAGE_URL variable in the code.")

st.info("📄 **Reference:** Refer to the diagram of the frame with the applied 160 lb load.")

PROBLEM_TEXT = (
    "**The Scenario:**\n"
    "You are analyzing a mechanical frame consisting of member ABC and member BD. "
    "To ensure the horizontal beam doesn't snap under the applied load, we need to verify the internal stresses at a specific critical cross-section.\n\n"
    "**The System Specs:**\n"
    "* **Member ABC:** A horizontal continuous beam.\n"
    "* **Member BD:** An angled support strut.\n"
    "* **Connections:** Pin supports at **C** and **D**. A connecting pin at **B**.\n"
    "* **Loading:** A downward point load of $160\\text{ lb}$ is applied at the very end (Point A).\n"
    "* **Dimensions:**\n"
    "  * A to B = $14\\text{ in.}$\n"
    "  * B to J = $8\\text{ in.}$\n"
    "  * J to C = $8\\text{ in.}$\n"
    "  * C to D (Vertical) = $10\\text{ in.}$\n"
    "  * B to D (Horizontal) = $24\\text{ in.}$\n\n"
    "**The Objective:**\n"
    "Determine the **internal axial force ($N$)**, **shearing force ($V$)**, and **bending moment ($M$)** at Point J."
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
        "fbd_correct": False,
        "fbd_val": 0,
        "nj_correct": False,
        "vj_correct": False,
        "mj_correct": False
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

    st.write("#### System Mechanics Check")
    st.write("Before diving into numbers, you must identify how the members behave. Look closely at member **BD**.")
    
    member_type = st.selectbox("Member BD has pins at both ends and no loads applied in the middle. This means Member BD is a:", 
                               ["Select...", "Zero-force member", "Two-force member", "Three-force body", "Continuous beam"])
    
    total_dist = st.number_input("What is the total horizontal distance from A to C? (inches):", min_value=0, step=1)

    if st.session_state.step_idx == 1 and st.session_state.timer_finished:
        if st.button("Check Mechanics & Continue"):
            if member_type == "Two-force member" and total_dist == 30:
                st.success("Correct! Because BD is a two-force member, we know the **exact direction** of the force it applies to point B (along the line connecting B and D).")
                st.session_state.step_idx = 2
                st.rerun()
            else:
                st.error("Review the problem. Add up the horizontal segments. Also, recall the definition of a member with only two pins and no intermediate loads.")

# ======================================================
# T — TRANSLATE TO DIAGRAM (Step 2: FBD)
# ======================================================
if st.session_state.step_idx >= 2:
    st.divider()
    st.header("T — Translate to a Diagram (FBD)")

    st.write("To solve this, we actually need to visualize **two** separate Free Body Diagrams in our minds.")
    
    with st.expander("Need a hint?"):
        st.write("First, we need to analyze the whole bar (ABC) to find the reaction forces. Then, to find the internal forces at J, we have to make an imaginary 'cut' through the member at J and look at just one side.")
        st.write("Youtube (Internal Forces): https://www.youtube.com/watch?v=LPd4vW8f9Ac")
    
    st.info("Using the canvas toolbar, sketch the FBD of the **Left Segment (ABJ)** after making an imaginary cut at J.")
    st.caption("Draw the segment ABJ. Include the applied $160\\text{ lb}$ load, the reaction force from BD acting at B, and the three internal forces ($N, V, M$) exposed at the cut J.")
    
    if _canvas_ok:
        canvas_fbd = st_canvas(
            stroke_width=3, stroke_color="#000", background_color="#fff",
            height=300, width=600, drawing_mode="line", display_toolbar=True, key="canvas_fbd_frame"
        )

        if st.button("Check FBD"):
            num_lines = len(canvas_fbd.json_data["objects"]) if canvas_fbd.json_data else 0
            if num_lines >= 4:
                st.success("FBD looks populated. You should have the beam, load A, force B, and internal forces at J. Proceed.")
                st.session_state.step_idx = 3
                st.rerun()
            else:
                st.error(f"Detected {num_lines} lines. Think about the segment itself, the external loads on it, and the 3 internal reactions exposed at the cut.")

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
    st.info("Assume member BD is in **Tension** (pulling up and to the right on point B). For the cut at J, it is standard to assume internal Normal force ($N$) points away from the cut, Shear ($V$) points down on a right-facing cut, and Moment ($M$) is CCW.")
    
    if st.button("Acknowledge Assumptions"):
        st.session_state.step_idx = 4
        st.rerun()

# ======================================================
# T — TRANSLATE TO COMPONENTS (Step 4: Geometry)
# ======================================================
if st.session_state.step_idx >= 4:
    st.divider()
    st.header("T — Translate Forces to Components")
    st.caption("Before writing equilibrium equations, we must find the geometry of the two-force member BD.")
    
    st.write("Force $F_{BD}$ acts along the physical slope of the strut. Let's find the dimensions of the right triangle formed by BD.")

    q_rise = st.number_input("What is the vertical 'Rise' of BD? (in):", min_value=0.0, step=1.0)
    q_run = st.number_input("What is the horizontal 'Run' of BD? (in):", min_value=0.0, step=1.0)
    q_hyp = st.number_input("Calculate the Hypotenuse length of BD (in):", min_value=0.0, step=1.0)

    with st.expander("Need a hint?"):
        st.write("Look at the dimensions provided. D is horizontally $24\\text{ in.}$ away from B. How high is D above the horizontal line ABC? Use the Pythagorean theorem for the hypotenuse.")
        st.write ("Youtube (Pythagorean Theorem): https://www.youtube.com/watch?v=uthjpYKD7Ng")

    if st.button("Verify Geometry"):
        if q_rise == 10.0 and q_run == 24.0 and q_hyp == 26.0:
            st.success("Correct! This is a 10-24-26 triangle (which simplifies to a 5-12-13 ratio). You can use this to find the X and Y components of $F_{BD}$.")
            st.session_state.step_idx = 5
            st.rerun()
        else:
            st.error("Check your dimensions. Use $a^2 + b^2 = c^2$ to find the hypotenuse.")

# ======================================================
# I — IMPLEMENT (Step 5: Equilibrium Strategy)
# ======================================================
if st.session_state.step_idx >= 5:
    st.divider()
    st.header("I — Implement Equilibrium Strategy")
    st.caption("Map out your mathematical strategy before computing numbers.")
    
    st.write("1. We must first find the force in member BD. Looking at the **entire frame ABC**, which point should we sum moments around to eliminate the unknown pin reactions at C and solve directly for $F_{BD}$?")
    pivot_ans = st.selectbox("Pivot Point:", ["Select...", "Point A", "Point B", "Point C", "Point D"])
    
    st.write("2. Once $F_{BD}$ is known, we look at the **Left Segment (ABJ)**. We will use $\\sum F_x = 0$ to find the normal force $N$, $\\sum F_y = 0$ to find the shear $V$, and $\\sum M = 0$ about point ________ to find the internal bending moment $M$.")
    cut_ans = st.selectbox("Pivot Point for Internal Moment:", ["Select...", "Point A", "Point B", "Point J"])
    
    with st.expander("Need a hint on the strategy?"):
        st.write("Concept 1: To isolate one unknown force, put your pivot point on top of the other unknown forces so they have a moment arm of zero.")
        st.write("Concept 2: When finding internal moments at a cut, it is always easiest to sum moments exactly AT the cut to eliminate the internal normal and shear forces from the equation.")
    
    if st.button("Validate Strategy"):
        if pivot_ans == "Point C" and cut_ans == "Point J":
            st.success("Excellent! Summing moments at C isolates $F_{BD}$. Summing moments at J isolates the internal moment. Let's calculate.")
            st.session_state.step_idx = 6
            st.rerun()
        else:
            st.error("Review your strategy. Where are the forces you want to IGNORE located?")

# ======================================================
# C — COMPUTE (Step 6: Guided Math)
# ======================================================
if st.session_state.step_idx >= 6:
    st.divider()
    st.header("C — Compute Results")
    st.caption("Solve algebraically step-by-step.")

    # --- Part 1: Force BD ---
    st.subheader("Part 1: Calculate Force $F_{BD}$")
    st.write("Use $\\sum M_C = 0$ on the entire member ABC.")
    
    with st.expander("Need a hint?"):
        st.write("The $160\\text{ lb}$ load at A pushes down. How far is A from C? The vertical component of $F_{BD}$ ($F_{BD,y}$) pushes up at B. How far is B from C?")
        st.write("Set the CCW moments equal to the CW moments: $(160 \\times \\text{dist AC}) = (F_{BD,y} \\times \\text{dist BC})$. Then remember $F_{BD,y} = F_{BD} \\times (10/26)$.")

    fbd_val = st.number_input("Magnitude of $F_{BD}$ (lb):", min_value=0.0, format="%.1f")
    
    if st.button("Check F_BD"):
        if abs(fbd_val - 780.0) < 1.0:
            st.success("Correct! $F_{BD} = 780\\text{ lb}$. Now break this into X and Y components to use on the cut segment.")
            st.session_state.fbd_correct = True
            st.session_state.fbd_val = fbd_val
        else:
            st.error("Check your moment arms. Point A is $30\\text{ in.}$ from C. Point B is $16\\text{ in.}$ from C.")

    # --- Part 2: Internal Forces ---
    if st.session_state.get("fbd_correct"):
        st.divider()
        st.subheader("Part 2: Calculate Internal Forces at J")
        st.write("Now, look **only at the Left Segment (ABJ)**. You have the $160\\text{ lb}$ downward force at A, and the components of $F_{BD}$ acting at B.")
        
        with st.expander("Need a hint for N and V?"):
            st.write("$F_{BD,x} = 780 \\times (24/26)$. Sum forces in X to find $N_J$.")
            st.write("$F_{BD,y} = 780 \\times (10/26)$. Sum forces in Y (including the $160\\text{ lb}$ load) to find $V_J$.")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nj_val = st.number_input("Magnitude of Axial Force $N_J$ (lb):", min_value=0.0, format="%.1f")
        with col_c2:
            vj_val = st.number_input("Magnitude of Shear Force $V_J$ (lb):", min_value=0.0, format="%.1f")
            
        with st.expander("Need a hint for Bending Moment?"):
            st.write("Sum moments about Point J for the left segment. The $160\\text{ lb}$ force is $22\\text{ in.}$ away from J. The upward $F_{BD,y}$ force is $8\\text{ in.}$ away from J. What are their moment directions relative to J?")

        mj_val = st.number_input("Absolute Magnitude of Bending Moment $M_J$ (lb*in):", min_value=0.0, format="%.1f")
        
        if st.button("Check Internal Forces and Finish"):
            ok_nj = abs(nj_val - 720.0) < 1.0
            ok_vj = abs(vj_val - 140.0) < 1.0
            ok_mj = abs(mj_val - 1120.0) < 1.0
            
            if ok_nj and ok_vj and ok_mj:
                st.balloons()
                st.session_state.step_idx = 7
                st.rerun()
            else:
                if not ok_nj:
                    st.error("Check $N_J$. It must balance the horizontal component of $F_{BD}$.")
                if not ok_vj:
                    st.error("Check $V_J$. It must balance the net vertical forces on the left segment ($160$ down and $F_{BD,y}$ up).")
                if not ok_mj:
                    st.error("Check $M_J$. Moment equation: $(160 \\times 22) - (F_{BD,y} \\times 8)$.")

# ======================================================
# S — SANITY CHECK (Step 7)
# ======================================================
if st.session_state.step_idx >= 7:
    st.divider()
    st.header("S — Sanity Check")
    
    st.success("Calculations Complete!")
    
    st.markdown("### Final Internal Forces at J:")
    st.write("- **Axial Force ($N_J$)**: $720$ lb (Compression)")
    st.write("- **Shear Force ($V_J$)**: $140$ lb")
    st.write("- **Bending Moment ($M_J$)**: $1120$ lb·in")
    
    st.markdown("### Reflection")
    st.write("Think about your final results and check the boxes if they make physical sense:")
    
    check1 = st.checkbox("Because the strut BD pushes to the right against the beam at B, the segment ABJ is being squeezed against the cut at J, which explains why the normal force $N_J$ is in **Compression**.")
    check2 = st.checkbox("The bending moment at A is $0$. The moment at B is large because of the $160\\text{ lb}$ load over a $14\\text{ in.}$ arm. At J, the upward pull from the strut starts relieving that moment, showing why $M_J$ is smaller than the moment exactly at B.")
    
    if check1 and check2:
        st.info("You have successfully applied the S.T.A.T.I.C.S. method to find internal forces! Great job.")
        
        if st.button("Start New Problem"):
            st.session_state.clear()
            st.rerun()