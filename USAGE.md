# 📖 Snippet Manager - Usage Guide

Complete reference for all commands and features.

---

## 🚀 Getting Started

### First-Time Setup

```bash
# Initialize system with master password
python main.py init

# You'll be prompted:
# Create master password (min 6 chars): ******
# Confirm password: ******
```

**Password Requirements:**
- Minimum 6 characters
- Must contain letters AND numbers
- Will be used to protect locked snippets

---

## 📝 Adding Snippets

### Basic Add

```bash
# Simple snippet (public)
python main.py add "Git Reset" "git reset --hard HEAD"

# With tag
python main.py add "Docker Build" "docker build -t app ." --tag docker

# Locked snippet (password-protected)
python main.py add "API Key" "sk-123456" --tag secrets --access LOCKED
```

### Examples

```bash
# Git command
python main.py add "Git Stash" "git stash save 'work in progress'" --tag git

# Python snippet
python main.py add "List Comprehension" "[x*2 for x in range(10)]" --tag python

# Database query
python main.py add "User Count" "SELECT COUNT(*) FROM users;" --tag sql

# Multi-line content (use quotes)
python main.py add "Bash Script" "#!/bin/bash
echo 'Starting...'
./deploy.sh" --tag bash
```

---

## 📋 Listing Snippets

### List All Active Snippets

```bash
python main.py list
```

**Output:**
```
ID                   TITLE                                              TAG             ACCESS
──────────────────────────────────────────────────────────────────────────────────────────────
22032026_00001       Git Reset Hard                                     git             
22032026_00002       API Key                                            secrets         🔒

Total: 2 active snippets
```

### Filter by Tag

```bash
# Show only Python snippets
python main.py list --tag python

# Show only Git snippets
python main.py list --tag git
```

### Show Archived Snippets

```bash
python main.py list --archived
```

---

## 🔍 Searching Snippets

### Search by Keyword

```bash
# Search in title and tag
python main.py search docker

# Search is case-insensitive
python main.py search PYTHON  # Finds "python" tags
```

**Output:**
```
🔍 Search results for 'docker':

ID                   TITLE                                              TAG             ACCESS
──────────────────────────────────────────────────────────────────────────────────────────────
22032026_00002       Docker Build                                       docker          
22032026_00005       Docker Compose                                     docker          

Found: 2 snippets
```

---

## 👁️ Viewing Snippets

### View Public Snippet

```bash
python main.py view 22032026_00001
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Git Reset Hard

  ID:      22032026_00001
  Tag:     git
  Status:  ACTIVE
  Access:  PUBLIC
  Created: 22/03/2026 10:30:45

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

git reset --hard HEAD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### View Locked Snippet

```bash
python main.py view 22032026_00002
```

**You'll be prompted:**
```
🔒 This snippet is LOCKED
   Title: API Key
   Enter master password to view content

Master password: ******

[Shows content if password correct]
```

---

## 🗄️ Archiving Snippets

### Archive (Hide from Default List)

```bash
python main.py archive 22032026_00001

# Confirmation prompt:
Archive 'Git Reset Hard'? (y/n): y
✓ Snippet archived: 22032026_00001
```

### Unarchive (Restore)

```bash
python main.py unarchive 22032026_00001

# Confirmation prompt:
Unarchive 'Git Reset Hard'? (y/n): y
✓ Snippet restored: 22032026_00001
```

---

## 🔒 Locking/Unlocking Snippets

### Lock a Snippet

```bash
python main.py lock 22032026_00001

# Confirmation:
Lock 'Git Reset Hard'? (y/n): y
✓ Snippet locked 🔒: 22032026_00001

This snippet now requires your master password to view.
```

### Unlock a Snippet

```bash
python main.py unlock 22032026_00002

# Password prompt:
Enter master password to unlock
Master password: ******

