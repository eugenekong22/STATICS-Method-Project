import streamlit as st
from io import BytesIO
from PIL import Image
import math
import re
import time
from datetime import timedelta

st.set_page_config(page_title="STATICS Method — Study", page_icon="🧱", layout="centered")

# ----------------------------
# PROBLEM (outside of STATICS method)
# ----------------------------
PROBLEM_TEXT = (
    "A smooth ring is located at point O. Two cables, OA and OB, are attached to the ring and pull on it so that the ring reamins in equilibrium."
    "Cable OA exerts a force F1 = 400N directed 30° above the positive x-axis."
    "Cable OB exerts a force F2 = 250N directed 135° counterclockwise from the positive x-axis."
    "A third force F3 is applied to the ring so that system remains equilibrium."
    "Using a force triangle method, determine the magnitude and direction of F3."
)

st.title("Force Triangle Excercise")
st.write(PROBLEM_TEXT)

st.divider()
st.header("STATICS Method")

# ----------------------------
# KEYWORDS & DEFINITIONS
# ----------------------------
KEY_DEFS = {
    "equilibrium": "The pulls and pushes on the ring balance each other so that the ring stays still (it doesn’t start moving or rotating).",
    "force triangle": "A way to show three forces that keep an object still by drawing them head-to-tail so they form a closed triangle. The last side that closes the triangle represents the third force needed to balance the other two.",
    "head-to-tail": "Place tail of one vector at head of previous; closing side gives the resultant/opposite.",
    "smooth ring": "Idealized contact with negligible friction; cable forces pass through the ring center.",
    "cable": "Tension-only member; force acts along the cable, away from the body.",
    "magnitude": "Size/length of a vector (e.g., newtons).",
    "direction": "Orientation/angle of a vector (e.g., degrees CCW from +x).",
}
# Only show terms actually present in the problem (simple scan)
TERMS_IN_PROBLEM = [k for k in KEY_DEFS if re.search(rf"\b{re.escape(k)}\b", PROBLEM_TEXT, re.IGNORECASE)]
CORE_TERMS = {"equilibrium", "force triangle"}  # must be acknowledged by student

# Expected patterns for pass/fail checking (lightweight, forgiving)
GIVEN_PATTERNS = {
    "F1 magnitude": r"f1[^0-9]*400\s*?n",
    "F1 direction": r"30\s*°|\b30\s*deg|\b30\s*degrees",
    "F2 magnitude": r"f2[^0-9]*250\s*?n",
    "F2 direction": r"135\s*°|\b135\s*deg|\b135\s*degrees",
    "equilibrium": r"\bequilibrium\b",
    # helpful but optional: smooth ring
}
TARGET_PATTERNS = {
    "F3 magnitude": r"f3.*(magnitude|find|compute|solve)",
    "F3 direction": r"f3.*(direction|angle|theta|θ)",
    # helpful but optional: ΣF = 0 / closes triangle
}

