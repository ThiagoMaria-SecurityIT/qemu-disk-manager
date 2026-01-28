# QEMU Disk Manager - Windows GUI  

A lightweight Python GUI tool for managing QEMU virtual disk files on Windows 11. This is the **starting point** of a larger project to create a comprehensive GUI for QEMU virtualization.
> **Project Timeline**: Starting with virtual disk management (January 2026) with plans to add VM creation, snapshot management, and other QEMU features throughout the year.

<img width="690" height="650" alt="image" src="https://github.com/user-attachments/assets/0e32a83b-8f6a-4c3a-83af-03a80b0d8ba4" />   

## 🚀 Quick Start

### 1. Download & Setup
```bash
# Clone the repository
git clone https://github.com/ThiagoMaria-SecurityIT/qemu-disk-manager.git
cd qemu-disk-manager

# Create virtual environment (recommended)
python -m venv venv

# Activate on Windows
venv\Scripts\activate

```

### 2. Run the Application
```bash
python qemu_disk_manager.py
```

## 📋 Requirements
- **Python 3.6+** (tested with Python 3.9+)
- **QEMU installed** and added to system PATH
  - Download from: [qemu.weilnetz.de/w64/](https://qemu.weilnetz.de/w64/)
  - Add `C:\Program Files\qemu` to your system PATH

## 🖥️ GUI Overview

### Prerequisite: Select a Folder
**All GUI functions require a folder to be selected first.**
1. Click **"Browse Folder"** to select where your virtual disks are (or will be)
2. Use **"Scan Folder"** to automatically find existing `.qcow2` and `.raw` files

### Main Features

#### 1. **Disk Creation**
- Select format: **QCOW2** (recommended) or **RAW**
- Enter size: e.g., `20G`, `50G`, `100G`
- Click **"Create Virtual Disk"**

#### 2. **Disk Management Table**
Displays all virtual disks with columns:
- **Filename** - Name of the disk file
- **Size** - Virtual size (e.g., 20G)
- **Format** - qcow2 or raw
- **Path** - Full file path (may be empty if unavailable)

#### 3. **Action Buttons**
| Button | Purpose |
|--------|---------|
| **Show Full Path** | View complete file path of selected disk |
| **Copy Path to Clipboard** | Copy path for use in QEMU commands |
| **Get Disk Info** | View detailed `qemu-img info` output |
| **Export to CSV** | Save disk list to CSV file |
| **Remove from List** | Remove entry from GUI (does not delete file) |

## 🔧 Key Features
- **Smart Folder Scanning**: Recursively finds QEMU disk files
- **Duplicate Detection**: Prevents adding identical disks (checks filename, size, format, and path)
- **CSV Export**: Export your disk inventory with full path information
- **Path Safety**: Handles missing paths gracefully (empty cells in table)
- **Alternating Row Colors**: Better readability in the table view

## 🤝 Contributing & Feedback

This is an **active development project**! I welcome:

- **Bug reports** and **feature requests**
- **Code contributions** (PRs welcome!)
- **Suggestions** for next QEMU features to implement

**Communication channels:**
- 📧 **Email/Direct Message**: Thisecurapps_767@proton.me
- 💬 **GitHub Issues**: Open an issue for bugs or feature requests
- 🔄 **Pull Requests**: Submit improvements directly

## 🤖 AI Transparency

**Development Approach:**
- **AI-Assisted**: This code was created with the help of **DeepSeek AI**
- **Human-Reviewed**: All code was reviewed, tested, and refined by a human developer
- **Hybrid Process**: AI provided scaffolding and suggestions; human decisions drove architecture and testing

**Why This Matters:**
- Faster prototyping of complex GUI applications
- Consistent code patterns and error handling
- Learning opportunity about QEMU's CLI interface
- All final decisions made by human developer

## 📅 Roadmap 2025

| Quarter | Planned Features |
|---------|-----------------|
| **Q1** | ✅ Virtual Disk Manager (Current) |
| **Q3** | VM Creation Wizard |
| **Q4** | Network Configuration & VM Templates |

## ⚠️ Notes
- This tool **does not delete actual disk files** - only removes them from the GUI list
- Empty "Path" cells mean the application couldn't retrieve the file location
- Always verify important operations with `qemu-img` directly for critical workloads

---

**Repository**: `https://github.com/ThiagoMaria-SecurityIT/qemu-disk-manager`  
**Author**: Thisecur  
**Initial Release**: January 28, 2026  
**License**: MIT
