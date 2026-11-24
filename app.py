import streamlit as st
import pandas as pd
import altair as alt
st.set_page_config(page_title="UCC CGPA Calculator", page_icon=":mortar_board:")

# UCC grading scale: grade letter -> points
ucc_scale = {
    "A": 4.0,
    "B+": 3.5,
    "B": 3.0,
    "C+": 2.5,
    "C": 2.0,
    "D+": 1.5,
    "D": 1.0,
    "E": 0.0,
}

st.title("UCC GPA & CGPA Calculator")
st.info("**Dear student,** welcome! This calculator is for **UCC undergraduate students** (usually 8 semesters over 4 years) and uses the official **UCC grading scale**. Choose your **number of courses**, then select the **credit hours** and **grade** for each course below to see your **semester GPA**, your **new CGPA**, and the **grades you need** for your target class.")
num_courses = st.selectbox("Select number of courses", list(range(1, 16)))

credits = []
grades = []
for i in range(1, num_courses + 1):
    col1, col2 = st.columns(2) 
    c = col1.selectbox("Course " + str(i) + " credit hours", [1, 2, 3, 12], index=2)
    g = col2.selectbox("Course " + str(i) + " grade", list(ucc_scale))
    credits.append(c)
    grades.append(g)



def total_gp(credits, grades):
    total = 0
    for c, g in zip(credits, grades):
        total = total + c * ucc_scale[g]
    return total

def gpa(credits, grades):
    return total_gp(credits, grades) / sum(credits)

st.subheader("Semester GPA: " + str(round(gpa(credits, grades), 4)))
fail_grade = list(ucc_scale)[-1]
if fail_grade in grades:
    st.warning("Warning: grade " + fail_grade + " means Fail. Check UCC's resit rules.")

st.header("CGPA")
prev_cgpa = st.number_input("Your CGPA before this semester", min_value=0.0, max_value=max(ucc_scale.values()), value=0.0, step=0.01, format="%.4f")
prev_credits = st.number_input("Total credit hours before this semester", min_value=0, max_value=300, value=0, step=1)

all_gp = prev_cgpa * prev_credits + total_gp(credits, grades)
all_credits = prev_credits + sum(credits)
new_cgpa = all_gp / all_credits
st.subheader("New CGPA: " + str(round(new_cgpa, 4)))

st.header("Target")
ucc_classes = {
    "First Class": 3.6,
    "Second Class Upper": 3.0,
    "Second Class Lower": 2.5,
    "Third Class": 2.0,
    "Pass": 1.0,
}
target_class = st.selectbox("Class you are aiming for", list(ucc_classes))
target = ucc_classes[target_class]

next_num = st.selectbox("Number of courses next semester", list(range(1, 16)))
next_credits = []
for i in range(1, next_num + 1):
    c = st.selectbox("Next semester course " + str(i) + " credit hours", [1, 2, 3, 12], index=2)
    next_credits.append(c)

needed = (target * (all_credits + sum(next_credits)) - all_gp) / sum(next_credits)
best = max(ucc_scale.values())
worst = min(ucc_scale.values())
if needed > best:
    st.error("Not possible next semester. You would need a GPA of " + str(round(needed, 4)))
elif needed <= worst:
    st.success("Your target is safe, even with the lowest grades.")
else:
    st.info("You need a GPA of " + str(round(needed, 4)) + " next semester.")

def fewest_high(next_credits, needed, high, low):
    n = len(next_credits)
    for k in range(n + 1):
        option = [high] * k + [low] * (n - k)
        if gpa(next_credits, option) >= needed:
            return k
    return None

def option_text(k, n, high, low):
    if k == n:
        return str(n) + " " + high
    elif k == 0:
        return str(n) + " " + low
    else:
        return str(k) + " " + high + " and " + str(n - k) + " " + low

def grade_options(next_credits, needed, how_many=3):
    next_credits = sorted(next_credits)
    letters = list(ucc_scale)[:-1]
    n = len(next_credits)
    found = []
    for i in range(len(letters)):
        for j in range(i + 1, min(i + 3, len(letters))):
            high = letters[i]
            low = letters[j]
            k = fewest_high(next_credits, needed, high, low)
            if k is not None:
                option = [high] * k + [low] * (n - k)
                result = round(gpa(next_credits, option), 4)
                text = option_text(k, n, high, low)
                found.append((result, text))
    options = []
    for result, text in sorted(found):
        if text not in options:
            options.append(text)
    return options[:how_many]

if worst < needed <= best:
    st.write("Grade options for next semester:")
    for option in grade_options(next_credits, needed):
        st.write("- " + option)

st.header("Chart")
chart_df = pd.DataFrame({
    "Measure": ["1. CGPA before", "2. Semester GPA", "3. New CGPA"],
    "Value": [prev_cgpa, gpa(credits, grades), new_cgpa],
})
chart = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X("Measure", title=None),
    y=alt.Y("Value", title="Points", scale=alt.Scale(domain=[0, max(ucc_scale.values())])),
)
st.altair_chart(chart)

st.divider()
st.caption("Built by Mr Edem Yevewonu, Mphil Economic Policy & Data Science student, UCC.")
st.caption("This is a student-made tool, not an official UCC service. Always confirm your results with your official transcript.")