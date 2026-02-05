import streamlit as st
import time
from datetime import timedelta

# Try to import drawable canvas
try:
    from streamlit_drawable_canvas import st_canvas
    _canvas_ok = True
except ImportError:
    _canvas_ok = False

st.set_page_config(page_title="STATICS Method — Beam Reactions", page_icon="🏗️", layout="centered")

# ----------------------------
# 1. PROBLEM DEFINITION (Always Visible)
# ----------------------------
st.title("Beam Reactions Exercise")

PROBLEM_TEXT = (
    "A beam is supported by a roller at A and a pin at B. "
    "Three vertical loads are applied: P = 15 kips at 3 ft from A, "
    "6 kips at 2 ft to the right of B, and another 6 kips at the far right end. "
    "Determine the reactions at supports A and B."
)
st.info(PROBLEM_TEXT)
st.divider()

# ----------------------------
# 2. STATE MANAGEMENT
# ----------------------------
if "current_step_idx" not in st.session_state:
    st.session_state.current_step_idx = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "timer_finished" not in st.session_state:
    st.session_state.timer_finished = False
if "vocab_idx" not in st.session_state:
    st.session_state.vocab_idx = 0

STUDY_DURATION = 180 

VOCAB = [
    {"term": "Roller Support", "def": "Allows rotation and horizontal movement. Prevents vertical movement. Result: 1 Vertical Reaction (Ay)."},
    {"term": "Pin Support", "def": "Prevents translation in any direction. Result: 2 Reactions (Vertical By & Horizontal Bx)."},
    {"term": "Static Determinacy", "def": "A structure is determinate if the number of unknowns equals the number of available equilibrium equations."},
    {"term": "Moment (M)", "def": "M = Force × Perpendicular Distance. It is the 'twist' applied to a point."}
]

# ----------------------------
# 3. NAVIGATION / RESET
# ----------------------------
if st.sidebar.button("🔄 Reset Problem"):
    st.session_state.clear()
    st.rerun()

if st.session_state.current_step_idx == 0:
    if st.button("▶️ Begin STATICS Method"):
        st.session_state.current_step_idx = 1
        st.session_state.start_time = time.time()
        st.rerun()
    st.stop()

# ======================================================
# S — STUDY (Step 1)
# ======================================================
if st.session_state.current_step_idx >= 1:
    st.header("S — Study & Vocabulary")
    
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
        card = VOCAB[st.session_state.vocab_idx]
        st.subheader(card["term"])
        st.write(card["def"])
        c1, c2 = st.columns(2)
        if c1.button("⬅️ Prev") and st.session_state.vocab_idx > 0:
            st.session_state.vocab_idx -= 1
            st.rerun()
        if c2.button("Next ➡️") and st.session_state.vocab_idx < len(VOCAB)-1:
            st.session_state.vocab_idx += 1
            st.rerun()

    if st.session_state.current_step_idx == 1 and st.session_state.timer_finished:
        if st.button("Move to T — Translate"):
            st.session_state.current_step_idx = 2
            st.rerun()

# ======================================================
# T — TRANSLATE (Step 2)
# ======================================================
if st.session_state.current_step_idx >= 2:
    st.divider()
    st.header("T — Translate (FBD)")
    st.write("Draw your Free Body Diagram. Include the beam, the 3 applied loads, and the reaction forces at A and B.")
    
    
    if _canvas_ok:
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000", background_color="#eee",
            height=250, width=650, drawing_mode="line", key="fbd_draw_v6"
        )
        
        if st.session_state.current_step_idx == 2:
            if st.button("Check Drawing"):
                num_lines = len(canvas_result.json_data["objects"]) if canvas_result.json_data else 0
                if 6 <= num_lines <= 9:
                    st.success("FBD looks solid. Let's assign coordinates.")
                    st.session_state.current_step_idx = 3
                    st.rerun()
                else:
                    st.error(f"Detection: {num_lines} lines. Did you include the beam + all loads and reactions?")

# ======================================================
# A — ASSIGN (Step 3: Reference Axes)
# ======================================================
if st.session_state.current_step_idx >= 3:
    st.divider()
    st.header("A — Assign Reference Axes")
    st.write("Before implementing equations, define your positive directions.")
    
    col1, col2 = st.columns(2)
    y_axis = col1.selectbox("Positive Vertical Direction:", ["Upward (+y)", "Downward (-y)"])
    m_axis = col2.selectbox("Positive Rotation:", ["Counter-Clockwise (+M)", "Clockwise (-M)"])
    
    if st.session_state.current_step_idx == 3:
        if st.button("Set Axes"):
            st.session_state.current_step_idx = 4
            st.rerun()

