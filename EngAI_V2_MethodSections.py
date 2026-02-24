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

st.set_page_config(page_title="STATICS Method — Roof Truss", page_icon="🏠", layout="centered")

# ==========================================
# 1. PROBLEM DEFINITION & IMAGE
# ==========================================
st.title("Roof Truss Analysis: Method of Sections")

# Replace this URL with the direct link to the image if hosting online, 
# or use a local file path if running locally (e.g., "truss_problem.png")
PROBLEM_IMAGE_URL = "https://i.imgur.com/FQHvFiW.jpeg"

try:
    st.image(PROBLEM_IMAGE_URL, caption="Roof Truss Diagram", use_container_width=True)
except Exception:
    st.error("Could not load image. Please check the PROBLEM_IMAGE_URL variable in the code.")

st.info("📄 **Reference:** Refer to the uploaded diagram of the roof truss with top and bottom loads.")

PROBLEM_TEXT = (
    "**The System:**\n"
    "A Fink roof truss is subjected to multiple point loads. "
    "Top loads at B, D, F, H, J are $1\\text{ kN}$ each. "
    "Bottom loads at C, E, G are $5\\text{ kN}$ each.\n\n"
    "**Dimensions:**\n"
    "* Total span: 6 panels @ $5\\text{ m} = 30\\text{ m}$\n"
    "* Peak height ($h$) at node F = $8\\text{ m}$\n\n"
    "**The Objective:**\n"
    "Determine the forces in members **FH**, **GH**, and **GI** and indicate whether they are in Tension (T) or Compression (C)."
)
st.markdown(PROBLEM_TEXT)
st.divider()

# ----------------------------
# 2. STATE MANAGEMENT
# ----------------------------
if "step_idx" not in st.session_state: st.session_state.step_idx = 0
if "start_time" not in st.session_state: st.session_state.start_time = None
if "timer_finished" not in st.session_state: st.session_state.timer_finished = False
if "vocab_idx" not in st.session_state: st.session_state.vocab_idx = 0
if "s_given_sel" not in st.session_state: st.session_state.s_given_sel = set()
if "ly_correct" not in st.session_state: st.session_state.ly_correct = False
if "h_height_correct" not in st.session_state: st.session_state.h_height_correct = False
if "fgi_correct" not in st.session_state: st.session_state.fgi_correct = False
if "ffh_correct" not in st.session_state: st.session_state.ffh_correct = False

STUDY_DURATION = 180 

