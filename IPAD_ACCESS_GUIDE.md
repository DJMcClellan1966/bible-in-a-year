# iPad Access Guide

## ✅ Database Issue Fixed

The database schema has been updated and is now ready to use!

---

## How to Run the App and Access from iPad

### Method 1: Quick Start (Recommended)

1. **Start the Network Server:**
   ```bash
   python run_for_ipad.py
   ```
   
   This will:
   - Start the backend on all network interfaces (0.0.0.0)
   - Show your local IP address
   - Display the URL to access from iPad

2. **On Your iPad:**
   - Make sure iPad is on the **same Wi-Fi network** as your computer
   - Open Safari browser
   - Type the URL shown (e.g., `http://192.168.1.100:8000/static/index.html`)
   - The app will load!

3. **Add to Home Screen (Optional):**
   - Tap the Share button in Safari
   - Select "Add to Home Screen"
   - The app will appear like a native app!

---

### Method 2: Manual Start

1. **Find Your Computer's IP Address:**
   - Windows: Open Command Prompt and type `ipconfig`
   - Look for "IPv4 Address" under your active network adapter
   - Example: `192.168.1.100`

2. **Start the Backend:**
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

3. **Access from iPad:**
   - Open Safari on iPad
   - Go to: `http://YOUR_IP_ADDRESS:8000/static/index.html`
   - Replace `YOUR_IP_ADDRESS` with the IP from step 1

---

## Important Notes

### Network Requirements
- ✅ Both devices must be on the **same Wi-Fi network**
- ✅ Computer must allow incoming connections on port 8000

### Windows Firewall
If iPad can't connect, you may need to allow the connection:

1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Add Python or allow port 8000

Or run PowerShell as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Bible in a Year" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### iPad Safari Settings
- The app works best in Safari
- Make sure JavaScript is enabled
- You may need to allow "Insecure Content" if you see security warnings

---

## Troubleshooting

### Can't Connect from iPad?

1. **Check IP Address:**
   - Make sure you're using the correct IP (run `ipconfig` again)
   - The IP may change if you reconnect to Wi-Fi

2. **Check Firewall:**
   - Temporarily disable Windows Firewall to test
   - If it works, add a firewall rule (see above)

3. **Check Network:**
   - Both devices must be on same network
   - Some corporate/school networks block device-to-device communication

4. **Check Server:**
   - Look at the terminal running the server for errors
   - Try accessing from the computer: `http://127.0.0.1:8000/static/index.html`

5. **Try Different Port:**
   - If port 8000 is blocked, use a different port:
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080
   ```
   - Then access: `http://YOUR_IP:8080/static/index.html`

---

## Features on iPad

✅ All features work on iPad:
- Daily Bible reading
- AI Persona conversations
- Character studies
- Timeline visualization
- Study plans
- Theological profile
- And all other features!

💡 **Tip**: Add to Home Screen for app-like experience!

---

## Security Note

⚠️ **Development/Home Use Only**

This setup makes the app accessible on your local network. For production use, you should:
- Add authentication
- Use HTTPS
- Configure proper firewall rules
- Consider a VPN for remote access

---

## Quick Reference

| Task | Command |
|------|---------|
| Start for iPad | `python run_for_ipad.py` |
| Fix database schema | `python fix_database.py` |
| Find IP address | `ipconfig` (Windows) |
| Manual start | `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000` |
| Access locally | `http://127.0.0.1:8000/static/index.html` |
| Access from iPad | `http://YOUR_IP:8000/static/index.html` |

---

**Enjoy your Bible study on iPad! 📱🙏**
