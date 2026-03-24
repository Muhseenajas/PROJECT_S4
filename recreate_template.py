#!/usr/bin/env python3
"""Recreate enter_hr_score.html with proper content"""

template_content = """{% extends 'core/base.html' %}
{% block title %}HR Interview Score - RecruitAI{% endblock %}
{% block content %}
<div class="container" style="max-width:600px;">
    <div class="page-header">
        <h1>📝 Enter HR Score</h1>
        <p>Record HR interview results</p>
    </div>
    <div class="card">
        <div style="background:#e8f4fd; border-radius:12px; padding:1rem; margin-bottom:1.5rem;">
            <div style="font-weight:700; font-size:1.1rem;">
                {{ application.candidate.get_full_name|default:application.candidate.username }}
            </div>
            <div style="color:#888; font-size:0.88rem;">{{ application.candidate.email }}</div>
            <div style="margin-top:0.5rem;">Job: <strong>{{ application.job.title }}</strong></div>
            <div style="margin-top:0.3rem;">📅 HR Interview Date: <strong>{{ application.hr_date|default:"Not set" }}</strong></div>
            {% if application.technical_score is not None %}
            <div style="margin-top:0.3rem;">💻 Technical Score: <strong>{{ application.technical_score }}/10</strong></div>
            {% endif %}
        </div>
        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label class="form-label">✅ Did Candidate Attend? *</label>
                <div style="display:flex; gap:1rem; margin-top:0.5rem;">
                    <label style="flex:1; cursor:pointer; padding:0.75rem; border:2px solid #e8e8e8; border-radius:10px; text-align:center;">
                        <input type="radio" name="hr_attended" value="True" style="margin-right:0.4rem;"
                            {% if application.hr_attended == True %}checked{% endif %}>
                        ✅ Yes, Attended
                    </label>
                    <label style="flex:1; cursor:pointer; padding:0.75rem; border:2px solid #e8e8e8; border-radius:10px; text-align:center;">
                        <input type="radio" name="hr_attended" value="False" style="margin-right:0.4rem;"
                            {% if application.hr_attended == False %}checked{% endif %}>
                        ❌ Absent
                    </label>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">🎯 HR Score (0–10) *</label>
                <input type="number" name="hr_score" class="form-control"
                       min="0" max="10" step="0.1" placeholder="e.g. 8.0"
                       value="{{ application.hr_score|default:'' }}" required>
                <div class="form-text">Rate candidate's HR interview out of 10</div>
            </div>
            <div class="form-group">
                <label class="form-label">📝 Feedback</label>
                <textarea name="hr_feedback" class="form-control" rows="4"
                    placeholder="Enter HR interview feedback...">{{ application.hr_feedback }}</textarea>
            </div>
            <div class="alert alert-info" style="font-size:0.85rem;">
                🧠 After saving, <strong>Final Score</strong> will be automatically calculated:<br>
                Final = (0.6 × Resume Score) + (0.3 × Technical Score) + (0.1 × HR Score)
            </div>
            <div style="display:flex; gap:1rem; justify-content:flex-end; margin-top:1rem;">
                <a href="{% url 'job_applicants' application.job.pk %}" class="btn btn-secondary">Cancel</a>
                <button type="submit" class="btn btn-primary">💾 Save & Calculate Final Score</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}"""

with open(r"c:\Users\muhseena\Desktop\AI\recruitment_ai\core\templates\core\enter_hr_score.html", 'w', encoding='utf-8') as f:
    f.write(template_content)

print("✅ enter_hr_score.html recreated successfully!")