# ----------------------------
# SESSION STATE
# ----------------------------
def init_state():
    defaults = {
        "method_started": False,
        # Study substep 1 (timer)
        "s_timer_started": False,
        "s_timer_start_time": None,
        "s_timer_done": False,
        # Study substep 2 (vocab)
        "s_vocab_ack": {t: False for t in TERMS_IN_PROBLEM},  # “I understand” ticks
        # Study substep 3 (identifier)
        "givens_text": "",
        "target_text": "",
        "s_identifier_pass": False,
        # Overall S completion & unlock for T
        "S_done": False,
        "unlock_T": False,
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
# Start/Reset Controls
# ----------------------------
c_start, c_reset = st.columns([1, 1])
with c_start:
    if not st.session_state.method_started:
        if st.button("▶️ Start STATICS Method"):
            st.session_state.method_started = True
            # Gate to S substep 1 (timer)
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
# S — STUDY (Substep 1): Focus timer (only this visible)
# ======================================================
st.subheader("S — Study (1/3): 3-minute quiet focus")
if not st.session_state.s_timer_done:
    left = seconds_left()
    if st.session_state.s_timer_started:
        pct = (STUDY_SECONDS - left) / STUDY_SECONDS
        st.progress(min(max(pct, 0.0), 1.0))
        mmss = str(timedelta(seconds=left))[2:7] if left >= 60 else f"00:{left:02d}"
        st.info(f"⏳ Read carefully and understand the keywords and problem. — {mmss} remaining")
        st.caption("Visualize the ring at O and visualize the direction of F3 for the ring to be in equilibrium.")
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
            # time up
            st.session_state.s_timer_done = True
            st.rerun()
    else:
        st.warning("Timer paused. Click **Start STATICS Method** again to resume.")
    st.stop()  # do not reveal later substeps yet

st.success("✅ Focus timer complete.")

# ======================================================
# S — STUDY (Substep 2): Vocabulary flash cards
# ======================================================
st.subheader("S — Study (2/3): Vocabulary flash cards")
st.caption("Click each card to reveal the definition. Tick **I understand** when you’re comfortable with the term.")

if not TERMS_IN_PROBLEM:
    st.info("No specific vocabulary detected for this problem.")
else:
    cols = st.columns(min(3, max(1, len(TERMS_IN_PROBLEM))))
    for i, term in enumerate(TERMS_IN_PROBLEM):
        with cols[i % len(cols)]:
            # simple “card” using an expander
            with st.expander(term.title(), expanded=False):
                st.write(KEY_DEFS[term])

            # student acknowledgement
            st.session_state.s_vocab_ack[term] = st.checkbox(
                f"I understand **{term}**",
                value=st.session_state.s_vocab_ack.get(term, False),
                key=f"ack_{term}"
            )

# Require core vocab acknowledged
core_ok = all(st.session_state.s_vocab_ack.get(t, False) for t in CORE_TERMS if t in st.session_state.s_vocab_ack)

# Only allow proceeding if core terms acknowledged
if not core_ok:
    missing = [t for t in CORE_TERMS if not st.session_state.s_vocab_ack.get(t, False)]
    st.warning(f"Please acknowledge the core terms: {', '.join(missing)}")
    st.stop()

st.success("✅ Core vocabulary acknowledged.")

# ======================================================
# S — STUDY (Substep 3): Identifier (Multiple Choice)
# ======================================================
st.subheader("S — Study (3/3): Identify Givens & Target")
st.caption("Select all that apply. Then click **Check**.")

# --- Multiple-choice banks ---
GIVEN_ITEMS = [
    ("F₁ = 400 N", True),
    ("F₁ direction = 30° above +x", True),
    ("F₂ = 250 N", True),
    ("F₂ direction = 135° from +x", True),
    ("System is in equilibrium", True),
    ("Smooth ring (no frictional resistance at ring contact)", True),
    # plausible distractors:
    ("Mass of the ring is given", False),
    ("Coefficient of friction is given", False),
    ("Moment about O is specified", False),
    ("A distributed load is acting", False),
]

TARGET_ITEMS = [
    ("Find |F₃| (magnitude)", True),
    ("Find direction (angle) of F₃", True),
    # distractors:
    ("Find the position of point O", False),
    ("Find the mass of the ring", False),
    ("Find the tension of an additional third cable (given)", False),
]

# --- Session state for selections ---
if "s_given_sel" not in st.session_state:
    st.session_state.s_given_sel = set()
if "s_target_sel" not in st.session_state:
    st.session_state.s_target_sel = set()

# --- Render checklists ---
st.markdown("#### Givens — select all statements that are provided in the problem")
cols_g = st.columns(2)
for i, (label, _) in enumerate(GIVEN_ITEMS):
    with cols_g[i % 2]:
        checked = st.checkbox(label, value=(label in st.session_state.s_given_sel), key=f"given_{i}")
        if checked:
            st.session_state.s_given_sel.add(label)
        else:
            st.session_state.s_given_sel.discard(label)

st.markdown("#### Target — select what we are asked to determine")
cols_t = st.columns(2)
for j, (label, _) in enumerate(TARGET_ITEMS):
    with cols_t[j % 2]:
        checked = st.checkbox(label, value=(label in st.session_state.s_target_sel), key=f"target_{j}")
        if checked:
            st.session_state.s_target_sel.add(label)
        else:
            st.session_state.s_target_sel.discard(label)

# --- Grade selections (no model answers shown beforehand) ---
def grade_mcq(selected_labels: set, items: list[tuple[str, bool]]):
    """Returns (all_correct: bool, num_correct_picked: int, num_false_picked: int, total_true: int)."""
    truth = {label: is_true for label, is_true in items}
    num_true_total = sum(truth.values())
    num_correct_picked = sum(1 for lab in selected_labels if truth.get(lab, False))
    num_false_picked = sum(1 for lab in selected_labels if truth.get(lab, False) is False)
    # all-correct means: picked every true item and picked no false items
    all_correct = (num_correct_picked == num_true_total) and (num_false_picked == 0)
    return all_correct, num_correct_picked, num_false_picked, num_true_total

c_chk, c_clear = st.columns([1, 1])
with c_chk:
    if st.button("✅ Check"):
        g_ok, g_hit, g_fp, g_total = grade_mcq(st.session_state.s_given_sel, GIVEN_ITEMS)
        t_ok, t_hit, t_fp, t_total = grade_mcq(st.session_state.s_target_sel, TARGET_ITEMS)

        # Feedback without revealing which specific ones were missed
        st.markdown("**Givens:**")
        if g_ok:
            st.success(f"All correct ✓  (selected {g_hit}/{g_total} correct; 0 incorrect)")
        else:
            st.warning(f"Not quite. You selected {g_hit}/{g_total} correct and {g_fp} incorrect. Adjust your choices and try again.")

        st.markdown("**Target:**")
        if t_ok:
            st.success(f"All correct ✓  (selected {t_hit}/{t_total} correct; 0 incorrect)")
        else:
            st.warning(f"Not quite. You selected {t_hit}/{t_total} correct and {t_fp} incorrect. Adjust your choices and try again.")

        st.session_state.s_identifier_pass = bool(g_ok and t_ok)
        if st.session_state.s_identifier_pass:
            st.session_state.S_done = True
            st.session_state.unlock_T = True
            st.success("🎉 Step S (Study) complete. The **Translate (T)** section is now unlocked.")
            st.rerun()
        else:
            st.info("Make corrections and re-check.")

with c_clear:
    if st.button("🗑️ Clear selections"):
        st.session_state.s_given_sel = set()
        st.session_state.s_target_sel = set()
        st.session_state.s_identifier_pass = False
        st.rerun()


# Try to import drawable canvas (assuming this is done at the top of your actual script)
try:
    from streamlit_drawable_canvas import st_canvas
    _canvas_ok = True
except ImportError:
    # Handle the case where the user hasn't installed the library
    _canvas_ok = False
except Exception:
    _canvas_ok = False


# ===============================
# T — TRANSLATE: Diagram / FBD
# ===============================

# --- Define angle diff helper ---
def ang_diff(a, b):
    d = (a - b + 180) % 360 - 180
    return abs(d)

# --- Define line extraction helper ---
def extract_lines(canvas_json):
    objs = (canvas_json or {}).get("objects", [])
    lines = []
    for obj in objs:
        if obj.get("type") == "line":
            x1, y1 = obj["x1"], obj["y1"]
            x2, y2 = obj["x2"], obj["y2"]
            dx, dy_canvas = x2 - x1, y2 - y1
            ang = math.degrees(math.atan2(-dy_canvas, dx))  
            if ang <= -180: ang += 360
            if ang > 180: ang -= 360
            L = math.hypot(dx, dy_canvas)
            lines.append({"p1": (x1, y1), "p2": (x2, y2),
                          "angle": ang, "length": L})
    return lines


# --- Main Section ---
if st.session_state.get("unlock_T", False):
    st.header("T — Translate: Draw a Force Triangle")

    # Given forces
    F1 = 400.0
    th1 = 30.0
    F2 = 250.0
    th2 = 135.0

    th1r = math.radians(th1)
    th2r = math.radians(th2)
    F1x, F1y = F1*math.cos(th1r), F1*math.sin(th1r)
    F2x, F2y = F2*math.cos(th2r), F2*math.sin(th2r)
    Sx, Sy = F1x + F2x, F1y + F2y
    F3x, F3y = -Sx, -Sy
    th3 = math.degrees(math.atan2(F3y, F3x))

    st.markdown(
        "Please **draw your Force Triangle** on the canvas below. "
        "FBDs and picture uploads are disabled for now — we will use them later."
    )

    # 🔒 FBD and Upload disabled (but preserved in code)
    # mode = st.radio("Choose diagram type:", ["Force Triangle"])
    mode = "Force Triangle"

    # 🔒 Uploaded image handling disabled — kept for future use
    uploaded = None

    # --- Drawing canvas only ---
    if not _canvas_ok:
        st.warning("Install drawing tool: `pip install streamlit-drawable-canvas`")
    else:
        st.caption("Draw **lines** for F1, F2, and F3.")
        c1, c2, c3 = st.columns(3)
        with c1:
            stroke_w = st.slider("Line width", 2, 10, 3)
        with c2:
            height = st.slider("Canvas height", 280, 520, 340, step=20)
        with c3:
            tol_angle = st.slider("Angle tolerance (°)", 5, 30, 12)

        canvas = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=stroke_w,
            stroke_color="#111111",
            background_color="#ffffff",
            height=height,
            width=700,
            drawing_mode="line",
            key="translate_canvas"
        )

    # Labeling
    lines = extract_lines(canvas.json_data)
    line_names = [f"Line {i+1} (angle≈{l['angle']:.1f}°, len≈{l['length']:.0f}px)"
                  for i,l in enumerate(lines)]
    idx_opts = list(range(len(lines)))

    colL1, colL2, colL3 = st.columns(3)
    with colL1:
        f1_sel = st.selectbox("Select F1", [None]+idx_opts,
                              format_func=lambda i: "None" if i is None else line_names[i])
    with colL2:
        f2_sel = st.selectbox("Select F2", [None]+idx_opts,
                              format_func=lambda i: "None" if i is None else line_names[i])
    with colL3:
        f3_sel = st.selectbox("Select F3", [None]+idx_opts,
                              format_func=lambda i: "None" if i is None else line_names[i])

    # Magnitude ratio check
    st.markdown("### Optional scaling check")
    st.caption("Check if |F1|:|F2| ≈ 400:250")
    colS1, colS2 = st.columns(2)
    with colS1:
        ratio_tol_pct = st.slider("Length ratio tolerance (%)", 5, 40, 20)
    with colS2:
        require_f3 = st.checkbox("Require F3", value=True)

    # ------------------------------
    # 📘 Refresher before check
    # ------------------------------
    st.markdown("#### 📘 Optional Refresher")
    with st.expander("Vector refresher"):
        st.markdown(
            "- Draw F1, then attach F2 head-to-tail.\n"
            "- F3 closes the triangle so the forces balance.\n"
            "- Directions measured CCW from +x-axis.\n"
            "- Force Triangle (Youtube)](https://www.youtube.com/watch?v=ntgahbh_GI4) \n"
        )

    # ------------------------------
    # Diagram Check Button
    # ------------------------------
    passed = False

    if st.button("✅ Check my diagram"):
        if f1_sel is None or f2_sel is None:
            st.error("Please label **F1** and **F2**.")
        elif require_f3 and f3_sel is None:
            st.error("Please label **F3**.")
        else:
            ok_ang1 = ang_diff(lines[f1_sel]["angle"], th1) <= tol_angle
            ok_ang2 = ang_diff(lines[f2_sel]["angle"], th2) <= tol_angle

            msgs = [
                f"F1 angle vs {th1}° → {lines[f1_sel]['angle']:.1f}° : {'✅' if ok_ang1 else '❌'}",
                f"F2 angle vs {th2}° → {lines[f2_sel]['angle']:.1f}° : {'✅' if ok_ang2 else '❌'}",
            ]

            if require_f3:
                ok_ang3 = ang_diff(lines[f3_sel]["angle"], th3) <= tol_angle
                msgs.append(
                    f"F3 angle vs {th3:.1f}° → {lines[f3_sel]['angle']:.1f}° : {'✅' if ok_ang3 else '❌'}"
                )
            else:
                ok_ang3 = True

            st.markdown("### Checks")
            for m in msgs:
                st.write(m)

            # Magnitude ratio
            L1, L2 = lines[f1_sel]["length"], lines[f2_sel]["length"]
            if L1 > 0 and L2 > 0:
                drawn_ratio = L1 / L2
                true_ratio = F1 / F2
                pct_err = abs(drawn_ratio - true_ratio) / true_ratio * 100
                ok_ratio = pct_err <= ratio_tol_pct
                st.write(
                    f"Length ratio: drawn {drawn_ratio:.2f}, true {true_ratio:.2f}, err {pct_err:.1f}% → "
                    f"{'✅' if ok_ratio else '⚠️'}"
                )
            else:
                ok_ratio = True

            if ok_ang1 and ok_ang2 and ok_ang3 and ok_ratio:
                st.success("Diagram looks correct — proceeding!")
                passed = True
            else:
                st.warning("Some items need correction.")

    # Gate next section
    if "T_done" not in st.session_state:
        st.session_state["T_done"] = False

    if passed:
        st.session_state["T_done"] = True
        st.session_state["unlock_A"] = True
        st.success("🎉 **Translate (T)** complete! Next step unlocked.")
    else:
        st.info("Finish this step to continue.")



