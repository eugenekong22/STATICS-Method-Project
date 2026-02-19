import streamlit as st
import time
from datetime import timedelta

# Try to import drawable canvas
try:
    from streamlit_drawable_canvas import st_canvas
    _canvas_ok = True
except ImportError:
    _canvas_ok = False

st.set_page_config(page_title="STATICS Method — Truss Analysis", page_icon="🏗️", layout="centered")

# ==========================================
# 1. PROBLEM DEFINITION & IMAGE
# ==========================================
st.title("Truss Analysis: Method of Joints")

# --- 🖼️ PASTE YOUR IMAGE URL BELOW ---
# Replace the URL inside the quotes with the direct link to your problem image.
PROBLEM_IMAGE_URL = "https://i.imgur.com/QpHoGiS.jpeg"
# ------------------------------------

try:
    st.image(PROBLEM_IMAGE_URL, caption="Problem Diagram", use_container_width=True)
except Exception:
    st.error("Could not load image. Please check the PROBLEM_IMAGE_URL variable in the code.")

st.info("📄 **Reference:** Look at the diagram above showing a right-angled truss with a 500 N horizontal load.")

PROBLEM_TEXT = (
    "**The System:**\n"
    "A simple truss is supported by a pin at $A$ and a roller at $C$. A horizontal force of $500$ N acts to the right at joint $B$.\n\n"
    "**Dimensions:**\n"
    "* Height ($AB$) = $2$ m\n"
    "* Base ($AC$) = $2$ m\n\n"
    "**The Objective:**\n"
    "Determine the force in each member of the truss ($F_{AB}$, $F_{BC}$, $F_{AC}$) and indicate whether the members are in **Tension (T)** or **Compression (C)**."
)
st.markdown(PROBLEM_TEXT)
st.divider()

# ----------------------------
# 2. STATE MANAGEMENT
# ----------------------------
if "step_idx" not in st.session_state:
    st.session_state.step_idx = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "timer_finished" not in st.session_state:
    st.session_state.timer_finished = False
if "vocab_idx" not in st.session_state:
    st.session_state.vocab_idx = 0
if "s_given_sel" not in st.session_state:
    st.session_state.s_given_sel = set()
if "angle_correct" not in st.session_state: 
    st.session_state.angle_correct = False
if "bc_correct" not in st.session_state: 
    st.session_state.bc_correct = False
if "ab_correct" not in st.session_state: 
    st.session_state.ab_correct = False

STUDY_DURATION = 180 

VOCAB = [
    {"term": "Method of Joints", "def": "A process of analyzing a truss by finding equilibrium at each individual pin (joint). You must choose a starting joint carefully based on the number of unknowns."},
    {"term": "Tension (T)", "def": "A force that pulls a member apart. In a joint FBD, a tension force arrow points AWAY from the joint."},
    {"term": "Compression (C)", "def": "A force that squeezes a member. In a joint FBD, a compression force arrow points TOWARDS the joint."},
    {"term": "Two-Force Member", "def": "A truss member with pins at each end and no loads in between. Forces can only act strictly along the axis of the member."}
]

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
    st.caption("Read carefully and visualize what’s happening physically.")
    
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

    with st.container(border=True):
        st.subheader(f"Vocabulary Card {st.session_state.vocab_idx + 1}/{len(VOCAB)}")
        card = VOCAB[st.session_state.vocab_idx]
        st.markdown(f"**{card['term']}**")
        st.write(card['def'])
        c1, c2 = st.columns(2)
        if c1.button("⬅️ Prev") and st.session_state.vocab_idx > 0:
            st.session_state.vocab_idx -= 1
            st.rerun()
        if c2.button("Next ➡️") and st.session_state.vocab_idx < len(VOCAB)-1:
            st.session_state.vocab_idx += 1
            st.rerun()

    st.write("#### Identify Key Parameters")
    GIVEN_OPTS = [
        ("A 500 N force acts horizontally at Joint B", True),
        ("Support A is a Roller", False),  
        ("Support C can only provide a vertical reaction", True), 
        ("The height and base of the truss are both 2m", True)
    ]
    
    cols_g = st.columns(2)
    for i, (txt, is_correct) in enumerate(GIVEN_OPTS):
        with cols_g[i % 2]:
            if st.checkbox(txt, value=(txt in st.session_state.s_given_sel), key=f"g_{i}"):
                st.session_state.s_given_sel.add(txt)
            else:
                st.session_state.s_given_sel.discard(txt)

    if st.session_state.step_idx == 1 and st.session_state.timer_finished:
        if st.button("Check & Continue to T"):
            correct = sum(1 for t, c in GIVEN_OPTS if c and t in st.session_state.s_given_sel)
            wrongs = sum(1 for t, c in GIVEN_OPTS if not c and t in st.session_state.s_given_sel)
            if correct == 3 and wrongs == 0:
                st.success("Correct! Understanding the specific reaction capabilities of Pins vs Rollers is crucial.")
                st.session_state.step_idx = 2
                st.rerun()
            else:
                st.warning("Please review the support types carefully in your textbook before proceeding.")

