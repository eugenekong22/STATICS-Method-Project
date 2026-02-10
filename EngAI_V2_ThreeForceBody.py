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

st.set_page_config(page_title="STATICS Method — Tank Problem", page_icon="🛢️", layout="centered")

# ----------------------------
# 1. PROBLEM DEFINITION (Always Visible)
# ----------------------------
st.title("Cylindrical Tank: Three-Force Member")

st.info("🖼️ **Reference:** Please refer to the diagram provided in the assignment.")

PROBLEM_TEXT = (
    "A **500-lb** cylindrical tank ($W$), **8 ft in diameter**, is to be raised over a **2-ft obstruction**.\n"
    "The corner of the obstruction at $A$ is rough. A cable pulls horizontally ($T$) from the top.\n"
    "**Goal:** Determine the tension $T$ and the reaction at A ($R_A$) using the **Three-Force Rigid Body** principle."
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

# Study Timer Duration (3 mins)
STUDY_DURATION = 180 

VOCAB = [
    {"term": "Three-Force Principle", "def": "If a body is in equilibrium under 3 forces, their lines of action must meet at a single point (Concurrency)."},
    {"term": "Point of Concurrency", "def": "The intersection point. Here, Weight (Vertical) and Tension (Horizontal) meet at the top of the tank."},
    {"term": "Isosceles Triangle", "def": "A triangle with two equal sides. The base angles are equal. This is the key to solving the geometry!"},
    {"term": "Impending Motion", "def": "The tank is about to lift off, so the floor reaction at B is zero."}
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
    if st.button("▶️ Begin STATICS Method"):
        st.session_state.step_idx = 1
        st.session_state.start_time = time.time()
        st.rerun()
    st.stop()

# ======================================================
# S — STUDY (Step 1)
# ======================================================
if st.session_state.step_idx >= 1:
    st.header("S — Study & Vocabulary")
    
    # --- Timer ---
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

    # --- Flashcards ---
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

    # --- Givens ---
    st.write("#### Identify Key Parameters")
    GIVEN_OPTS = [
        ("Weight W = 500 lb (Vertical)", True),
        ("Tension T is Horizontal (Top)", True),
        ("Corner A is Rough (Direction of Force A is unknown)", True),
        ("Reaction at B = 0", True),
        ("Radius = 4 ft", True)
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
            if correct == 5:
                st.success("Correct parameters identified.")
                st.session_state.step_idx = 2
                st.rerun()
            else:
                st.warning("Please ensure you have selected all valid parameters.")

# ======================================================
# T — TRANSLATE (Step 2: Diagramming)
# ======================================================
if st.session_state.step_idx >= 2:
    st.divider()
    st.header("T — Translate")

    st.subheader("1. Locate the Point of Concurrency")
    
    # --- Dropdown Review ---
    with st.expander("📘 Review: What is the Point of Concurrency?"):
        st.write("""
        **The Three-Force Principle:**
        If a rigid body is in equilibrium under the action of only three forces, the lines of action of these forces must be **concurrent** (intersect at a single point) or be parallel.
        
        * Since Weight (Vertical) and Tension (Horizontal) are NOT parallel, they must intersect.
        * The third force (Reaction A) **must** pass through this same intersection point.
        * Youtube Video: https://www.youtube.com/watch?v=1irV4NXRZJA
        """)

    st.markdown("""
    * **Weight ($W$)** acts vertically through the center ($G$).
    * **Tension ($T$)** acts horizontally along the top tangent.
    * Where do these two lines intersect? Let's call this **Point C**.
    """)
    
    loc_guess = st.radio("Where is Point C?", 
                         ["At the center G", "At the top of the tank (directly above G)", "At corner A"])
    
    if loc_guess == "At the top of the tank (directly above G)":
        st.success("Correct. Point C is the 'North Pole' of the tank.")
        
        st.subheader("2. Draw the Force Triangle")
        st.info("Now, construct the vector triangle. Since the body is in equilibrium, the vectors must form a closed path.")
        
        if _canvas_ok:
            st.caption("Use the **Line Tool** to draw $W$ (Down), $T$ (Left), and $R_A$ (Closing the triangle).")
            # Force Triangle Canvas
            canvas_tri = st_canvas(
                stroke_width=3, stroke_color="#000", background_color="#fff",
                height=300, width=500, drawing_mode="line", display_toolbar=True, key="canvas_tri_only"
            )

            if st.button("Check Triangle"):
                # Rough check: line counts
                num_tri = len(canvas_tri.json_data["objects"]) if canvas_tri.json_data else 0
                
                if num_tri >= 3:
                    st.success("Vector Triangle looks populated. Let's solve the geometry.")
                    st.session_state.step_idx = 3
                    st.rerun()
                else:
                    st.error(f"Detected {num_tri} lines. Please draw at least 3 vectors to close the triangle.")
    else:
        st.warning("Visualize the vertical line from the center and the horizontal line from the top. Where do they cross?")

# ======================================================
# A — ASSIGN (Step 3: Geometry of Angles)
# ======================================================
if st.session_state.step_idx >= 3:
    st.divider()
    st.header("A — Assign Geometry")
    
    st.write("To solve the Force Triangle, we need the angle of Reaction A.")
    st.info("We will use the physical geometry of the tank (Radius & Obstruction Height) to find this angle.")
    
    st.image("https://i.imgur.com/Jo3xYgI.jpeg", caption="Radius geometry", use_container_width=True) 
    # (Note: In a real app, ensure this URL is valid or remove image)
    
    if st.button("I'm ready to Calculate Angles"):
        st.session_state.step_idx = 4
        st.rerun()

# ======================================================
# I — IMPLEMENT (Step 4: Solving for Angles)
# ======================================================
if st.session_state.step_idx >= 4:
    st.divider()
    st.header("I — Implement Equations")
    
    # --- Step 1: Alpha ---
    st.subheader("Step 1: Find the Angle $\\alpha$")
    st.write("Consider the triangle formed by Center ($G$), Corner ($A$), and the vertical axis.")
    st.write("We know the Hypotenuse is the Radius ($r=4$) and the Vertical side is $(r - h) = 2$.")
    
    st.markdown("**Which trig function relates these sides to $\\alpha$?**")
    
    with st.expander("Need a hint?"):
        st.write("You have the **Adjacent** side (Vertical) and the **Hypotenuse** (Radius).")
        st.write("SOH **CAH** TOA.")
    
    alpha_in = st.number_input("Calculate angle $\\alpha$ (degrees):", min_value=0.0, max_value=90.0)
    
    if st.button("Check Alpha"):
        if abs(alpha_in - 60.0) < 1.0:
            st.success("Correct! $\\alpha = 60^{\\circ}$.")
            st.session_state.alpha_correct = True
        else:
            st.error("Not quite. Check your SOH CAH TOA logic.")

    # --- Step 2: Theta ---
    if st.session_state.get("alpha_correct"):
        st.divider()
        st.subheader("Step 2: Find the Reaction Angle $\\theta$")
        
        st.write("Now consider the triangle formed by points **A, G, and C**.")
        st.write("We need $\\theta$ (the angle at vertex C, which determines the direction of Reaction A).")
        
        q_geo = st.radio("How does finding $\\alpha$ help us find $\\theta$?", 
                         ["They are the same angle (Alternate Interior)", 
                          "Triangle AGC is Isosceles, relating $\\alpha$ to the base angles",
                          "Triangle AGC is a Right Triangle"])
        
        with st.expander("Hint for Step 2"):
            st.write("Look at the sides $AG$ and $GC$. Are they equal? What does that mean for the angles inside that triangle?")
            st.write("The angle at $G$ is $(180 - \\alpha)$.")

        if q_geo == "Triangle AGC is Isosceles, relating $\\alpha$ to the base angles":
            st.success("Exactly. Side $AG$ = Side $GC$ = Radius. Therefore, the base angles are equal.")
            
            theta_in = st.number_input("So, what is the value of $\\theta$ (degrees)?", min_value=0.0)
            
            if st.button("Check Theta"):
                # Angle at G = 120. Sum = 180. 2*theta = 60. theta = 30.
                if abs(theta_in - 30.0) < 1.0:
                    st.success("Perfect. $\\theta = 30^{\\circ}$.")
                    st.session_state.theta_correct = True
                    st.session_state.step_idx = 5
                    st.rerun()
                else:
                    st.warning("Check the math: Angle at G is $120^{\\circ}$. Sum of angles is $180^{\\circ}$.")
        elif q_geo:
             st.warning("Look closer at the lengths of the sides of Triangle AGC.")

# ======================================================
# C — COMPUTE (Step 5: Solve Triangle)
# ======================================================
if st.session_state.step_idx >= 5:
    st.divider()
    st.header("C — Compute Results")
    
    st.write("We now have a Force Triangle with:")
    st.write("1. $W = 500$ lb (Vertical)")
    st.write("2. $T$ (Horizontal)")
    st.write("3. Angle of Reaction $R_A$ is $\\theta = 30^{\\circ}$ from the vertical.")
    
    st.image("https://i.imgur.com/jlJ6Zud.jpeg", caption="Force Triangle Sketch")

    # --- Part 1: Tension ---
    st.subheader("Part 1: Solve for Tension T")
    st.markdown("**Use the Force Triangle to find $T$.**")
    
    with st.expander("Hint for Tension"):
        st.write("$W$ is Adjacent (Vertical). $T$ is Opposite (Horizontal).")
        st.write("Use Tangent.")
    
    t_input = st.number_input("Enter your calculated Tension T (lbs):", min_value=0.0)
    
    if st.button("Check Tension"):
        if abs(t_input - 289.0) < 2.0:
            st.success("CORRECT! Tension $T \\approx 289$ lbs.")
            st.session_state.tension_correct = True
        else:
            st.error("Incorrect. Check your trig function and angle ($30^{\\circ}$).")

    # --- Part 2: Reaction A ---
    if st.session_state.get("tension_correct"):
        st.divider()
        st.subheader("Part 2: Solve for Reaction Force $R_A$")
        st.markdown("**Now find the hypotenuse of the Force Triangle ($R_A$).**")
        
        with st.expander("Hint for Reaction Force"):
            st.write("You can use Cosine ($W$ and $R_A$) or Pythagorean Theorem ($W$ and $T$).")
        
        ra_input = st.number_input("Enter your calculated Reaction Force A (lbs):", min_value=0.0)
        
        if st.button("Check Reaction Force"):
            # Ra = W / cos(30) = 500 / 0.866 = 577.35
            if abs(ra_input - 577.0) < 5.0:
                st.balloons()
                st.success("CORRECT! Reaction $R_A \\approx 577$ lbs.")
                st.session_state.step_idx = 6
                st.rerun()
            else:
                st.error("Incorrect. Remember $R_A$ is the hypotenuse, so it should be larger than $W$.")

# ======================================================
# S — SANITY CHECK (Step 6)
# ======================================================
if st.session_state.step_idx >= 6:
    st.divider()
    st.header("S — Sanity Check")
    
    st.write(f"**Tension:** 289 lbs")
    st.write(f"**Reaction A:** 577 lbs")
    st.write(f"**Weight:** 500 lbs")
    
    st.markdown("""
    **Reflection:**
    * **Tension < Weight:** We have a mechanical advantage because we are pulling from the top.
    * **Reaction > Weight:** The ground must push up hard to counteract both the Weight's downward pull and the Tension's tendency to drive the corner into the ground.
    """)
    
    if st.button("Start New Problem"):
        st.session_state.clear()
        st.rerun()