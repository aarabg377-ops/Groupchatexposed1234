# YOUR_BRAND_NAME — Marketing Site

## Setup
```bash
pip install -r requirements.txt
python app.py
```

## URLs
- Homepage:   http://localhost:5000/
- Admin panel: http://localhost:5000/admin?pw=changeme123

## Config (top of app.py)
| Variable      | What to change                          |
|---------------|-----------------------------------------|
| BRAND_NAME    | Your brand/society name                 |
| WEBHOOK_URL   | Discord/Zapier/Make.com webhook URL     |
| ADMIN_PASS    | Password for /admin panel               |

## Features
- Homepage shows your ad photos + Share Location + Upload Photo buttons
- Admin: upload/delete ad photos, see visitor location & photo logs
- All visitor actions are user-triggered (browser asks permission)
- Logs sent to your webhook in real time

## Folder structure
marketing-site/
├── app.py
├── requirements.txt
├── static/uploads/    ← photos saved here
└── templates/
    ├── index.html     ← public site
    └── admin.html     ← your dashboard