# ======================================================
# T — TRANSLATE TO DIAGRAM (Step 2: FBD)
# ======================================================
if st.session_state.step_idx >= 2:
    st.divider()
    st.header("T — Translate to a Diagram (FBD)")

    st.subheader("1. Strategic Starting Point")
    st.markdown("In the Method of Joints, you must start at a joint with a specific maximum number of unknowns.")
    
    with st.expander("Need a hint?"):
        st.write("Count the unknown member forces and unknown reaction forces at each joint. You only have two 2D equilibrium equations per joint ($\\Sigma F_x$ and $\\Sigma F_y$). Therefore, how many unknowns can you solve for at once?")
        st.write ("Youtube Link: https://www.youtube.com/watch?v=_rK02neOF18")

    joint_guess = st.radio("Which joint should we analyze first to bypass finding global reactions?", 
                           ["Joint A", "Joint B", "Joint C"])
    
    if joint_guess == "Joint B":
        st.success("Correct! Starting at Joint B is the most efficient path since it has exactly 2 unknowns.")
        
        st.subheader("2. Draw FBD of Joint B")
        st.info("Use the **Line Tool** to draw the Free Body Diagram of **Joint B** only.")
        
        if _canvas_ok:
            canvas_fbd = st_canvas(
                stroke_width=3, stroke_color="#000", background_color="#fff",
                height=300, width=500, drawing_mode="line", display_toolbar=True, key="canvas_fbd_jointb"
            )

            if st.button("Check FBD"):
                num_lines = len(canvas_fbd.json_data["objects"]) if canvas_fbd.json_data else 0
                if 3 <= num_lines <= 5:
                    st.success("FBD detected. Proceed to Assign.")
                    st.session_state.step_idx = 3
                    st.rerun()
                else:
                    st.error(f"Detected {num_lines} lines. Think about all external loads and connected members at Joint B.")
    elif joint_guess:
        st.error("Count the unknowns again. Joint A has reactions + members. Joint C has a reaction + members. Find the joint with exactly two unknowns.")

# ======================================================
# A — ASSIGN (Step 3: Coordinates & Assumptions)
# ======================================================
if st.session_state.step_idx >= 3:
    st.divider()
    st.header("A — Assign Coordinates and Assumptions")
    
    st.write("Set up your coordinate system and assume force directions.")
    st.radio("Standard Coordinate System:", ["+X is Right, +Y is Up"], disabled=True)
    
    st.markdown("**Assumption Strategy:**")
    q_assume = st.radio("When drawing an unknown member force on a joint FBD, what is the standard engineering assumption?",
                        ["Assume the member is in Compression (pointing towards the joint)",
                         "Assume the member is in Tension (pointing away from the joint)",
                         "Guess based on visual inspection"])
    
    if st.button("Acknowledge Assumptions"):
        if "Tension" in q_assume:
            st.success("Correct! Assuming Tension means a positive math result confirms Tension, and a negative math result means Compression. This keeps signs consistent.")
            st.session_state.step_idx = 4
            st.rerun()
        else:
            st.warning("While you *can* guess, assuming Tension universally prevents sign errors later. Try selecting the standard assumption.")

