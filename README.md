# 🌸 Flower Bot

A modern GUI game bot developed in Python with advanced automation features.

## 🚀 Features

- 🎮 Automatic flower/item collection
- 💡 Smart target selection
- 🎯 Center Zone protection (80x80 pixel radius)
- ⌨️ Automatic E-Q camera control
- 📩 Discord Webhook integration
- 🖼️ Modern and user-friendly interface
- 🔄 Auto-retry system with blacklisting
- 🎯 Multi-target support (flowers, chests, trees)
- ⚡ High-performance image recognition
- 🛡️ Anti-ghost click protection

## 📋 Requirements

- Python 3.10+
- PIL (Pillow)
- Tkinter (included with Python)
- Requests

## 🛠️ Installation

1. Install Python 3.10 or higher
2. Install required libraries:
```bash
pip install pillow requests
```
3. Download and extract the project
4. Run `start.py` with administrator privileges

## 📝 Usage

1. Launch the bot
2. Select target window
3. Configure settings
4. Click Start button

## ⚙️ Configuration

- **Max Retries:** Maximum number of failed attempts
- **Herb Timeout:** Waiting time for herb collection
- **Health Timeout:** Waiting time for health regeneration
- **Blacklist Duration:** Duration for failed targets to remain blacklisted
- **Target Type:** Type of item to collect (flower, chest, tree)

## 🔧 Advanced Features

### Center Zone Protection
- Maintains an 80x80 pixel protected radius
- Prevents clicking on ghost items
- Automatically adjusts camera when stuck

### Target Selection
- Smart priority system
- Blacklist management for failed targets
- Automatic retries with configurable limits

### Performance Optimization
- Efficient image processing
- Memory management
- Thread-safe logging

## 🖥️ Interface

The modern GUI includes:
- Real-time statistics
- Status indicators
- Progress tracking
- Configuration panels
- Log viewer
- Discord integration settings

## 📊 Statistics Tracking

Monitors and displays:
- Session duration
- Successful clicks
- Failed attempts
- Total items found
- Verified collections

## ⚠️ Important Notes

- Administrator privileges required
- Add message box images to Templates/message/ directory
- Blacklist clears only after successful collection
- Supports multiple game windows
- Automatic window detection

## 🔍 Technical Details

- Written in Python 3.10+
- Uses Tkinter for GUI
- PIL for image processing
- Thread-safe operation
- Event-driven architecture
- Modular design

## 🔧 Troubleshooting

### Common Issues
- Window not detected: Run as administrator
- Target not found: Check Templates directory
- Performance issues: Adjust timeouts
- Discord notifications: Verify webhook URL

### Performance Tips
- Keep Templates folder organized
- Regular cache clearing
- Optimal timeout settings
- Proper window selection

---

Made with ❤️ by [kazehere4you] 
add me on discord: kazehere4you