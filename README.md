# 📝 Personal Snippet Manager

A secure, lightweight command-line tool for managing code snippets, commands, and notes. Built as a personal knowledge vault with password-protected storage for sensitive information.

## ✨ Features

- **Quick Storage**: Save code snippets, commands, links, and notes
- **Tag-Based Organization**: Categorize snippets with tags for easy filtering
- **Smart Search**: Find snippets by keyword in title or tag
- **Password Protection**: Lock sensitive snippets (API keys, tokens) with master password
- **Archive Management**: Archive old snippets without deleting them
- **Unique IDs**: Time-based IDs for easy identification

## 🚀 Quick Start

### Installation

```bash
# Clone or download the project
cd snippet-manager

# Install dependencies (if any)
pip install --break-system-packages -r requirements.txt  # If requirements.txt exists
```

### First-Time Setup

```bash
# Initialize with master password
python main.py init
```

### Basic Usage

```bash
# Add a snippet
python main.py add "Git Reset Hard" "git reset --hard HEAD" --tag git

# List all snippets
python main.py list

# Search snippets
python main.py search docker

# View a snippet
python main.py view 22032026_00001

# Add a locked snippet (password-protected)
python main.py add "API Key" "sk-123456" --tag secrets --access LOCKED
```

## 📋 Requirements

- Python 3.10+
- No external dependencies (uses only Python standard library)

## 🗂️ Project Structure

```
snippet-manager/
├── data/                    # Data files (auto-created)
│   ├── snippets.json       # All snippets
│   ├── config.json         # Master password hash
│   ├── counter.json        # ID counter
│   └── attempts.json       # Login attempts tracking
├── main.py                 # CLI interface
├── snippet_manager.py      # Business logic
├── snippet_entity.py       # Snippet data model
├── storage.py              # Data persistence
├── security.py             # Authentication
├── utils.py                # Utilities (ID gen, hashing)
├── counter_storage.py      # Counter management
├── health_check.py         # System health check
├── README.md               # This file
└── USAGE.md                # Detailed usage guide
```

## 🔐 Security Features

- **Master Password**: SHA-256 hashed password for locked snippets
- **Lockout Protection**: 3 failed attempts → 30 second lockout
- **No Plain Text**: Passwords never stored in plain text
- **Locked Snippets**: Sensitive data requires password to view

## 🎯 Use Cases

- **Developers**: Store frequently used commands, code snippets, git workflows
- **DevOps**: Keep deployment commands, server configs, SSH keys
- **Researchers**: Save notes, links, reference materials
- **Security**: Store API keys, tokens, credentials (with password protection)

## 📚 Documentation

- [USAGE.md](USAGE.md) - Complete command reference and examples
- [health_check.py](health_check.py) - Run system diagnostics

## 🧪 Testing

```bash
# Run health check
python health_check.py
```

## 🛠️ Commands Overview

| Command | Description |
|---------|-------------|
| `init` | First-time setup (create master password) |
| `add` | Add a new snippet |
| `list` | List all active snippets |
| `search` | Search snippets by keyword |
| `view` | View snippet details |
| `archive` | Archive a snippet |
| `unarchive` | Restore archived snippet |
| `lock` | Password-protect a snippet |
| `unlock` | Remove password protection |

For detailed usage, see [USAGE.md](USAGE.md)

## 📊 Data Storage

All data is stored locally in the `data/` directory as JSON files:
- **Portable**: Easy to backup (just copy the data folder)
- **Human-Readable**: JSON format for easy inspection
- **No Database**: Simple file-based storage

## 🔧 Troubleshooting

**Problem: "System not initialized"**
```bash
# Solution: Run init command
python main.py init
```

**Problem: "Account locked"**
```bash
# Solution: Wait 30 seconds and try again
# Or delete data/attempts.json to reset
```

**Problem: "Corrupted data file"**
```bash
# Solution: Check data/ folder for .backup files
# Restore from backup or delete corrupted file
```

## 🤝 Contributing

This is a personal project built for learning. Feel free to fork and customize for your needs!

## 📝 License

MIT License - Use freely for personal or commercial projects.

## 💡 Tips

- Use meaningful tags for better organization
- Lock sensitive snippets immediately
- Archive old snippets to keep lists clean
- Regular backups of `data/` folder recommended
- Use search for quick access instead of scrolling

## 📞 Support

For issues or questions:
1. Check [USAGE.md](USAGE.md) for examples
2. Run `python health_check.py` to diagnose issues
3. Check `data/` folder for backup files

---

**Built with ❤️ using Python**