# ===============================
# A — ASSIGN: Axes & Assumed Directions
# ===============================
if st.session_state.get("unlock_A", False):
    st.header("A — Assign: Define your axes & assume directions")

    # Given forces from previous section
    F1 = 400.0
    th1 = 30.0
    F2 = 250.0
    th2 = 135.0

    # Compute expected F3 direction
    th1r = math.radians(th1)
    th2r = math.radians(th2)
    F1x, F1y = F1 * math.cos(th1r), F1 * math.sin(th1r)
    F2x, F2y = F2 * math.cos(th2r), F2 * math.sin(th2r)
    Sx, Sy = F1x + F2x, F1y + F2y
    F3x, F3y = -Sx, -Sy
    th3 = math.degrees(math.atan2(F3y, F3x))

    st.markdown(
        "In this step, you will **set up your coordinate system** and "
        "**assume the signs/directions** for unknown forces. "
        "If an assumption is wrong, the final answer will simply come out negative — and that’s OK!"
    )

    # --------------------------------
    # 1️⃣ Define axes orientation
    # --------------------------------
    st.subheader("1) Define your x–y axes")

    axis_mode_choice = st.radio(
        "Select coordinate system orientation:",
        ["Standard (x → right, y ↑ up)", "Rotate axes by β (CCW)"],
        horizontal=False,
        key="axis_mode_choice"
    )

    beta = 0.0
    if "Rotate" in axis_mode_choice:
        beta = st.number_input(
            "β = rotation of axes (degrees, CCW positive)",
            value=0.0, min_value=-180.0, max_value=180.0, step=1.0, key="beta_value"
        )

    # Compute angles relative to chosen axes
    th1_rel = (th1 - beta + 360) % 360
    th2_rel = (th2 - beta + 360) % 360
    th3_rel = (th3 - beta + 360) % 360

    colA1, colA2, colA3 = st.columns(3)
    with colA1:
        st.metric("θ₁ (from x-axis)", f"{th1_rel:.1f}°")
    with colA2:
        st.metric("θ₂ (from x-axis)", f"{th2_rel:.1f}°")
    with colA3:
        st.metric("θ₃ (from x-axis)", f"{th3_rel:.1f}°")

    st.caption("Tip: Choosing rotated axes can make one of the forces align with an axis for simpler equations.")

    # --------------------------------
    # 2️⃣ Assume unknown directions
    # --------------------------------
    st.subheader("2) Assume directions for unknown forces")

    st.markdown(
        "For this problem, the unknown is **F₃** (the closing equilibrium force). "
        "Assume the signs of its x and y components before writing equations."
    )

    colU1, colU2 = st.columns(2)
    with colU1:
        F3x_positive = st.toggle("Assume **F₃x** is positive (→)", value=True, key="F3x_assumption")
    with colU2:
        F3y_positive = st.toggle("Assume **F₃y** is positive (↑)", value=True, key="F3y_assumption")

    st.caption("If your assumption is wrong, your solution will just produce a negative component — that's part of learning!")

    # --------------------------------
    # 3️⃣ Save and unlock next section
    # --------------------------------
    st.divider()
    c1, c2 = st.columns([1, 1])
    with c1:
        save_btn = st.button("💾 Save Assign choices")
    with c2:
        finish_btn = st.button("✅ Finish A — continue to next step")

    # Pull the values from widgets
    axis_mode_val = st.session_state.get("axis_mode_choice", "Standard (x → right, y ↑ up)")
    beta_val = st.session_state.get("beta_value", 0.0)
    F3x_assume = st.session_state.get("F3x_assumption", True)
    F3y_assume = st.session_state.get("F3y_assumption", True)

    if save_btn or finish_btn:
        st.session_state["A_done"] = True
        # Save safe copies under new names (to avoid widget conflicts)
        st.session_state["A_axis_mode_saved"] = axis_mode_val
        st.session_state["A_beta_saved"] = beta_val
        st.session_state["A_F3x_assume_saved"] = F3x_assume
        st.session_state["A_F3y_assume_saved"] = F3y_assume

        # Unlock next section (example)
        st.session_state["unlock_C"] = True  # You can rename for next phase
        st.success("🎉 Step A (Assign) complete — your coordinate system and sign assumptions are saved!")

    if not st.session_state.get("A_done"):
        st.info("Set your axes and sign assumptions, then click **Finish A** to continue.")