# Then confirmation:
Unlock 'API Key'? (y/n): y
✓ Snippet unlocked: 22032026_00002
```

---

## 🔐 Security Features

### Password Attempts

- **Maximum Attempts**: 3 failed attempts
- **Lockout Duration**: 30 seconds
- **Auto-Reset**: Successful login resets counter

**Example:**
```
Master password: ******
✗ Wrong password (2 attempts remaining)

Master password: ******
✗ Wrong password (1 attempt remaining)

Master password: ******
✗ Too many failed attempts. Account locked for 30 seconds.
```

### Change Master Password

Currently not supported. To reset:
1. Delete `data/config.json`
2. Run `python main.py init` again
3. **Warning**: All locked snippets will become inaccessible

---

## 💡 Tips & Best Practices

### Organization

```bash
# Use consistent tag naming
--tag git          # Good
--tag Git_Commands # Avoid (gets normalized to git_commands)

# Common tags:
--tag git
--tag docker
--tag python
--tag bash
--tag sql
--tag secrets
--tag config
```

### Security

```bash
# Lock sensitive snippets immediately
python main.py add "AWS Key" "AKIAIOSFODNN7..." --tag secrets --access LOCKED

# Archive old credentials
python main.py archive <old-key-id>
```

### Workflow

```bash
# Daily routine:
python main.py list --tag docker     # Find Docker commands
python main.py search kubernetes     # Search recent notes
python main.py add ...               # Save new discoveries

# Weekly cleanup:
python main.py list                  # Review active snippets
python main.py archive <old-ids>     # Archive outdated ones
```

---

## 📊 Common Workflows

### Developer Workflow

```bash
# Morning: Review recent snippets
python main.py list

# During work: Save useful commands
python main.py add "Port Forward" "kubectl port-forward svc/app 8080:80" --tag k8s

# End of day: Archive completed work
python main.py archive 22032026_00005
```

### DevOps Workflow

```bash
# Store deployment commands
python main.py add "Deploy Prod" "./deploy.sh prod" --tag deploy

# Lock server credentials
python main.py add "SSH Key" "-----BEGIN RSA..." --tag secrets --access LOCKED

# Quick access during incident
python main.py search rollback
```

---

## 🛠️ Command Reference

### All Commands

```bash
python main.py init                              # First-time setup
python main.py add TITLE CONTENT [OPTIONS]       # Add snippet
python main.py list [--tag TAG] [--archived]     # List snippets
python main.py search KEYWORD                    # Search snippets
python main.py view SNIPPET_ID                   # View snippet
python main.py archive SNIPPET_ID                # Archive snippet
python main.py unarchive SNIPPET_ID              # Restore snippet
python main.py lock SNIPPET_ID                   # Lock snippet
python main.py unlock SNIPPET_ID                 # Unlock snippet
python main.py --help                            # Show help
```

### Options

- `--tag TAG`: Category tag (lowercase, underscores)
- `--access LEVEL`: PUBLIC or LOCKED (default: PUBLIC)
- `--archived`: Show archived snippets (with list)

---

## 🐛 Troubleshooting

### Common Issues

**"System not initialized"**
```bash
python main.py init
```

**"Snippet not found"**
```bash
# Check ID is correct
python main.py list

# Use search to find it
python main.py search <keyword>
```

**"Account locked"**
```bash
# Wait 30 seconds, or:
rm data/attempts.json
```

**Forgot master password**
```bash
# Nuclear option - loses all locked snippets:
rm data/config.json
python main.py init
```

---

## 🎯 Quick Reference Card

```bash
# Essential Commands
init       - Setup master password
add        - Create new snippet
list       - Show all snippets
search     - Find by keyword
view       - Display snippet content

# Management
archive    - Hide from list
lock       - Require password
unlock     - Remove password

# Shortcuts
python main.py list --tag <tag>     # Filter by tag
python main.py search <keyword>     # Quick search
python main.py view <id>            # Quick view
```

---

**Need help? Run `python main.py --help` or check README.md**