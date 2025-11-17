# Scripts Directory

This directory contains utility scripts organized into logical subdirectories.

## 📁 Directory Structure

```
scripts/
├── seeding/          # Database seeding scripts
├── testing/          # Testing and validation scripts
├── admin/            # Admin and management scripts
├── validation/       # Configuration and service validation
├── utils/            # Utility scripts
└── [compatibility wrappers]  # Backward compatibility wrappers
```

## 🔧 Script Categories

### Seeding Scripts (`seeding/`)

- **`populate_questions.py`** - Populate database with trivia questions from OpenTDB
- **`seed_content_data.py`** - Seed dungeons and content structure
- **`seed_items.py`** - Seed items for character customization
- **`seed_once.py`** - Quick one-time seeding script
- **`seed_questions_simple.py`** - Simple question seeding
- **`trigger_seeding.py`** - Trigger background seeding task
- **`clear_and_repopulate.py`** - Clear and repopulate questions

### Testing Scripts (`testing/`)

- **`test_*.py`** - Various test scripts for API endpoints, services, and features

### Admin Scripts (`admin/`)

- **`admin_seed_data.py`** - Admin data seeding
- **`check_api_status.py`** - Check external API status
- **`check_questions.py`** - Check question counts
- **`create_*.py`** - Create test data
- **`add_*.py`** - Add test data
- **`give_*.py`** - Give items/users to test accounts

### Validation Scripts (`validation/`)

- **`validate_config.py`** - Validate configuration
- **`validate_services.py`** - Validate services
- **`final_validation.py`** - Final validation checks

### Utility Scripts (`utils/`)

- **`generate_jwt_keys.py`** - Generate JWT keys
- **`debug_registration.py`** - Debug registration issues
- **`complete_auth_demo.py`** - Authentication demo
- **`direct_api_test.py`** - Direct API testing
- **`simple_test_refresh.py`** - Simple test refresh

## 🚀 Usage

### Backward Compatibility

All scripts maintain backward compatibility. You can still use:

```bash
# These commands still work exactly as before
docker-compose exec api python -m scripts.populate_questions
docker-compose exec api python -m scripts.seed_content_data
docker-compose exec api python -m scripts.seed_items
docker-compose exec api python -m scripts.trigger_seeding
docker-compose exec api python -m scripts.check_api_status
```

### New Paths (Optional)

You can also use the new organized paths:

```bash
# New organized paths
docker-compose exec api python -m scripts.seeding.populate_questions
docker-compose exec api python -m scripts.seeding.seed_content_data
docker-compose exec api python -m scripts.admin.check_api_status
docker-compose exec api python -m scripts.testing.test_api_endpoints
```

## 📝 Common Commands

### Seeding Database

```bash
# Populate questions (most common)
docker-compose exec api python -m scripts.populate_questions

# Seed specific category
docker-compose exec api python -m scripts.populate_questions --category history --count 100

# Seed content (dungeons)
docker-compose exec api python -m scripts.seed_content_data

# Seed items
docker-compose exec api python -m scripts.seed_items
```

### Admin Tasks

```bash
# Check API status
docker-compose exec api python -m scripts.check_api_status

# Check question counts
docker-compose exec api python -m scripts.admin.check_questions
```

### Testing

```bash
# Run test scripts
docker-compose exec api python -m scripts.testing.test_api_endpoints
docker-compose exec api python -m scripts.testing.test_daily_challenge
```

## 🔄 Migration Notes

- All scripts have been moved to subdirectories for better organization
- Compatibility wrappers ensure existing commands continue to work
- Path references in scripts have been updated to work from subdirectories
- Documentation references remain valid (backward compatible)

## 📚 Related Documentation

- **Database Seeding**: See `docs/Services/Database/DATABASE_SEEDING_GUIDE.md`
- **Quick Reference**: See `docs/Services/Database/QUICK_SEEDING_REFERENCE.md`

