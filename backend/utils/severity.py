def get_severity(confidence):

    if confidence > 90:
        severity = "High"
        recommendation = "Immediate treatment required. Disease may spread rapidly."

    elif confidence >= 70:
        severity = "Moderate"
        recommendation = "Apply recommended pesticide soon and monitor crop."

    else:
        severity = "Early Stage"
        recommendation = "Monitor crop closely and apply preventive measures."

    return severity, recommendation