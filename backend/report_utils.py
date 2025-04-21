import openai
import os

# 🔐 Read from environment variable only
openai.api_type = os.environ.get("OPENAI_API_KEY")

# ----------------------------
# Single-Row GPT Report
# ----------------------------
def generate_single_report(sensor_row):
    """
    Accepts one SQLAlchemy SensorData row and generates a GPT-based report string.
    """
    prompt = (
        f"You are a digital health assistant. Based on the patient's recent biometric data:\n"
        f"Heart Rate: {sensor_row.heart_rate} BPM\n"
        f"HRV: {sensor_row.hrv} ms\n"
        f"GSR Average: {sensor_row.gsr_mean}\n"
        f"GSR Peaks: {sensor_row.gsr_peak_count}\n"
        f"GSR Trend: {sensor_row.gsr_trend}\n\n"
        f"Write a brief 3-4 sentence summary of the patient's stress status. "
        f"Include any suggestions or alerts if necessary."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"⚠️ GPT report generation failed: {e}")
        return "Stress report not available due to system error."


# ----------------------------
# Full Report for Multiple Rows
# ----------------------------
def generate_stress_report(sensor_data_list):
    """
    Accepts a list of dicts with patient data to summarize a 10-minute window.
    Each dict should contain keys like heart_rate, hrv, gsr_mean, etc.
    """

    prompt = (
        "You are a medical assistant generating a stress analysis summary for a patient. "
        "Based on the following biometric time series, provide a concise report that includes:\n"
        "- Overall stress level (low/moderate/high)\n"
        "- Heart Rate and HRV patterns\n"
        "- GSR conductance trends and spikes\n"
        "- Any detected arrhythmia concerns\n"
        "- Suggestions or insights to improve stress response\n\n"
        f"Sensor Data:\n{sensor_data_list}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"⚠️ GPT full report failed: {e}")
        return "Unable to generate full stress summary at this time."



