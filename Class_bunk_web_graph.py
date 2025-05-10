import streamlit as st
import math
import plotly.graph_objects as go

# Attendance calculation function
def calculate_attendance(present, total, required_percentage):
    required_decimal = required_percentage / 100
    current_percentage = (present / total) * 100 if total > 0 else 0

    if total == 0:
        return {"status": "undefined", "current_percentage": 0}

    if present / total < required_decimal - 1e-6:
        needed_classes = math.ceil((required_decimal * total - present) / (1 - required_decimal))
        return {
            "status": "below",
            "current_percentage": current_percentage,
            "needed_classes": needed_classes
        }
    else:
        bunk_days = 0
        while True:
            new_total = total + bunk_days
            new_percentage = present / new_total
            if new_percentage < required_decimal:
                break
            bunk_days += 1

        final_total = total + bunk_days - 1
        final_percentage = (present / final_total) * 100
        return {
            "status": "above",
            "current_percentage": current_percentage,
            "bunk_days": bunk_days - 1,
            "final_total": final_total,
            "final_percentage": final_percentage
        }

# Plotting function
def plot_attendance_graph(present, total, required_percentage):
    current_percentage = (present / total) * 100 if total > 0 else 0
    y_max = min(max(current_percentage, required_percentage) + 10, 100)

    fig = go.Figure(data=[
        go.Bar(name='Current', x=['Attendance'], y=[current_percentage], marker_color='royalblue'),
        go.Bar(name='Required', x=['Attendance'], y=[required_percentage], marker_color='tomato')
    ])
    fig.update_layout(
        barmode='group',
        title='Attendance Progress',
        xaxis_title='Status',
        yaxis_title='Percentage',
        yaxis=dict(range=[0, y_max]),
        template='plotly_white'
    )
    return fig

# Streamlit UI
st.set_page_config(page_title="Attendance Bunk Calculator", page_icon="🎓")
st.title("🎓 Attendance Bunk Calculator")

# User inputs
required_attendance = st.number_input("Required Attendance (%)", min_value=1.0, max_value=100.0, value=75.0)
present_days = st.number_input("Classes Present", min_value=0, value=30)
total_days = st.number_input("Total Classes", min_value=1, value=40)

# Validate user input
if present_days > total_days:
    st.error("⚠️ Classes Present cannot be more than Total Classes.")
else:
    if st.button("Calculate"):
        # Calculate attendance details
        result = calculate_attendance(present_days, total_days, required_attendance)

        # Display results
        st.info(f"📊 Current Attendance: {present_days}/{total_days} → {result['current_percentage']:.2f}%")

        if result["status"] == "below":
            st.error("⚠️ Your attendance is **below** the required threshold.")
            st.warning(f"📌 You must attend **{result['needed_classes']}** more classes without missing any "
                    f"to reach {required_attendance:.2f}%.")
        elif result["status"] == "above":
            if result["bunk_days"] == 0:
                st.warning("⚠️ You can't bunk any more classes without dropping below the required attendance.")
            else:
                st.success(f"🎉 You can bunk **{result['bunk_days']}** more classes.")
                st.info(f"📉 After bunking: {present_days}/{result['final_total']} → {result['final_percentage']:.2f}%")

        # Plot attendance progress graph
        fig = plot_attendance_graph(present_days, total_days, required_attendance)
        st.plotly_chart(fig)
        st.caption("This bar graph shows your current attendance compared to the required percentage.")