# ======================================================
# T — TRANSLATE TO COMPONENTS (Step 4: Breakdown)
# ======================================================
if st.session_state.step_idx >= 4:
    st.divider()
    st.header("T — Translate Forces to Components")
    st.caption("Break each force into x- and y-components using trigonometry.")
    
    st.write("Look at Joint B. $F_{AB}$ is vertical. The 500 N force is horizontal. But $F_{BC}$ is diagonal.")
    
    st.subheader("1. Find the Angle of Member BC")
    st.markdown("Look at the global dimensions of the truss. Height ($AB$) = $2$ m. Base ($AC$) = $2$ m.")
    
    with st.expander("Need a hint?"):
        st.write("You have the Opposite and Adjacent sides of the large triangle. Which trigonometric function relates these two sides to an angle?")
        st.write("Youtube Link: https://www.youtube.com/watch?v=gSGbYOzjynk1")
    
    angle_in = st.number_input("What is the interior angle of Member BC relative to the horizontal (degrees)?", min_value=0.0, max_value=90.0)
    
    if st.button("Check Angle"):
        if abs(angle_in - 45.0) < 0.1:
            st.success("Correct. The geometry forms a 45-45-90 right triangle.")
            st.session_state.angle_correct = True
        else:
            st.error("Check your trigonometry. Set up the ratio of opposite over adjacent and find the inverse.")

    if st.session_state.get("angle_correct"):
        st.subheader("2. Define Components of $F_{BC}$")
        st.write("Assume $F_{BC}$ is in **Tension**.")
        st.info("💡 **Tip:** Use the $45^{\\circ}$ angle at the **bottom** of the triangle (Joint C) to define your components via alternate interior angles.")
        
        with st.expander("Need a hint?"):
            st.write("If a vector points away from Joint B (Tension), it points down and to the right. What are the standard signs (+ or -) for X and Y in that direction?")
            st.write("Youutbe Link: https://www.youtube.com/watch?v=dC4cudpxVQw")

        q_x_comp = st.radio("What is the $X$-component of $F_{BC}$?", 
                            ["+F_BC * cos(45°)", "-F_BC * cos(45°)", "+F_BC * sin(45°)"])
        q_y_comp = st.radio("What is the $Y$-component of $F_{BC}$?", 
                            ["+F_BC * sin(45°)", "-F_BC * sin(45°)", "-F_BC * cos(45°)"])
                            
        if st.button("Verify Components"):
            if "+F_BC * cos(45°)" in q_x_comp and "-F_BC * sin(45°)" in q_y_comp:
                st.success("Correct. Tension pulls down and right, meaning $+X$ and $-Y$.")
                st.session_state.step_idx = 5
                st.rerun()
            else:
                st.error("Review your quadrant signs and trig functions. If it pulls away from the top-left joint, where is it heading?")

# ======================================================
# I — IMPLEMENT (Step 5: Equilibrium Equations)
# ======================================================
if st.session_state.step_idx >= 5:
    st.divider()
    st.header("I — Implement Equilibrium Equations")
    st.caption("Apply $\\sum F_x = 0$ and $\\sum F_y = 0$ at Joint B.")
    
    st.write("We have two unknown magnitudes at Joint B: $F_{AB}$ and $F_{BC}$.")
    
    with st.expander("Need a hint?"):
        st.write("Write out both the $\\sum F_x$ and $\\sum F_y$ equations on scratch paper based on your components from the previous step. Which equation contains only ONE unknown variable?")
        st.write ("Youtube Link: https://www.youtube.com/watch?v=jQDEOwrR4UU")

    strat_q = st.radio("Which equation should we evaluate FIRST to solve for $F_{BC}$ directly?", 
                       ["Sum of Forces in Y = 0", "Sum of Forces in X = 0"])
    
    if st.button("Confirm Equation Strategy"):
        if strat_q == "Sum of Forces in X = 0":
            st.success("Correct. Since $F_{AB}$ is purely vertical, the X-equation only contains the external load and the horizontal component of $F_{BC}$.")
            st.session_state.step_idx = 6
            st.rerun()
        else:
            st.error("Evaluate the variables in the Y-equation. Can you solve an equation with two unknown variables?")

