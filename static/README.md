# Dustin Downs Bars — Website

Dual-bar website for **ALiBi Bar & Grill** (Marinette, WI) and **Ogden Club** (Menominee, MI).

## Features
- Toggle between ALiBi and Ogden Club
- Full real menus for both bars
- ALiBi: Fixed daily specials box (Mon–Fri per the menu)
- Ogden Club: Manager-editable daily special
- Manager login panel (⚙ Manager button, top right)

---

## Deploy with Docker

### 1. Change the manager password (recommended)
Edit `docker-compose.yml` and set:
```
MANAGER_PASSWORD=your-new-password
SECRET_KEY=some-long-random-string
```

### 2. Build and run
```bash
docker compose up -d --build
```

Site will be live at **http://localhost:5000**

### 3. Stop the site
```bash
docker compose down
```

### 4. View logs
```bash
docker compose logs -f
```

---

## Manager Access
1. Click the **⚙ Manager** button in the top-right corner
2. Enter the manager password (default: `ogden2026`)
3. Type in today's special — Title, Description, and Price
4. Hit **Save Special** — it updates instantly for all visitors

Daily specials are saved persistently in a Docker volume (`bar-data`), so they survive container restarts.

---

## Environment Variables
| Variable | Default | Description |
|---|---|---|
| `MANAGER_PASSWORD` | `ogden2026` | Password for manager login |
| `SECRET_KEY` | `dustin-downs-bars-2026` | Flask session secret (change this!) |

---

## File Structure
```
bar-site/
├── app.py              # Flask backend
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── static/
│   └── index.html      # Full single-page site
└── README.md
```
