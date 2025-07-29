# Escalation Policy

Harri’s escalation policy outlines how to handle critical issues, outages, and urgent incidents to ensure minimal disruption and timely resolution.

---

## 1. When to Escalate

Escalate immediately in the following situations:
- Production outages or service unavailability
- Major security vulnerabilities or breaches
- Data loss or corruption
- Failed deployments affecting users
- Any issue with business or legal impact

---

## 2. Immediate Actions

1. Page the current on-call engineer via PagerDuty or phone.
2. Document the incident in Jira and the #incidents Slack channel.
3. Collect logs and initial diagnostics for context.
4. If not resolved within 1 hour, escalate to engineering management and relevant stakeholders.

---

## 3. Escalation Matrix

- **First Responder:** On-call DevOps Engineer (see 'team_structure.md')
- **Secondary:** Backend or Frontend Lead (see 'team_structure.md')
- **Management:** Director of Engineering or CTO

---

## 4. Communication Guidelines

- All escalations must be communicated in writing via Slack and email.
- Provide clear incident summaries, current status, and next steps.
- Update the incident log throughout the resolution process.

---

## 5. Post-Incident

- After the incident, conduct a blameless postmortem within 48 hours.
- Document root causes, actions taken, and follow-up tasks in Jira.
- Update playbooks and documentation to prevent recurrence.

---

## 6. Resources

- For on-call schedule, see 'team_structure.md'.
- PagerDuty access: [link to internal PagerDuty]

*Remember: Fast, clear communication is key to effective escalations and rapid recovery.*
