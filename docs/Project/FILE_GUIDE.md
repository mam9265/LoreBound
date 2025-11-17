# 📁 File Guide

Quick reference for what each file in the root directory is for.

---

## 📖 Documentation Files

### Essential (Read These First)
- **`README.md`** - Project introduction, quick start, commands
- **`PROJECT_OVERVIEW.md`** - Complete project details, architecture, technology stack
- **`TESTING_GUIDE.md`** - How to test backend and frontend
- **`SPRINT_STATUS.md`** - Current development status, what's done/in-progress/planned

### Detailed Documentation
- **`docs/`** - Folder with detailed technical documentation
  - `API_DOCUMENTATION.md` - Complete REST API reference
  - `ARCHITECTURE_OVERVIEW.md` - System design
  - `AUTHENTICATION_SETUP.md` - Auth implementation
  - `SERVICES_OVERVIEW.md` - Backend services
  - `DEPLOYMENT_GUIDE.md` - Production deployment

---

## 🔧 Executable Scripts

### Active Scripts (Use These)
- **`test_integration.ps1`** ⭐ - Automated backend testing (14 tests)
- **`start_frontend_test.ps1`** ⭐ - Launch frontend with guided setup
- **`test_backend.ps1`** - Legacy backend test script (Windows)
- **`test_backend.sh`** - Legacy backend test script (Linux/Mac)

### How to Use
```powershell
# Test backend
.\test_integration.ps1

# Launch frontend
.\start_frontend_test.ps1
```

---

## 📦 Project Folders

### Main Folders
- **`lorebound/`** - React Native mobile app (frontend)
  - All mobile app code
  - Screens, services, components
  - Run `npm start` from here

- **`lorebound-backend/`** - FastAPI backend server
  - API, database, services
  - Docker containers defined here
  - Run `docker-compose up -d` from here

- **`docs/`** - Technical documentation
  - API specs
  - Architecture diagrams
  - Deployment guides

- **`archive/`** - Old/reference documents
  - Outdated files moved here
  - Phase-specific docs
  - Historical reference

---

## 📋 File Purpose Summary

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` | Project intro | First time setup |
| `PROJECT_OVERVIEW.md` | Full project details | Understanding system |
| `TESTING_GUIDE.md` | Testing instructions | Before testing |
| `SPRINT_STATUS.md` | Development status | Check progress |
| `test_integration.ps1` | Backend tests | Testing backend |
| `start_frontend_test.ps1` | Frontend launcher | Testing frontend |
| `FILE_GUIDE.md` | This file | Finding files |

---

## 🗂️ Archive Folder Contents

Files that were consolidated or superseded:

### Consolidated into `TESTING_GUIDE.md`
- `INTEGRATION_TEST_PLAN.md` - Detailed test plan
- `FRONTEND_TEST_GUIDE.md` - Frontend testing steps
- `FRONTEND_TEST_CHECKLIST.md` - Test checklist
- `TEST_QUESTIONS_ANSWERS.md` - Answer key
- `TEST_RESULTS_SUMMARY.md` - Test results
- `RUN_TESTS_GUIDE.md` - Setup guide
- `run_integration_tests.ps1` - Older test script

### Consolidated into `PROJECT_OVERVIEW.md`
- `API_QUICK_REFERENCE.md` - API quick ref
- `CONTENT_ENDPOINTS_STATUS.md` - Endpoint status
- `PHASE2_QUICK_START.md` - Phase 2 start
- `PHASE2_SUMMARY.md` - Phase 2 summary
- `PHASE2_TESTING_GUIDE.md` - Phase 2 testing

### Consolidated into `SPRINT_STATUS.md`
- `SPRINT_INDEX.md` - Sprint index
- `SPRINT_ROADMAP.md` - Sprint roadmap
- `SPRINT_SUMMARY.md` - Sprint summary
- `VISUAL_TIMELINE.md` - Visual timeline

**Note:** These files are kept in `archive/` for reference but are no longer actively maintained.

---

## 🎯 Quick Navigation

**Need to...**

### Start the Project
1. Read: `README.md` (Quick Start section)
2. Run: `cd lorebound-backend && docker-compose up -d`
3. Run: `cd lorebound && npm start`

### Test Backend
1. Read: `TESTING_GUIDE.md` (Backend Testing section)
2. Run: `.\test_integration.ps1`

### Test Frontend
1. Read: `TESTING_GUIDE.md` (Frontend Testing section)
2. Run: `.\start_frontend_test.ps1`

### Understand the System
1. Read: `PROJECT_OVERVIEW.md` (Architecture section)
2. Read: `docs/ARCHITECTURE_OVERVIEW.md` (Detailed design)

### Check What's Done
1. Read: `SPRINT_STATUS.md` (Current Status section)
2. Read: `PROJECT_OVERVIEW.md` (Features section)

### Deploy to Production
1. Read: `docs/DEPLOYMENT_GUIDE.md`
2. Follow deployment steps

### Learn the API
1. Visit: http://localhost:8000/docs (interactive)
2. Read: `docs/API_DOCUMENTATION.md` (complete reference)

---

## 🔄 File Maintenance

### Active Files (Keep Updated)
- `README.md`
- `PROJECT_OVERVIEW.md`
- `TESTING_GUIDE.md`
- `SPRINT_STATUS.md`
- Test scripts (`.ps1` files)

### Reference Files (As-Needed Updates)
- `docs/` folder contents
- `FILE_GUIDE.md` (this file)

### Archive Files (No Updates)
- Everything in `archive/` folder
- Kept for historical reference only

---

## 📝 File Relationships

```
README.md (Start Here)
    ↓
PROJECT_OVERVIEW.md (Learn More)
    ↓
TESTING_GUIDE.md (Test It)
    ↓
SPRINT_STATUS.md (Track Progress)
    ↓
docs/ (Deep Dive)
```

---

## ⚠️ Important Notes

1. **Don't edit archive files** - They're outdated, edit the current versions instead
2. **Test scripts are up-to-date** - Use `test_integration.ps1` and `start_frontend_test.ps1`
3. **Docs folder has details** - Root docs are summaries, see `docs/` for complete info
4. **Interactive API docs** - Best way to explore API is http://localhost:8000/docs

---

## 🆘 If You're Lost

1. **Just starting?** → Read `README.md`
2. **Want to understand?** → Read `PROJECT_OVERVIEW.md`
3. **Ready to test?** → Read `TESTING_GUIDE.md`
4. **Need API info?** → Visit http://localhost:8000/docs or read `docs/API_DOCUMENTATION.md`
5. **Still confused?** → All docs link to each other, follow the references!

---

**This guide is your map to the codebase!** 🗺️