# ===============================
# T — Translate forces to components (optional for force triangle)
# ===============================
if st.session_state.get("unlock_C", False):  # <-- this should be set when A (Assign) is finished
    st.header("T — Translate forces to components")

    # ---- Robust gates for this section ----
    if "T_components_done" not in st.session_state:
        st.session_state["T_components_done"] = False
    if "unlock_I" not in st.session_state:
        st.session_state["unlock_I"] = False

    st.info(
        "For **this force-triangle** problem, you can solve with pure geometry (head-to-tail). "
        "If you want practice, you can enter components below. "
        "**You’ll advance only by clicking Continue or by passing the component check.**"
    )

    # ----------- Givens / from previous steps -----------
    F1, th1 = 400.0, 30.0     # deg CCW from +x
    F2, th2 = 250.0, 135.0
    beta = st.session_state.get("A_beta_saved", 0.0)  # axis rotation (deg CCW)
    # Angles relative to chosen axes (rotate axes by +β -> subtract β)
    th1_rel = (th1 - beta + 360.0) % 360.0
    th2_rel = (th2 - beta + 360.0) % 360.0

    # Helpers
    def comp(F, theta_deg):
        t = math.radians(theta_deg)
        return F*math.cos(t), F*math.sin(t)  # (Fx, Fy)

    def fmt(x): 
        return f"{x:.2f}"

    # ---------- Path A: Skip components (always available) ----------
    st.success("You may **skip components** for this triangle problem and continue.")
    if st.button("➡️ Continue without components", key="T2_btn_continue_without_components"):
        st.session_state["T_components_done"] = True
        st.session_state["unlock_I"] = True      # ← unlock I ONLY here
        st.rerun()

    st.divider()

    # ---------- Path B: Optional practice (inside an expander) ----------
    with st.expander("Optional: Practice the component method", expanded=False):
        st.caption(f"Enter components relative to your chosen axes (β = {beta:.1f}° CCW).")

        # Truth for checking
        F1x_true, F1y_true = comp(F1, th1_rel)
        F2x_true, F2y_true = comp(F2, th2_rel)

        coltol = st.columns(1)
        with coltol[0]:
            abs_tol = st.number_input("Numerical tolerance (N)", min_value=0.0, value=1.0, step=0.5, key="T2_tol_abs")
        
        # Removed: show_hints checkbox

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**F₁ = 400 N @ {th1_rel:.1f}° (from your x-axis)**")
            F1x_user = st.number_input("F₁ₓ (N)", value=0.0, step=1.0, key="T2_input_F1x")
            F1y_user = st.number_input("F₁ᵧ (N)", value=0.0, step=1.0, key="T2_input_F1y")

        with c2:
            st.markdown(f"**F₂ = 250 N @ {th2_rel:.1f}° (from your x-axis)**")
            F2x_user = st.number_input("F₂ₓ (N)", value=0.0, step=1.0, key="T2_input_F2x")
            F2y_user = st.number_input("F₂ᵧ (N)", value=0.0, step=1.0, key="T2_input_F2y")

        def within(a, b, tol): 
            return abs(a - b) <= tol

        if st.button("✅ Check my components", key="T2_btn_check_components"):
            ok1x = within(F1x_user, F1x_true, abs_tol)
            ok1y = within(F1y_user, F1y_true, abs_tol)
            ok2x = within(F2x_user, F2x_true, abs_tol)
            ok2y = within(F2y_user, F2y_true, abs_tol)

            st.markdown("#### Results")
            st.write(f"F₁ₓ: entered {fmt(F1x_user)} → {'✅' if ok1x else '❌'} (Expected: {fmt(F1x_true)})")
            st.write(f"F₁ᵧ: entered {fmt(F1y_user)} → {'✅' if ok1y else '❌'} (Expected: {fmt(F1y_true)})")
            st.write(f"F₂ₓ: entered {fmt(F2x_user)} → {'✅' if ok2x else '❌'} (Expected: {fmt(F2x_true)})")
            st.write(f"F₂ᵧ: entered {fmt(F2y_user)} → {'✅' if ok2y else '❌'} (Expected: {fmt(F2y_true)})")

            all_ok = ok1x and ok1y and ok2x and ok2y
            if all_ok:
                st.success("Great—your components match the expected values.")
                st.session_state["T_components_done"] = True
                st.session_state["unlock_I"] = True   # ← unlock I ONLY here
                st.rerun()
            else:
                st.warning("Some components differ from the expected values. Adjust and check again.")

    # IMPORTANT FIX: Prevent later sections (like I) from rendering
    # unless T_components_done has been set by either the skip button or the check button.
    if not st.session_state.get("T_components_done"):
        st.stop() 