# ======================================================
# I — IMPLEMENT (Step 4: Logic of Unknowns)
# ======================================================
if st.session_state.current_step_idx >= 4:
    st.divider()
    st.header("I — Implement Equations")
    
    with st.expander("💡 Implement Helper: Static Equilibrium"):
        st.write("To solve a 2D statics problem, we have 3 equations: $\sum F_x = 0$, $\sum F_y = 0$, and $\sum M_z = 0$.")

    q1 = st.number_input("How many unknown reaction forces are in this problem?", min_value=0, step=1)
    q2 = st.multiselect("Which equations will we need to solve for all unknowns?", 
                        ["Sum of Forces in X", "Sum of Forces in Y", "Sum of Moments", "Energy Balance"])
    
    if st.session_state.current_step_idx == 4:
        if st.button("Validate Logic"):
            if q1 == 3 and "Sum of Forces in X" in q2 and "Sum of Forces in Y" in q2 and "Sum of Moments" in q2:
                st.success("Correct. We have Ay, By, and Bx (3 unknowns) and 3 equations.")
                st.session_state.current_step_idx = 5
                st.rerun()
            else:
                st.error("Think about the supports: A roller has 1 reaction, a pin has 2. How many equations do we usually use in 2D Statics?")

# ======================================================
# C — COMPUTE (Step 5 & 6: Guided Solving)
# ======================================================
if st.session_state.current_step_idx >= 5:
    st.divider()
    st.header("C — Compute Results")

    # --- Part 1: Strategic Choice & Solving for Ay ---
    st.subheader("Part 1: Selecting the Pivot Point")
    
    with st.expander("💡 Compute Helper: Which point is better?"):
        st.write("In Statics, we want to write one equation with only **one** unknown. Look at your FBD:")
        st.write("- **Point A** has 1 unknown reaction ($A_y$).")
        st.write("- **Point B** has 2 unknown reactions ($B_y$ and $B_x$).")
        st.write ("Moment Refresher Video: https://www.youtube.com/watch?v=O8BRl0xLlJw")
        st.info("If you sum moments at a point where many unknowns meet, those forces disappear from your equation (distance = 0). Which point simplifies your math more?")

    # Guiding them to choose B
    choice_pivot = st.radio(
        "Based on the helper above, which point should we sum moments about to solve for $A_y$ in one step?",
        ["Point A", "Point B"],
        index=0
    )

    if choice_pivot == "Point A":
        st.warning("You can do this, but you will still have $B_y$ in your equation. Try choosing the point with more unknowns instead!")
    else:
        st.success("Great choice! Summing at B eliminates both $B_x$ and $B_y$, leaving only $A_y$.")
        
        st.write("Now, sum moments about **Point B** ($\sum M_B = 0$):")
        
        ans_ay = st.number_input("Enter your calculated value for Ay (kips):", value=0.0, key="input_ay")
        
        if st.session_state.current_step_idx == 5:
            if st.button("Check Ay"):
                if abs(ans_ay - 6.0) < 0.1:
                    st.success("Correct! $A_y = 6$ kips.")
                    st.session_state.current_step_idx = 6
                    st.rerun()
                else:
                    st.error("Hint: At Point B, the 15k load is 6ft to the left (+M), and $A_y$ is 9ft to the left (-M). The two 6k loads are to the right. Set them to zero and solve.")

# --- Part 2: Solving for Reactions at B ---
if st.session_state.current_step_idx >= 6:
    st.divider()
    st.subheader("Part 2: Solving for Reactions at B")
    
    with st.expander("💡 Compute Helper: The Final Balance"):
        st.write("You now have $A_y$. The hardest part is over!")
        st.markdown("""
        1. **Horizontal:** Are there any forces pushing the beam left or right? If not, $B_x$ must be...
        2. **Vertical:** Use $\sum F_y = 0$. (Total Up = Total Down).
        """)

    col1, col2 = st.columns(2)
    ans_bx = col1.number_input("Value of Bx (kips):", value=0.0, key="input_bx")
    ans_by = col2.number_input("Value of By (kips):", value=0.0, key="input_by")
    
    

    if st.session_state.current_step_idx == 6:
        if st.button("Final Computation Check"):
            correct_bx = (ans_bx == 0)
            correct_by = (abs(ans_by - 21.0) < 0.1)
            
            if correct_bx and correct_by:
                st.success("Perfect! You've found all reaction forces.")
                st.session_state.current_step_idx = 7
                st.rerun()
            else:
                if not correct_bx:
                    st.warning("Check $B_x$: Are there any horizontal external forces acting on the beam?")
                if not correct_by:
                    st.warning(f"Check $B_y$: Total downward force is 27 kips ($15+6+6$). Since $A_y = 6$, what must $B_y$ be to reach 27?")

# ======================================================
# S — SANITY CHECK (Step 7)
# ======================================================
if st.session_state.current_step_idx >= 7:
    st.divider()
    st.header("S — Sanity Check")
    st.balloons()
    st.success("Final Results: Ay = 6k, By = 21k, Bx = 0k")
    st.info("Intuition Check: Does it make sense that By is much larger than Ay? Yes, because most of the weight (the two 6k loads) is hanging off the right side near B.")
    if st.button("Restart Exercise"):
        st.session_state.clear()
        st.rerun()