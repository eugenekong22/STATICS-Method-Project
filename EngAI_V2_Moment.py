import streamlit as st
from io import BytesIO
from PIL import Image
import math
import re
import time
from datetime import timedelta

# Try to import drawable canvas
try:
    from streamlit_drawable_canvas import st_canvas
    _canvas_ok = True
except ImportError:
    _canvas_ok = False

st.set_page_config(page_title="STATICS Method — Moments", page_icon="🔧", layout="centered")

# ----------------------------
# PROBLEM DEFINITION
# ----------------------------
PROBLEM_TEXT = (
    "A lever OA has a length of L = 24 inches. It is attached to a pivot shaft at O. "
    "The lever makes an angle of 60° with the horizontal ground. "
    "A vertical force F_v = 100 lb is applied at the end of the lever (point A), acting downwards. "
    "1) Determine the moment of the 100 lb force about point O. "
    "2) Determine the magnitude of a horizontal force applied at A that creates the same moment about O."
)

st.title("Moment of a Force Exercise")
st.write(PROBLEM_TEXT)

st.divider()
st.header("STATICS Method")

# ----------------------------
# KEYWORDS & DEFINITIONS
# ----------------------------
KEY_DEFS = {
    "moment": "The tendency of a force to rotate a body about a specific point or axis. Calculated as Force × Perpendicular Distance (M = Fd).",
    "moment arm": "The perpendicular distance from the pivot point (O) to the line of action of the force.",
    "line of action": "The infinite line extending along the direction of the force vector.",
    "pivot": "The point of rotation (O) which is fixed.",
    "vertical force": "A force acting perpendicular to the horizon (along the y-axis).",
    "horizontal force": "A force acting parallel to the horizon (along the x-axis).",
    "equilibrium": "A state where moments and forces balance (though here we are just calculating the moment, not necessarily balancing it).",
}

# Scan for terms
TERMS_IN_PROBLEM = [k for k in KEY_DEFS if re.search(rf"\b{re.escape(k)}\b", PROBLEM_TEXT, re.IGNORECASE)]
CORE_TERMS = {"moment", "vertical force"} 