# I — IMPLEMENT section will now run if st.session_state.get("unlock_I", False) is True


# ===============================
# I — IMPLEMENT: Write equilibrium equations (placeholder)
# ===============================
if st.session_state.get("unlock_I", False):
    st.header("I — Implement: Write the equilibrium equations")

    st.info(
        "For this **three-force triangle** problem, detailed equations are not required "
        "because the geometry (force triangle) directly provides the solution.  \n\n"
        "For other Statics problems, you’ll apply the **conditions of equilibrium**:\n\n"
        r"- $\sum F_x = 0$  \n"
        r"- $\sum F_y = 0$  \n"
        r"- (Optional) $\sum M_O = 0$"
    )

    mode_I = st.radio(
        "How do you want to proceed?",
        [
            "Skip (triangle problem — solved by geometry)",
            "Practice writing equilibrium equations (for future problems)"
        ],
        key="I_mode_choice_radio"
    )

    # --- Skip option for triangle problems ---
    if mode_I.startswith("Skip"):
        if st.button("➡️ Continue (skip I for this triangle)", key="I_btn_skip_continue"):
            st.session_state["I_done"] = True
            st.session_state["unlock_C_next"] = True   # gate your next phase
            st.success("I — Implement skipped for triangle case. Next step unlocked.")
            st.rerun()
        # **REMOVED st.stop() HERE**
    # --- Practice mode (no numeric answers revealed) ---
    elif mode_I.startswith("Practice"):
        st.subheader("Practice: Record your equilibrium equations")

        beta_saved = st.session_state.get("A_beta_saved", 0.0)
        st.caption(f"Write equations **relative to your chosen axes** (β = {beta_saved:.1f}° CCW).")

        col_eq = st.columns(2)
        with col_eq[0]:
            fx_text = st.text_area("ΣFx = 0", height=90, key="I_text_fx",
                                   placeholder="Example: F1 cosθ1 + F2 cosθ2 + F3x = 0")
        with col_eq[1]:
            fy_text = st.text_area("ΣFy = 0", height=90, key="I_text_fy",
                                   placeholder="Example: F1 sinθ1 + F2 sinθ2 + F3y = 0")

        use_moments = st.checkbox("Include a moment equation (ΣM = 0)?", value=False, key="I_chk_use_moments")
        if use_moments:
            M_text = st.text_area("ΣM = 0", height=80, key="I_text_M",
                                  placeholder="Example: ∑(r×F) = 0 about point O")

        st.markdown("#### Self-check before continuing")
        c1, c2, c3 = st.columns(3)
        with c1: chk_signs    = st.checkbox("Signs match my axes", key="I_chk_signs_good")
        with c2: chk_forces   = st.checkbox("All forces included", key="I_chk_forces_all")
        with c3: chk_unknowns = st.checkbox("Unknowns are identifiable", key="I_chk_unknowns_id")

        if st.button("✅ Mark as complete", key="I_btn_mark_complete"):
            if (fx_text.strip() == "") or (fy_text.strip() == ""):
                st.warning("Please enter both ΣFx and ΣFy (or choose Skip above).")
            elif not (chk_signs and chk_forces and chk_unknowns):
                st.info("Check all three boxes to proceed.")
            else:
                st.session_state["I_done"] = True
                st.session_state["unlock_C_next"] = True
                st.success("🎉 Implement step completed. Next step unlocked.")
                st.rerun()
    
    # We only stop if the section is not yet completed, otherwise we fall through to C.
    if not st.session_state.get("I_done", False):
        st.stop()