# ======================================================
# C — COMPUTE (Step 6: Guided Math)
# ======================================================
if st.session_state.step_idx >= 6:
    st.divider()
    st.header("C — Compute Results")
    st.caption("Solve algebraically for unknown magnitudes and angles.")

    # --- Part 1: Member BC ---
    st.subheader("Part 1: Force in Member BC")
    st.write("Set up your $\\sum F_x = 0$ equation at Joint B and solve.")
    
    with st.expander("Need a hint?"):
        st.write("Your equation should sum the external 500 N force and the X-component of $F_{BC}$ you identified in Step 4 to zero. Isolate $F_{BC}$.")

    col1, col2 = st.columns(2)
    f_bc_val = col1.number_input("Magnitude of $F_{BC}$ (N):", min_value=0.0)
    f_bc_state = col2.selectbox("State of BC:", ["Tension (T)", "Compression (C)"], key="bc_state")
    
    if st.button("Check BC"):
        if abs(f_bc_val - 707.1) < 2.0 and f_bc_state == "Compression (C)":
            st.success("Correct! $F_{BC} = 707.1$ N (C).")
            st.session_state.bc_correct = True
        else:
            st.error("Check your algebra. If your calculated value is negative, what does that mean for the state of the member?")

    # --- Part 2: Member AB ---
    if st.session_state.get("bc_correct"):
        st.divider()
        st.subheader("Part 2: Force in Member AB")
        st.write("Now set up your $\\sum F_y = 0$ equation at Joint B and solve.")
        
        with st.expander("Need a hint?"):
            st.write("Your equation should sum $F_{AB}$ (which way did you assume it points?) and the Y-component of $F_{BC}$. **Crucial:** Since you discovered $F_{BC}$ is in Compression, how does that change the sign you plug into your equation?")

        col3, col4 = st.columns(2)
        f_ab_val = col3.number_input("Magnitude of $F_{AB}$ (N):", min_value=0.0)
        f_ab_state = col4.selectbox("State of AB:", ["Tension (T)", "Compression (C)"], key="ab_state")
        
        if st.button("Check AB"):
            if abs(f_ab_val - 500.0) < 1.0 and f_ab_state == "Tension (T)":
                st.success("Correct! $F_{AB} = 500$ N (T).")
                st.session_state.ab_correct = True
            else:
                st.error("Think carefully about the signs. If $F_{BC}$ is in compression, it pushes *up* on Joint B. What must $F_{AB}$ do to keep the joint from flying upwards?")

    # --- Part 3: Member AC (Final Calculation) ---
    if st.session_state.get("ab_correct"):
        st.divider()
        st.subheader("Part 3: Force in Member AC")
        st.write("Move your analysis to **Joint C** to find the force in the bottom member.")
        
        with st.expander("Need a hint?"):
            st.write("Mentally visualize the FBD of Joint C. Sum the forces in the X-direction. You have $F_{AC}$ (assumed pulling left) and the X-component of $F_{BC}$ (which you know is in compression, pushing into Joint C).")

        col5, col6 = st.columns(2)
        f_ac_val = col5.number_input("Magnitude of $F_{AC}$ (N):", min_value=0.0)
        f_ac_state = col6.selectbox("State of AC:", ["Tension (T)", "Compression (C)"], key="ac_state")
        
        if st.button("Check AC and Finish"):
            if abs(f_ac_val - 500.0) < 1.0 and f_ac_state == "Tension (T)":
                st.balloons()
                st.session_state.step_idx = 7
                st.rerun()
            else:
                st.error("Look at the horizontal forces at Joint C. If the diagonal member is pushing down and to the right, what must the bottom horizontal member do to stop Joint C from moving right?")

# ======================================================
# S — SANITY CHECK (Step 7)
# ======================================================
if st.session_state.step_idx >= 7:
    st.divider()
    st.header("S — Sanity Check")
    st.caption("Do the results make physical sense?")
    
    st.success("Calculations Complete!")
    
    st.markdown("### Final Truss Forces:")
    st.write("* **$F_{BC}$**: 707.1 N (Compression)")
    st.write("* **$F_{AB}$**: 500.0 N (Tension)")
    st.write("* **$F_{AC}$**: 500.0 N (Tension)")
    
    st.markdown("""
    **Does this make physical sense?**
    * Imagine physically pushing Joint B to the right with 500 N. 
    * The diagonal member ($BC$) gets squeezed against the ground support at C $\\rightarrow$ **Compression**.
    * Because Joint B is being pushed, it wants to lift up and pivot around C. Member $AB$ acts like a rope anchoring it to the pin at A $\\rightarrow$ **Tension**.
    * Since $BC$ pushes down and right on roller C, the roller would slide away to the right if member $AC$ wasn't holding it back $\\rightarrow$ **Tension**.
    """)
    
    st.info("You have successfully applied the Method of Joints using the S.T.A.T.I.C.S. approach.")
    
    if st.button("Start New Problem"):
        st.session_state.clear()
        st.rerun()