# ----------------------------
# SESSION STATE INIT
# ----------------------------
def init_state():
    defaults = {
        "method_started": False,
        # S - Timer
        "s_timer_started": False,
        "s_timer_start_time": None,
        "s_timer_done": False,
        # S - Vocab
        "s_vocab_ack": {t: False for t in TERMS_IN_PROBLEM},
        # S - Identifier
        "s_given_sel": set(),
        "s_target_sel": set(),
        "s_identifier_pass": False,
        "S_done": False,
        # T - Translate
        "unlock_T": False,
        "T_done": False,
        # A - Assign
        "unlock_A": False,
        "A_done": False,
        # I - Implement
        "unlock_I": False,
        "I_done": False,
        # C - Compute
        "unlock_C": False,
        "C_done": False,
        # Sanity
        "unlock_S": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
STUDY_SECONDS = 3 * 60  # 3 minutes

def seconds_left():
    if not st.session_state.s_timer_started or st.session_state.s_timer_start_time is None:
        return STUDY_SECONDS
    return max(0, STUDY_SECONDS - int(time.time() - st.session_state.s_timer_start_time))

# ----------------------------
# CONTROLS
# ----------------------------
c_start, c_reset = st.columns([1, 1])
with c_start:
    if not st.session_state.method_started:
        if st.button("▶️ Start STATICS Method"):
            st.session_state.method_started = True
            st.session_state.s_timer_started = True
            st.session_state.s_timer_start_time = time.time()
            st.rerun()
with c_reset:
    if st.button("🔄 Reset All"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        init_state()
        st.rerun()

if not st.session_state.method_started:
    st.info("Click **Start STATICS Method** to begin Step S — Study.")
    st.stop()

# ======================================================
# S — STUDY (Substep 1): Focus timer
# ======================================================
st.subheader("S — Study (1/3): 3-minute quiet focus")
if not st.session_state.s_timer_done:
    left = seconds_left()
    if st.session_state.s_timer_started:
        pct = (STUDY_SECONDS - left) / STUDY_SECONDS
        st.progress(min(max(pct, 0.0), 1.0))
        mmss = str(timedelta(seconds=left))[2:7] if left >= 60 else f"00:{left:02d}"
        st.info(f"⏳ Read carefully. Visualize the lever angle and where the force acts. — {mmss} remaining")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("⏭️ I'm done early"):
                st.session_state.s_timer_done = True
                st.rerun()
        with c2:
            if st.button("⏸️ Pause"):
                st.session_state.s_timer_started = False
                st.rerun()

        if left > 0 and st.session_state.s_timer_started:
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.s_timer_done = True
            st.rerun()
    else:
        st.warning("Timer paused. Click **Start STATICS Method** again to resume.")
    st.stop()

st.success("✅ Focus timer complete.")

# ======================================================
# S — STUDY (Substep 2): Vocabulary
# ======================================================
st.subheader("S — Study (2/3): Vocabulary flash cards")
st.caption("Click each card to reveal the definition. Tick **I understand**.")

if not TERMS_IN_PROBLEM:
    st.info("No specific vocabulary detected.")
else:
    cols = st.columns(min(3, max(1, len(TERMS_IN_PROBLEM))))
    for i, term in enumerate(TERMS_IN_PROBLEM):
        with cols[i % len(cols)]:
            with st.expander(term.title(), expanded=False):
                st.write(KEY_DEFS[term])
            st.session_state.s_vocab_ack[term] = st.checkbox(
                f"I understand **{term}**",
                value=st.session_state.s_vocab_ack.get(term, False),
                key=f"ack_{term}"
            )

core_ok = all(st.session_state.s_vocab_ack.get(t, False) for t in CORE_TERMS if t in st.session_state.s_vocab_ack)
if not core_ok:
    st.warning(f"Please acknowledge core terms: {', '.join(CORE_TERMS)}")
    st.stop()

st.success("✅ Core vocabulary acknowledged.")

# ======================================================
# S — STUDY (Substep 3): Identifier
# ======================================================
st.subheader("S — Study (3/3): Identify Givens & Target")
st.caption("Select all that apply. Then click **Check**.")

GIVEN_ITEMS = [
    ("Force magnitude = 100 lb", True),
    ("Lever Length L = 24 inches", True),
    ("Shaft angle θ = 60° with ground", True),
    ("Force is vertical (down)", True),
    ("Lever is horizontal", False), # distractor
    ("Force is perpendicular to the lever", False), # distractor
]

TARGET_ITEMS = [
    ("Find Moment about O (M_O)", True),
    ("Find equivalent Horizontal Force at A", True),
    ("Find the reaction forces at the pivot", False), # distractor
    ("Find the angular velocity", False), # distractor
]

st.markdown("#### Givens")
cols_g = st.columns(2)
for i, (label, _) in enumerate(GIVEN_ITEMS):
    with cols_g[i % 2]:
        if st.checkbox(label, value=(label in st.session_state.s_given_sel), key=f"given_{i}"):
            st.session_state.s_given_sel.add(label)
        else:
            st.session_state.s_given_sel.discard(label)

st.markdown("#### Target")
cols_t = st.columns(2)
for j, (label, _) in enumerate(TARGET_ITEMS):
    with cols_t[j % 2]:
        if st.checkbox(label, value=(label in st.session_state.s_target_sel), key=f"target_{j}"):
            st.session_state.s_target_sel.add(label)
        else:
            st.session_state.s_target_sel.discard(label)

def grade_mcq(selected, items):
    truth = {l: t for l, t in items}
    correct = sum(1 for l in selected if truth.get(l, False))
    wrong = sum(1 for l in selected if not truth.get(l, False))
    total_true = sum(truth.values())
    return (correct == total_true and wrong == 0), correct, wrong, total_true

if st.button("✅ Check Identifiers"):
    g_ok, g_h, g_fp, g_tot = grade_mcq(st.session_state.s_given_sel, GIVEN_ITEMS)
    t_ok, t_h, t_fp, t_tot = grade_mcq(st.session_state.s_target_sel, TARGET_ITEMS)

    if g_ok: st.success(f"Givens correct ({g_h}/{g_tot})")
    else: st.warning(f"Givens: {g_h}/{g_tot} correct, {g_fp} wrong.")
    
    if t_ok: st.success(f"Targets correct ({t_h}/{t_tot})")
    else: st.warning(f"Targets: {t_h}/{t_tot} correct, {t_fp} wrong.")

    if g_ok and t_ok:
        st.session_state.S_done = True
        st.session_state.unlock_T = True
        st.rerun()

if not st.session_state.S_done:
    st.stop()

# ======================================================
# T — TRANSLATE: Diagram
# ======================================================
if st.session_state.unlock_T:
    st.header("T — Translate: Diagram the System")
    
    st.markdown("Draw the **Lever OA** on the canvas below at approximately 60°.")
    
    if not _canvas_ok:
        st.warning("Canvas library missing. Please visualize the lever at 60°.")
        st.session_state.T_done = True # skip
        st.session_state.unlock_A = True
    else:
        st.caption("Draw a single line representing the lever OA starting from the left side.")
        
        canvas_T = st_canvas(
            fill_color="rgba(0,0,0,0)", stroke_width=3, stroke_color="#111",
            background_color="#fff", height=300, width=600, drawing_mode="line", key="T_canvas"
        )
        
        # Analyze lines
        objs = (canvas_T.json_data or {}).get("objects", [])
        lines = [o for o in objs if o["type"] == "line"]
        
        if st.button("✅ Check Diagram"):
            if not lines:
                st.error("Please draw the lever.")
            else:
                valid_line = False
                for l in lines:
                    dx = l["x2"] - l["x1"]
                    dy = l["y2"] - l["y1"]
                    # canvas y is inverted (down is positive)
                    # 60 deg up means dy is negative
                    ang = math.degrees(math.atan2(-dy, dx))
                    if ang < 0: ang += 360
                    if 45 <= ang <= 75:
                        valid_line = True
                        break
                
                if valid_line:
                    st.success("Diagram looks good! You drew the lever at the correct approximate angle.")
                    st.session_state.T_done = True
                    st.session_state.unlock_A = True
                    st.rerun()
                else:
                    st.warning("The angle doesn't look like 60°. Remember 60° is steeper than 45°. (Draw from O to A).")

    if not st.session_state.T_done:
        st.stop()

# ======================================================
# A — ASSIGN: Conventions
# ======================================================
if st.session_state.unlock_A:
    st.header("A — Assign: Sign Conventions")
    
    st.markdown("Define your coordinate system and moment signs.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.radio("Coordinate System:", ["Standard (x Right, y Up)"], index=0, disabled=True)
    with c2:
        moment_sign = st.radio(
            "Moment Sign Convention:",
            ["Counter-Clockwise (CCW) is Positive (+)", "Clockwise (CW) is Positive (+)"],
            key="moment_convention"
        )
    
    st.info("Typically, **CCW is Positive (+)** is the standard scientific convention.")
    
    if st.button("💾 Save & Continue"):
        st.session_state.A_done = True
        st.session_state.unlock_I = True
        st.rerun()

    if not st.session_state.A_done:
        st.stop()

# ======================================================
# I — IMPLEMENT: Geometry & Equations
# ======================================================
if st.session_state.unlock_I:
    st.header("I — Implement: Geometry & Equations")

    # --- MATH REFRESHER START ---
    with st.expander("📘 Math Refresher: Visualizing the Triangle"):
        st.markdown(r"""
        **SOH CAH TOA** is your best friend here.
        
        Imagine the lever $L$ is the **Hypotenuse** of a right triangle.
        
        * **Horizontal Distance ($d_x$):** This is the "shadow" of the lever on the ground. It is **Adjacent** to the $60^\circ$ angle.
            * $\text{Adjacent} = \text{Hypotenuse} \cdot \cos(\theta)$
        * **Vertical Distance ($d_y$):** This is the height of the tip A. It is **Opposite** to the $60^\circ$ angle.
            * $\text{Opposite} = \text{Hypotenuse} \cdot \sin(\theta)$
        * Youtube Vidoe: https://www.youtube.com/watch?v=gSGbYOzjynk
        """)
        # Triggering a relevant diagram for SOH CAH TOA
        st.write("")
    # --- MATH REFRESHER END ---
    

    st.markdown(
        "To calculate Moment remember $M_O = F * d$ "
    )
    
    L = 24.0
    theta = 60.0
    
    # Calculate True Values for checking
    rx_true = L * math.cos(math.radians(theta)) # 12
    ry_true = L * math.sin(math.radians(theta)) # 20.78
    
    st.markdown("#### 1. Geometry Calculation")
    st.caption(f"Resolve the position of A relative to O (where L={L}, θ={theta}°).")
    
    c1, c2 = st.columns(2)
    with c1:
        rx_in = st.number_input("Horizontal distance ($d_x$):", min_value=0.0, step=0.1)
    with c2:
        ry_in = st.number_input("Vertical distance ($d_y$):", min_value=0.0, step=0.1)
        
    st.markdown("#### 2. Equation Setup")
    eq_type = st.radio("Select the correct Moment equation for the **vertical** force F_v:", 
                       [
                           "M = F_v * (Vertical Distance)", 
                           "M = F_v * (Horizontal Distance)", 
                           "M = F_v * L"
                       ])
    
    # --- HINT START ---
    with st.expander("📘 Hint: The 'Line of Action' Rule"):
        st.info("Key Concept: The Moment Arm must be PERPENDICULAR to the Force.")
        
        st.markdown("""
        1.  **Draw the Line of Action:** Imagine an infinite line passing through the force vector.
            * Since $F_v$ is **Vertical**, its line of action is a vertical line.
        2.  **Find the Distance:** Measure the shortest distance from the pivot $O$ to that infinite line.
            * To reach a vertical line from the pivot, you must measure **Horizontally**.
        
        Therefore: For a **Vertical** force, use the **Horizontal** distance.
        * Youtube Vidoe: https://www.youtube.com/watch?v=rtHW-YRDozE
        """)
        # Visualizing the moment arm concept
        st.write("")
    # --- HINT END ---

    if st.button("✅ Check Implementation"):
        # Check Geometry
        ok_x = abs(rx_in - rx_true) < 1.0
        ok_y = abs(ry_in - ry_true) < 1.0
        
        # Check Equation Logic (Vertical force needs Horizontal moment arm)
        ok_eq = "Horizontal Distance" in eq_type
        
        if ok_x and ok_y and ok_eq:
            st.success("Geometry and Logic are correct!")
            st.session_state.I_done = True
            st.session_state.unlock_C = True
            st.session_state.rx_val = rx_in
            st.session_state.ry_val = ry_in
            st.rerun()
        else:
            msg = ""
            if not ok_x: msg += f"Check horizontal distance ($d_x = L \\cos\\theta$). "
            if not ok_y: msg += f"Check vertical distance ($d_y = L \\sin\\theta$). "
            if not ok_eq: msg += "For a VERTICAL force, the line of action is vertical. The perpendicular distance to it is HORIZONTAL."
            st.warning(msg)

    if not st.session_state.I_done:
        st.stop()

# ======================================================
# C — COMPUTE
# ======================================================
if st.session_state.unlock_C:
    st.header("C — Compute")
    
    rx = st.session_state.rx_val
    ry = st.session_state.ry_val
    Fv = 100.0
    M_mag_true = Fv * rx
    
    st.subheader("Part 1: Moment of the Vertical Force")
    
    c1, c2 = st.columns(2)
    with c1:
        M_user = st.number_input("Magnitude of Moment (lb-in):", min_value=0.0, step=10.0)
    with c2:
        M_dir = st.selectbox("Direction of Moment:", ["Select...", "Clockwise (CW)", "Counter-Clockwise (CCW)"])

    # --- HINT START ---
    with st.expander("📘 Hint: The 'Pin' Technique"):
        st.markdown("""
        **Visualize it physically:**
        1.  Imagine sticking a **pin** through point $O$ so it can't move.
        2.  Tie a string to point $A$ and pull it **down** (direction of the 100 lb force).
        3.  Which way does the lever rotate?
        
        * Does it turn like the hands of a clock? (**CW**)
        * Or against them? (**CCW**)
        * Youtube Vidoe: https://www.youtube.com/watch?v=fuTVnSFBhwk
                    
        """)
        # Triggering a diagram for rotation direction
        st.write("")
    # --- HINT END ---

        
    st.subheader("Part 2: Equivalent Horizontal Force")
    st.markdown(
        "Find the magnitude of a **horizontal** force at A that produces this **same** moment magnitude."
    )
    
    # --- HINT START ---
    with st.expander("📘 Hint: Sliding the Force"):
        st.markdown(r"""
        We want the **same rotation** (Moment), but using a different push.
        
        $$M_{target} = F_{new} \cdot d_{\perp}$$
        
        * **New Force:** Horizontal ($F_h$).
        * **New Line of Action:** Horizontal line through A.
        * **New Moment Arm:** The perpendicular distance from $O$ to a *horizontal* line is the **Vertical Height** ($d_y$).
        
        *Equation:* $$F_h = \frac{\text{Moment calculated in Part 1}}{d_y}$$
        """) 
        st.write("")
    # --- HINT END ---
    
    Fh_user = st.number_input("Magnitude of Horizontal Force (lb):", min_value=0.0, step=1.0)
    
    if st.button("✅ Verify Results"):
        # Check Moment
        ok_M_mag = abs(M_user - M_mag_true) < (M_mag_true * 0.05) # 5% tol
        ok_M_dir = M_dir == "Clockwise (CW)" 
        
        # Check Force H
        if ry > 0:
            Fh_true = M_mag_true / ry 
            ok_Fh = abs(Fh_user - Fh_true) < (Fh_true * 0.05)
        else:
            ok_Fh = False
            
        if ok_M_mag and ok_M_dir and ok_Fh:
            st.success("🎉 Calculations Correct! Part 1 and 2 are solved.")
            st.session_state.C_done = True
            st.session_state.unlock_S = True
            st.session_state.final_M = M_user
            st.session_state.final_Fh = Fh_user
            st.rerun()
        else:
            if not ok_M_mag: st.warning(f"Moment Magnitude incorrect. Check $100 \\times {rx:.1f}$.")
            if not ok_M_dir: st.warning("Check rotation direction. Visualize the clock hand.")
            if not ok_Fh: st.warning(f"Horizontal force incorrect. Did you divide Moment by the vertical distance ($d_y$)?")

    if not st.session_state.C_done:
        st.stop()

# ======================================================
# S — SANITY CHECK
# ======================================================
if st.session_state.unlock_S:
    st.header("S — Sanity Check")
    
    M_res = st.session_state.final_M
    Fh_res = st.session_state.final_Fh
    
    st.markdown("### Intuition Check")
    
    st.write(f"**Your Moment:** {M_res:.1f} lb-in")
    st.write(f"**Your Horizontal Force:** {Fh_res:.1f} lb")
    
    st.info("Logic Check: The vertical arm (height) is larger than the horizontal arm (width) because 60° is steep.")
    
    check1 = st.checkbox("Since the Moment Arm for the Horizontal Force (Height) is LARGER than the Moment Arm for the Vertical Force (Width), the Horizontal Force required should be SMALLER than 100 lb.")
    
    if check1:
        if Fh_res < 100:
            st.success("✅ Correct! 57.7 lb < 100 lb. Physics holds up.")
            st.balloons()
        else:
            st.error("Wait... your result is > 100 lb but your logic says it should be smaller. Check math!")