# ===============================
# C — COMPUTE / CONCLUDE
# Start only after I is complete
# ===============================
if st.session_state.get("I_done", False) or st.session_state.get("unlock_C_next", False):
    st.header("C — Compute / Conclude")

    # --- givens (same as earlier) ---
    F1, th1 = 400.0, 30.0      # deg CCW from +x
    F2, th2 = 250.0, 135.0
    beta = st.session_state.get("A_beta_saved", 0.0)  # axis rotation (deg CCW, if you used it earlier)

    # ---------- helpers ----------
    def included_angle_deg(a, b):
        """Smallest included angle between directions a and b (deg)."""
        d = (a - b + 180) % 360 - 180
        return abs(d)

    def law_of_cosines(Fa, Fb, gamma_deg):
        g = math.radians(gamma_deg)
        return math.sqrt(Fa**2 + Fb**2 - 2*Fa*Fb*math.cos(g))

    def clamp01(x):  # for safe arcsin
        return max(-1.0, min(1.0, x))

    def fmt(x): return f"{x:.3f}"

    # expected geometry (used internally, but not revealed when wrong)
    d_tail = included_angle_deg(th1, th2)        # tail-to-tail angle between F1 and F2
    gamma_expected = 180.0 - d_tail              # interior angle in the force triangle

    # expected F3 from components (for reference / checks)
    th1r = math.radians(th1); th2r = math.radians(th2)
    F1x, F1y = F1*math.cos(th1r), F1*math.sin(th1r)
    F2x, F2y = F2*math.cos(th2r), F2*math.sin(th2r)
    Sx, Sy   = F1x + F2x, F1y + F2y
    F3x, F3y = -Sx, -Sy
    F3_true  = math.hypot(F3x, F3y)
    th3_true = math.degrees(math.atan2(F3y, F3x))  # this is in [-180, 180]

    # ---------- init C-state ----------
    if "C_gamma_ok" not in st.session_state: st.session_state["C_gamma_ok"] = False
    if "C_F3_ok"    not in st.session_state: st.session_state["C_F3_ok"]    = False
    if "C_dir_ok"   not in st.session_state: st.session_state["C_dir_ok"]   = False
    if "C_done"     not in st.session_state: st.session_state["C_done"]     = False
    if "C_gamma_val" not in st.session_state: st.session_state["C_gamma_val"] = gamma_expected
    if "C_F3_val"    not in st.session_state: st.session_state["C_F3_val"]    = F3_true

    # ============================
    # C1 — Find included angle γ
    # ============================
    st.subheader("C1 — Angle between Line 1 and Line 2")

    with st.expander("Geometry refresher (help)", expanded=False):
        st.markdown(
            "- A straight line has **180°**.\n"
            "- When two rays share a tail at the same point (tail-to-tail), "
            "the angle between them is the **tail-to-tail angle**.\n"
            "- The interior angle inside the triangle is the **supplement** "
            "of that tail-to-tail angle (180° minus that angle).\n"
            "- [Parallel Lines cut by a Transversal (Youtube)](https://www.youtube.com/watch?v=uYRvUdpL94g)\n"
        )

    c1a, c1b = st.columns([2, 1])
    with c1a:
        gamma_guess = st.number_input(
            "Enter your γ (degrees inside the triangle)",
            min_value=0.0, max_value=180.0,
            value=0.0,
            step=0.5,
            key="C_gamma_guess"
        )
    with c1b:
        tol_g = st.slider("Tolerance (deg)", 1, 15, 5, key="C_tol_gamma")

    if st.button("Check γ", key="C_btn_check_gamma"):
        diff = abs(gamma_guess - gamma_expected)
        if diff <= tol_g:
            st.success("✅ Your γ looks reasonable for the interior angle between F₁ and F₂ in the triangle.")
            st.session_state["C_gamma_ok"] = True
            st.session_state["C_gamma_val"] = gamma_guess
        else:
            st.warning(
                "γ doesn’t look quite right.  \n"
                "Hint: First find the **angle between F₁ and F₂ when both start at O** (tail-to-tail).  \n"
                "Then the interior angle γ in the triangle should satisfy:  \n"
                "**γ = 180° − (tail-to-tail angle)**. Try recomputing that relationship."
            )

    # gate: must get γ right before moving on
    if not st.session_state["C_gamma_ok"]:
        st.stop()

    gamma_used = st.session_state["C_gamma_val"]

    # ============================
    # C2 — Law of Cosines for |F₃|
    # ============================
    st.subheader("C2 — Solve |F₃| using the Law of Cosines")

    with st.expander("Trig refresher: Law of Cosines", expanded=False):
        st.latex(r"|F_3|^2 = |F_1|^2 + |F_2|^2 - 2|F_1||F_2|\cos(\gamma)")
        st.caption("Here γ is the **interior angle** between F₁ and F₂ inside the force triangle (from C1).")
        st.markdown("[Law of Cosines (YouTube)](https://www.youtube.com/watch?v=9CGY0s-uCUE)")

    c2a, c2b = st.columns([2, 1])
    with c2a:
        F3_user = st.number_input(
            "Enter your computed |F₃| (N)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="C_F3_user"
        )
    with c2b:
        tol_F3 = st.number_input(
            "Tolerance (N)",
            min_value=0.0,
            value=2.0,
            step=0.5,
            key="C_tol_F3"
        )

    F3_lawcos = law_of_cosines(F1, F2, gamma_used)

    if st.button("Check |F₃|", key="C_btn_check_F3"):
        if abs(F3_user - F3_lawcos) <= tol_F3:
            st.success("✅ Your |F₃| is consistent with the Law of Cosines for this triangle.")
            st.session_state["C_F3_ok"] = True
            st.session_state["C_F3_val"] = F3_user
        else:
            st.warning(
                "|F₃| doesn’t look consistent with your γ and the side lengths.  \n"
                "Hints:\n"
                "- Make sure you are using **the same γ** you found in C1 (the interior angle between F₁ and F₂).  \n"
                "- Check that your calculator is in **degrees**, not radians.  \n"
                "- Re-write the Law of Cosines carefully and plug in the numbers step by step."
            )

    # gate: must get |F3| right
    if not st.session_state["C_F3_ok"]:
        st.stop()

    F3_for_sines = st.session_state["C_F3_val"]

    # ============================
    # C3 — Law of Sines for θ₃
    # ============================
    st.subheader("C3 — Use Law of Sines to find direction of F₃ (θ₃ from +x)")

    with st.expander("Trig refresher: Law of Sines", expanded=False):
        st.latex(r"\frac{|F_1|}{\sin(\alpha)} = \frac{|F_2|}{\sin(\beta)} = \frac{|F_3|}{\sin(\gamma)}")
        st.caption(
            "γ is opposite side |F₃|. Once you find another interior angle (like the one opposite |F₁|), "
            "you can relate that to the orientation of F₃ in the global x–y axes."
        )
        st.markdown("[Law of Sines (YouTube)](https://www.youtube.com/watch?v=9fS0uA4iLxI)")

    # interior angle between line1 and line3 by Law of Sines (internal help, not a 'given answer')
    s = clamp01((F1 * math.sin(math.radians(gamma_used))) / max(F3_for_sines, 1e-9))
    alpha_13 = math.degrees(math.asin(s))  # interior angle between F1 and F3 inside the triangle

    st.caption(
        "Using Law of Sines, you can find the interior angle between **Line 1 (F₁)** and **Line 3 (F₃)**.  \n"
        "From there, combine that interior angle with the known direction of F₁ (30° from +x) to find θ₃."
    )

    st.markdown("**Now convert that interior geometry to the actual direction θ₃ (CCW from +x).**")
    st.caption(
        "Hints:\n"
        "- F₁ has absolute direction θ₁ = 30° (from +x).  \n"
        "- F₃ should point generally **down and to the left** (compare with your force triangle sketch).  \n"
        "- Use your triangle’s interior angles to decide how far F₃ is rotated from the +x-axis.\n"
        "- Finally, express θ₃ between 0° and 360°."
    )

    theta3_guess = st.number_input(
        "Enter your θ₃ (deg CCW from +x, 0°–360°)",
        min_value=0.0,
        max_value=360.0,
        value=0.0,
        step=0.5,
        key="C_theta3_guess"
    )
    tol_th3 = st.slider("Tolerance (deg)", 2, 20, 8, key="C_tol_th3")

    if st.button("Check θ₃", key="C_btn_check_th3"):
        theta3_norm = theta3_guess % 360.0
        th3_norm    = th3_true % 360.0
        diff = (theta3_norm - th3_norm + 180.0) % 360.0 - 180.0  # signed smallest diff

        if abs(diff) <= tol_th3:
            st.success("✅ Your θ₃ is consistent with the expected direction of F₃ for equilibrium.")
            st.session_state["C_dir_ok"] = True
        else:
            st.warning(
                "θ₃ doesn’t look quite right.  \n"
                "Hints:\n"
                "- Think about the **quadrant** F₃ should lie in, based on F₁ and F₂ (your sketch helps!).  \n"
                "- Check how you converted from the triangle’s interior angles to the global x–y axes.  \n"
                "- Make sure you measured θ₃ **counterclockwise from the +x-axis** and wrapped it into 0°–360°."
            )

    if st.session_state["C_gamma_ok"] and st.session_state["C_F3_ok"] and st.session_state["C_dir_ok"]:
        st.success("🎉 C — Compute/Conclude complete.")
        st.session_state["C_done"] = True
        st.session_state["unlock_next_stage"] = True


