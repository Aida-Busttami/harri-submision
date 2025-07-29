# Code Review Policy

The code review process at Harri ensures quality, security, and maintainability of our software.
All team members are responsible for following and upholding this policy.

---

## 1. Review Requirements

- Every pull request (PR) must be reviewed by at least one other engineer before merging.
- The reviewer should be familiar with the relevant codebase or domain.
- For critical or high-risk changes, two reviewers are required (one must be a team lead).

---

## 2. Pull Request Checklist

Before requesting a review, ensure that:

- The PR description is clear and references any related Jira tickets.
- All CI tests pass (unit, integration, and linting).
- Documentation and comments are updated as needed.
- The code adheres to our team’s style guide and standards.
- Any new dependencies or config changes are documented in the PR.

---

## 3. Reviewer Guidelines

- Begin reviews within 24 hours of assignment.
- Provide actionable feedback; be constructive and respectful.
- Test locally when possible, especially for complex features.
- Approve only when you have full confidence in the change.

---

## 4. Common Reasons for Request Changes

- Incomplete test coverage or failing tests.
- Lack of clear documentation or unclear code.
- Security, performance, or maintainability concerns.
- Violations of team coding standards.

---

## 5. After Approval

- Only team leads or delegated engineers may merge to the main branch.
- After merging, delete the feature branch unless it is needed for future work.
- Announce significant changes in #engineering-announcements Slack channel.

---

## 6. Resources

- See 'onboarding_guide.md' for an overview of the review process in new hire onboarding.
- For questions, contact the Backend Lead (Ahmed Ali) or Frontend Lead (Leen Qasem).

*Your participation in code reviews helps us deliver reliable, maintainable software at Harri.*
