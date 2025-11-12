---
title: DokiDoki
date: 2025-11-11
tags: devops deployment automation python flask systemd-nspawn
abandoned: false
---

Eine selbst entwickelte Container-Plattform für automatisches Deployment von Web-Anwendungen. DokiDoki ermöglicht es, Git-Repositories mit wenigen Klicks zu deployen und über Webhooks automatisch zu aktualisieren.

**Technische Details:**
- **Container-Virtualisierung** mit systemd-nspawn für leichtgewichtige Isolation
- **Automatische SSL-Zertifikate** über Let's Encrypt und Certbot
- **Nginx Reverse Proxy** für Routing und statisches File-Serving
- **Git-Integration** mit SSH-Key-Management für private Repositories
- **Webhook-Support** für automatische Deployments bei Git-Push
- **Multi-Runtime-Support**: Python, PHP, Node.js und statische Sites

**Besondere Features:**
- **Build-Prozesse** für Node.js-Projekte (npm install & build)
- **Konfiguration per YAML** (dokidoki.yaml) im Repository
- **Verschlüsselte Umgebungsvariablen** für sensible Daten
- **Deployment-Historie** mit Logs und Rollback-Möglichkeit
- **CLI-Management** für Server-Administration

Die Plattform hostet aktuell alle meine Web-Projekte und ermöglicht schnelle Iteration durch automatische Deployments direkt aus GitHub.