# ===============================
# S — SANITY CHECK (no components shown)
# Start only after C is complete
# ===============================
if st.session_state.get("C_done", False):
    st.header("S — Sanity check")

    st.markdown(
        "Time to step back and ask: **Do my numbers make physical sense?**  \n"
        "We’ll look at the **direction** of your result and whether its **size fits the triangle**, "
        "without writing any ΣFx/ΣFy equations."
    )

    # --- givens (same as earlier) ---
    F1, th1 = 400.0, 30.0      # N, deg CCW from +x
    F2, th2 = 250.0, 135.0     # N, deg CCW from +x

    # --- student's F3 result from C ---
    F3_mag_student = st.session_state.get("C_F3_val", 0.0)
    theta3_student = st.session_state.get("C_theta3_guess", 0.0)  # deg
    theta3_student_norm = theta3_student % 360.0

    st.markdown("### 1️⃣ Your final answer for F₃")
    col_y, _ = st.columns(2)
    with col_y:
        st.write(f"|F₃| (your answer) = **{F3_mag_student:.2f} N**")
        st.write(f"θ₃ from +x (your answer) = **{theta3_student_norm:.2f}°**")

    st.caption(
        "Remember: angles are measured **counter-clockwise from the +x-axis**, "
        "with 0° to the right, 90° up, 180° left, and 270° down."
    )

    # --- internal reference for sanity (not shown explicitly) ---
    th1r = math.radians(th1)
    th2r = math.radians(th2)
    F1x, F1y = F1 * math.cos(th1r), F1 * math.sin(th1r)
    F2x, F2y = F2 * math.cos(th2r), F2 * math.sin(th2r)
    Sx, Sy   = F1x + F2x, F1y + F2y
    F3x_true = -Sx
    F3y_true = -Sy
    F3_true  = math.hypot(F3x_true, F3y_true)
    th3_true = math.degrees(math.atan2(F3y_true, F3x_true)) % 360.0  # 0–360, used only for hidden checks

    # Helper: smallest signed angle difference between a and b (deg)
    def small_angle_diff(a, b):
        return (a - b + 180.0) % 360.0 - 180.0

    # ============================
    # 2️⃣ Direction sanity check
    # ============================
    st.markdown("### 2️⃣ Direction: does F₃ point roughly where you expect?")

    dir_tol = st.slider(
        "How strict should the direction check be? (tolerance in degrees)",
        min_value=5, max_value=40, value=20, step=1,
        key="S_dir_tol"
    )

    if st.button("Check the direction of my F₃", key="S_btn_check_direction"):
        diff_dir = abs(small_angle_diff(theta3_student_norm, th3_true))

        # Quadrant expectation: for this problem F3 should be down and left (3rd quadrant, 180–270°)
        in_down_left_quadrant = 180.0 < theta3_student_norm < 270.0

        if in_down_left_quadrant and diff_dir <= dir_tol:
            st.success(
                "✅ Your F₃ points generally **down and to the left**, and its angle is consistent with "
                "what we’d expect from the force triangle."
            )
        elif in_down_left_quadrant:
            st.warning(
                "Your F₃ is in the **right general quadrant** (down-left), but the exact angle is a bit off.  \n"
                "Compare your force triangle sketch with the numeric angle you typed in."
            )
        else:
            st.warning(
                "⚠️ Your F₃ does **not** point where we’d expect. For this problem, F₃ should be roughly "
                "**down and to the left** to balance the two cables.  \n"
                "Re-check your triangle and think about which way the ring would move if F₃ were missing."
            )

    # ============================
    # 3️⃣ Triangle-length sanity check
    # ============================
    st.markdown("### 3️⃣ Triangle length check (no equations)")

    lower_bound = abs(F1 - F2)
    upper_bound = F1 + F2

    st.write(
        f"In **any triangle** with sides |F₁| = {F1:.1f} N and |F₂| = {F2:.1f} N, the third side must satisfy:  \n"
        f"**{lower_bound:.1f} N ≤ |F₃| ≤ {upper_bound:.1f} N**."
    )

    if lower_bound <= F3_mag_student <= upper_bound:
        st.success(
            "✅ Your |F₃| lies in the valid range for a triangle with sides 400 N and 250 N. "
            "So the **size** of your answer is geometrically reasonable."
        )
    else:
        st.warning(
            "⚠️ Your |F₃| is **outside** the range that would form a triangle with 400 N and 250 N.  \n"
            "Re-check your γ (interior angle) and your Law of Cosines step in the Compute (C) section."
        )

    # ============================
    # 4️⃣ “Ballpark” size check (hidden reference)
    # ============================
    st.markdown("### 4️⃣ Is the size of F₃ in the right ballpark?")

    size_tol_pct = st.slider(
        "Ballpark tolerance (% difference allowed)",
        min_value=5, max_value=50, value=20, step=5,
        key="S_size_tol_pct"
    )

    # percent difference from internal reference (not shown)
    if F3_true > 1e-9:
        pct_err = abs(F3_mag_student - F3_true) / F3_true * 100.0
    else:
        pct_err = 1000.0  # degenerate

    if pct_err <= size_tol_pct:
        st.success(
            "✅ The size of your F₃ is in the **same ballpark** as what the geometry of the triangle suggests."
        )
    else:
        # give qualitative feedback only
        relation = "smaller" if F3_mag_student < F3_true else "larger"
        st.warning(
            f"Your |F₃| looks quite a bit **{relation}** than what the triangle geometry suggests.  \n"
            "This doesn’t automatically mean it’s wrong, but it’s a good sign to re-check your Law of Cosines work."
        )

    # ============================
    # 5️⃣ Reflection & mark complete
    # ============================
    st.markdown("### 5️⃣ Final reflection")

    c1, c2 = st.columns(2)
    with c1:
        chk_quadrant = st.checkbox(
            "In my sketch, F₃ clearly points **down and to the left**.",
            key="S_chk_quadrant"
        )
        chk_triangle = st.checkbox(
            "My three force vectors form a **closed triangle** when drawn head-to-tail.",
            key="S_chk_triangle"
        )
    with c2:
        chk_values = st.checkbox(
            "My numeric |F₃| and θ₃ match the **shape** of the triangle I drew.",
            key="S_chk_values"
        )
        chk_conf = st.checkbox(
            "If I removed F₃, I can explain which way the ring would accelerate.",
            key="S_chk_conf"
        )

    if st.button("✅ Mark sanity check as complete", key="S_btn_complete"):
        if chk_quadrant and chk_triangle and chk_values:
            st.success("🎓 S — Sanity check complete. You’ve finished the full STATICS method on this problem.")
            st.session_state["S_done"] = True
            st.session_state["unlock_summary"] = True  # if you want a final summary step
        else:
            st.info(
                "Before marking this step complete, make sure you’ve checked the direction, triangle closure, "
                "and that your numbers match your picture."
            )
