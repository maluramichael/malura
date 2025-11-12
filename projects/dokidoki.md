---
title: DokiDoki
date: 2025-11-11
tags: devops deployment automation python flask systemd-nspawn
abandoned: false
---

Eine selbst entwickelte Container-Plattform für automatisches Deployment von Web-Anwendungen. DokiDoki ermöglicht es, Git-Repositories mit wenigen Klicks zu deployen und über Webhooks automatisch zu aktualisieren.

Die Plattform nutzt systemd-nspawn für leichtgewichtige Container-Isolation, verwaltet automatisch SSL-Zertifikate über Let's Encrypt und routet Traffic über Nginx. Git-Integration mit SSH-Key-Management erlaubt den Zugriff auf private Repositories.

**Features:**

- Automatische Deployments per GitHub Webhook
- Support für Python, PHP, Node.js und statische Sites
- Build-Prozesse für Node.js-Projekte (npm install & build)
- YAML-basierte Konfiguration direkt im Repository
- Verschlüsselte Umgebungsvariablen für sensible Daten
- Deployment-Historie mit Logs
- CLI-Tools für Server-Administration

**Beispiel-Konfigurationen:**

Statische Site mit Node.js Build (React/Vite):

```yaml
runtime:
  type: static
  subtype: node

app:
  serve_directory: dist
```

Python Flask Anwendung:

```yaml
runtime:
  type: python
  version: "3.11"

app:
  start_command: "gunicorn --bind 0.0.0.0:${PORT} wsgi:app"
  working_directory: "."
  env_file: ".env"
```

Statische HTML-Site:

```yaml
runtime:
  type: static

app:
  serve_directory: "."
```

Die Plattform hostet aktuell alle meine Web-Projekte und ermöglicht schnelle Iteration durch automatische Deployments direkt aus GitHub.
