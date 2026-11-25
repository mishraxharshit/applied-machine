# Security Policy

## Reporting a vulnerability
Please do **not** open a public issue. Use GitHub's private "Report a vulnerability" button
on the Security tab, or email: `security@YOUR-DOMAIN` (replace before publishing).

We aim to acknowledge reports within 3 working days.

## Scope notes
- `services/ingest` accepts data over HTTP. Run it behind a reverse proxy with authentication
  if exposed beyond localhost.
- Production traces may contain personal data. Scrub or anonymize before training.
