# Deployment Process

This guide details how to safely deploy code changes to Harri’s staging and production environments. All deployments must follow this process to ensure stability and traceability.

---

## 1. Prerequisites

- All code must be merged to the main branch after passing code review.
- CI/CD checks (unit/integration tests, linting, build) must pass with no errors.
- All new environment variables or secrets must be updated and documented.

---

## 2. Staging Deployment

1. Use the internal deployment tool or run:
      ./scripts/deploy.sh staging

2. Confirm deployment by checking logs in the deployment dashboard.

3. Run automated smoke tests:
      pytest --env=staging

4. If failures occur, roll back using:
      ./scripts/rollback.sh staging

5. Notify your team of deployment status in #deployments Slack channel.

---

## 3. Production Deployment

- Only team leads or authorized engineers may deploy to production.
- Repeat steps 1–4 above, using the production environment:
      ./scripts/deploy.sh production

- Double-check the deployment dashboard for errors.
- After deployment, verify using application health checks.
- For critical releases, announce completion and status in #engineering-announcements.

---

## 4. Troubleshooting & Rollbacks

- If deployment fails or application is unhealthy, initiate a rollback immediately.
- Document all incidents and solutions in the incident log (see 'escalation_policy.md').

---

## 5. Best Practices

- Schedule deployments during low-traffic hours whenever possible.
- Never deploy directly to production from a personal branch.
- Maintain up-to-date documentation for all scripts and processes.

---

## 6. Support

- On-call DevOps Engineer: Adam Smith (adam@harri.com)
- Deployment Tool Guide: [link to internal wiki]

*For escalations, see 'escalation_policy.md' and contact your team lead.*