VOCAB = [
    {"term": "Method of Sections", "def": "An analytical technique where you 'cut' through the truss (passing through the members you want to find) and analyze an entire section as a rigid body."},
    {"term": "Rigid Body Equilibrium", "def": "Because the entire section is in equilibrium, you can use ΣFx=0, ΣFy=0, and crucially, ΣM=0 about ANY point in space."},
    {"term": "Asymmetric Loading", "def": "When forces are not perfectly mirrored across the center of a structure. You cannot assume reactions or member forces are equal on both sides!"},
    {"term": "Line of Action", "def": "The infinite geometric line along which a force acts. You can slide a force anywhere along its line of action when calculating moments."}
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
        timer_placeholder.warning(f"⏳ **Focus Period:** {str(timedelta(seconds=remaining))[2:7]} remaining. Watch out for traps in the load layout!")
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
        ("The truss is symmetrically loaded.", False),
        ("The truss geometry is symmetric.", True),
        ("The Method of Sections is more efficient than Joints here.", True),
        ("The total downward load is 20 kN.", True)
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
                st.success("Correct! **TRAP AVOIDED:** While the frame is symmetric, the 5 kN loads are ONLY on the left side. You cannot assume symmetry for the reactions!")
                st.session_state.step_idx = 2
                st.rerun()
            else:
                st.warning("Look very closely at the 5 kN loads. Are they mirrored perfectly on the right side of the truss? Check your selections.")

# ======================================================
# T — TRANSLATE TO DIAGRAM (Step 2: FBD)
# ======================================================
if st.session_state.step_idx >= 2:
    st.divider()
    st.header("T — Translate to a Diagram (FBD)")

    st.subheader("1. Strategic Cutting")
    st.markdown("To find members FH, GH, and GI, we need to make a 'cut' completely through the truss, severing those three members.")
    
    with st.expander("Need a hint?"):
        st.write("Once you make the cut, you split the truss into a Left half and a Right half. You only need to analyze one. Count the number of external forces on the Left side vs the Right side. Which involves less math?")

    section_guess = st.radio("Which section of the cut truss should we draw an FBD of and analyze?", 
                           ["The Left Section (Nodes A through G)", "The Right Section (Nodes H through L)"])
    
    if section_guess == "The Right Section (Nodes H through L)":
        st.success("Correct! The right section only has two 1 kN loads and the reaction at L. The left section is cluttered with the heavy 5 kN loads.")
        
        st.subheader("2. Draw FBD of the Right Section")
        st.info("Use the **Line Tool** to draw the FBD of the Right Section.")
        st.caption("Include the partial truss, the external loads at J and H, the reaction at L, and the three severed members pointing AWAY from the cut.")
        
        if _canvas_ok:
            canvas_fbd = st_canvas(
                stroke_width=3, stroke_color="#000", background_color="#fff",
                height=350, width=600, drawing_mode="line", display_toolbar=True, key="canvas_fbd_section"
            )

            if st.button("Check FBD"):
                num_lines = len(canvas_fbd.json_data["objects"]) if canvas_fbd.json_data else 0
                if num_lines >= 4:
                    st.success("FBD detected. Proceed to Assign.")
                    st.session_state.step_idx = 3
                    st.rerun()
                else:
                    st.error("Please draw the external loads, the reaction, and the three unknown cut member vectors.")
    elif section_guess:
        st.error("Think about efficiency. You *could* use the left section, but why do extra math? Look at the loads again.")

# ======================================================
# A — ASSIGN (Step 3: Coordinates & Global Reactions)
# ======================================================
if st.session_state.step_idx >= 3:
    st.divider()
    st.header("A — Assign Coordinates & Find Global Reactions")
    
    st.write("Before we can evaluate the Right Section, we need to know the upward reaction force acting on it at node L ($L_y$).")
    
    with st.expander("Need a hint?"):
        st.write("Look at the ENTIRE, uncut truss. To find $L_y$ in one step, sum the moments about pin A. Don't forget any of the top or bottom loads! The total length is 30m, meaning each of the 6 panels is 5m wide.")
        st.write("Youtube: https://www.youtube.com/watch?v=O8BRl0xLlJw")


    ly_val = st.number_input("Calculate the global vertical reaction at L ($L_y$) in kN:", min_value=0.0)
    
    if st.button("Check Reaction L_y"):
        # Sum moments about A = 0
        # 1*(5+10+15+20+25) + 5*(5+10+15) = 75 + 150 = 225.
        # Ly * 30 = 225 => Ly = 7.5
        if abs(ly_val - 7.5) < 0.2:
            st.success("Correct! $L_y = 7.5\\text{ kN}$. You are ready to focus purely on the Right Section.")
            st.session_state.ly_correct = True
            st.session_state.step_idx = 4
            st.rerun()
        else:
            st.error("Check your moment arms. Top loads are at x = 5, 10, 15, 20, 25. Bottom loads are at x = 5, 10, 15. The pivot A is at x = 0.")

# ======================================================
# T — TRANSLATE TO COMPONENTS (Step 4: Geometry)
# ======================================================
if st.session_state.step_idx >= 4:
    st.divider()
    st.header("T — Translate Forces to Components (Geometry)")
    st.caption("We need the exact coordinates/heights of the nodes where we made our cut.")
    
    st.markdown("We know Node F is at the center ($x=15\\text{m}$) and is $8\\text{m}$ high. What about Node H?")
    
    with st.expander("Need a hint?"):
        st.write("Node H is located at $x=20\\text{m}$. That is $10\\text{m}$ away from the right edge (L). Because the roof is a straight line, use similar triangles relative to the right edge.")
        st.write("What is the angle at L? We can use that angle to calculate the height of HI")
        st.write("Youtube: https://www.youtube.com/watch?v=i3bjEOA5_zc")

    h_height = st.number_input("Calculate the vertical height of Node H (in meters):", min_value=0.0)
    
    if st.button("Check Geometry"):
        # Height at H: (8 / 15) * 10 = 5.333
        if abs(h_height - 5.333) < 0.1:
            st.success("Correct! Node H is approx $5.33\\text{ m}$ high. (Fractionally, $16/3\\text{ m}$).")
            st.session_state.h_height_correct = True
        else:
            st.error("Set up a ratio: Height at Center / Distance to L = Height at H / Distance to L.")

    if st.session_state.get("h_height_correct"):
        st.subheader("Component Strategy")
        st.write("Assume all cut members ($F_{FH}, F_{GH}, F_{GI}$) are in **Tension** (pulling AWAY from the right section).")
        st.info("💡 **Tip:** You will use this height geometry directly in your moment equations in the next step. You don't necessarily need angles (sine/cosine) if you use distances and slopes!")
        
        if st.button("Proceed to Equations"):
            st.session_state.step_idx = 5
            st.rerun()

# ======================================================
# I — IMPLEMENT (Step 5: Equilibrium Equations)
# ======================================================
if st.session_state.step_idx >= 5:
    st.divider()
    st.header("I — Implement Equilibrium Equations")
    st.caption("Look ONLY at the Right Section. Apply your 2D equilibrium tools.")
    
    st.write("You have 3 unknowns: $F_{FH}$, $F_{GH}$, and $F_{GI}$. You want to write equations that isolate one variable at a time.")
    
    with st.expander("Need a hint?"):
        st.write("To isolate a single force, sum moments about the point in space where the *other two* unknown forces intersect. It doesn't matter if that intersection point is physically on your 'Right Section' or not!")

    strat_gi = st.radio("To find the bottom chord $F_{GI}$ directly, where should you sum moments?", 
                       ["Node G", "Node H", "Node F"])
    
    if st.button("Confirm Strategy"):
        if strat_gi == "Node H":
            st.success("Exactly! Both $F_{FH}$ and $F_{GH}$ pass directly through Node H. Summing moments there eliminates them, leaving only $F_{GI}$ and the external loads.")
            st.session_state.step_idx = 6
            st.rerun()
        else:
            st.error("Look at where the lines of action for the forces you want to IGNORE cross each other.")

# ======================================================
# C — COMPUTE (Step 6: Guided Math)
# ======================================================
if st.session_state.step_idx >= 6:
    st.divider()
    st.header("C — Compute Results")
    st.caption("Solve your equations carefully.")

    # --- Part 1: Member GI ---
    st.subheader("Part 1: Force in Member GI")
    st.write("Use $\\sum M_H = 0$ on the Right Section. Assume $F_{GI}$ is in Tension (pulling left).")
    st.write("Use $\\sum M_H = 0$ on the Right Section. Assume $F_{GI}$ is in Tension (pulling left).")
    
    with st.expander("Need a hint for GI?"):
        st.write("Pivot at H ($x=20, y=5.333$). Forces creating moments: $L_y$ (pushing up at $x=30$), the 1kN load at J ($x=25$), and $F_{GI}$ (pulling left along the bottom, $y=0$). What are their perpendicular moment arms?")
        st.write("Youtube: https://www.youtube.com/watch?v=JU6-eo4W3Qk")

    col1, col2 = st.columns(2)
    f_gi_val = col1.number_input("Magnitude of $F_{GI}$ (kN):", min_value=0.0)
    f_gi_state = col2.selectbox("State of GI:", ["Tension (T)", "Compression (C)"], key="gi_state")
    
    if st.button("Check GI"):
        # Ly(10) CCW, 1kN_J(5) CW. F_GI pulls left at y=0. Pivot is at y=5.333.
        # Pulling left from the bottom against a top pivot creates CCW moment.
        # 7.5*10 - 1*5 + F_GI*5.333 = 0 -> 70 + F_GI*5.333 = 0 -> F_GI = -13.125
        if abs(f_gi_val - 13.1) < 0.2 and f_gi_state == "Tension (T)":
            st.success("Correct! $F_{GI} = 13.1\\text{ kN}$ (T).")
            st.session_state.fgi_correct = True
        else:
            st.error("Check your moments. $L_y$ creates a Counter-Clockwise moment. The load at J is Clockwise. If $F_{GI}$ pulls Left at the bottom, does it rotate CCW or CW around H?")

    # --- Part 2: Member FH ---
    if st.session_state.get("fgi_correct"):
        st.divider()
        st.subheader("Part 2: Force in Member FH")
        st.write("To isolate the top chord $F_{FH}$, sum moments about Node G ($x=15, y=0$).")
        
        with st.expander("Need a hint for FH?"):
            st.write("Extend the line of action for $F_{FH}$. It passes exactly through Node F ($x=15, y=8$). Because F is directly above your pivot G, only the horizontal component of $F_{FH}$ creates a moment! Find the $x$-component of $F_{FH}$ based on its slope.")
            st.write("Youtube: https://www.youtube.com/watch?v=JU6-eo4W3Qk")

        col3, col4 = st.columns(2)
        f_fh_val = col3.number_input("Magnitude of $F_{FH}$ (kN):", min_value=0.0)
        f_fh_state = col4.selectbox("State of FH:", ["Tension (T)", "Compression (C)"], key="fh_state")
        
        if st.button("Check FH"):
            # Pivot at G. Ly(15) CCW, J(10) CW, H(5) CW.
            # 7.5*15 - 1*10 - 1*5 = 112.5 - 10 - 5 = 97.5 CCW.
            # FH_x * 8 = 97.5 -> FH_x = 12.1875
            # FH_x = FH * (15/17) -> FH = 13.8125
            if abs(f_fh_val - 13.8) < 0.2 and f_fh_state == "Compression (C)":
                st.success("Correct! $F_{FH} = 13.8\\text{ kN}$ (C).")
                st.session_state.ffh_correct = True
            else:
                st.error("Calculate the moment arm correctly. The line of action of $F_{FH}$ passes through F. If you break $F_{FH}$ into X and Y components at F, the Y component passes through G (0 moment). Use the X component and the $8\\text{m}$ height.")

    # --- Part 3: Member GH (Final Calculation) ---
    if st.session_state.get("ffh_correct"):
        st.divider()
        st.subheader("Part 3: Force in Diagonal Member GH")
        st.write("With only one unknown left, you can use $\\sum F_y = 0$ on the Right Section.")
        
        with st.expander("Need a hint for GH?"):
            st.write("Sum all vertical forces on the right section: $L_y$ (up), external loads at J and H (down), the vertical component of $F_{FH}$ (you know it's in Compression, so it pushes INTO the right section at H... which way is that vertically?), and the vertical component of $F_{GH}$.")
            st.write("Youtube: https://www.youtube.com/watch?v=JU6-eo4W3Qk")

        col5, col6 = st.columns(2)
        f_gh_val = col5.number_input("Magnitude of $F_{GH}$ (kN):", min_value=0.0)
        f_gh_state = col6.selectbox("State of GH:", ["Tension (T)", "Compression (C)"], key="gh_state")
        
        if st.button("Check GH and Finish"):
            # Ly(7.5 up), J(1 down), H(1 down). Net external = 5.5 UP.
            # FH is compression (pushes down & right into H). Y-comp = 13.8125 * (8/17) = 6.5 DOWN.
            # Net so far = 5.5 UP + 6.5 DOWN = 1.0 DOWN.
            # GH must push 1.0 UP. To push UP on node H from below, it must push INTO H (Compression).
            # GH_y = 1.0. GH = 1.0 * (sqrt(5^2 + (16/3)^2) / (16/3)) = 1.37
            if abs(f_gh_val - 1.37) < 0.1 and f_gh_state == "Compression (C)":
                st.balloons()
                st.session_state.step_idx = 7
                st.rerun()
            else:
                st.error("Track the vertical forces. If the top chord ($F_{FH}$) is in compression, it is pushing down and to the right against Node H. Be sure to include its downward component in your Y sum!")

# ======================================================
# S — SANITY CHECK (Step 7)
# ======================================================
if st.session_state.step_idx >= 7:
    st.divider()
    st.header("S — Sanity Check")
    st.caption("Do the results make physical sense?")
    
    st.success("Calculations Complete!")
    
    st.markdown("### Final Truss Forces:")
    st.write("* **$F_{FH}$**: $13.81\\text{ kN}$ (Compression)")
    st.write("* **$F_{GI}$**: $13.13\\text{ kN}$ (Tension)")
    st.write("* **$F_{GH}$**: $1.37\\text{ kN}$ (Compression)")
    
    st.markdown("""
    **Does this make physical sense?**
    * **Top chords** of a simply supported truss are almost always in **Compression** because the truss is bending downward like a U-shape, squeezing the top.
    * **Bottom chords** are almost always in **Tension** as the bottom tries to stretch apart.
    * Check $\\sum F_x = 0$ on the right section:
        * $F_{GI}$ pulls Left ($13.13\\text{ kN}$).
        * $F_{FH}$ (Compression) pushes Right. Its X-component is approx $12.19\\text{ kN}$.
        * $F_{GH}$ (Compression) pushes Right. Its X-component is approx $0.94\\text{ kN}$.
        * $12.19 + 0.94 = 13.13$. The horizontal forces perfectly balance!
    """)
    
    st.info("You have successfully applied the Method of Sections using the S.T.A.T.I.C.S. approach.")
    
    if st.button("Start New Problem"):
        st.session_state.clear()
        st.rerun()