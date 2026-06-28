# 🚨 FORENSEEK: Server Connection Refused Error

## ❓ Why does this keep happening?
You are receiving the **"localhost refused to connect"** error because the FastAPI backend server is shutting down. 

When the AI (me) starts the server for you, it runs as a "background task" attached to our current conversation session. If our conversation goes idle for a few minutes while you test the app, the system automatically suspends my session to save memory. When my session goes to sleep, **it forcibly kills the background server I started.**

Because FORENSEEK is a full-stack application (frontend HTML/JS + Python FastAPI backend), the frontend *cannot* work if the backend Python server is dead.

---

## 🛠️ How to permanently resolve it

To fix this so it **never** happens again, you need to run the server in your own terminal rather than relying on me to start it. When *you* run it, it stays alive as long as your computer is on!

Here is how to do it in VS Code:

1. Open **VS Code**.
2. Press `` Ctrl + ` `` (the backtick key near Esc) or go to **Terminal > New Terminal** at the top.
3. Make sure you are inside the `FORENSEEK` folder:
   ```cmd
   cd C:\Users\monish\Desktop\FORENSEEK
   ```
4. Activate the virtual environment:
   ```cmd
   .\venv\Scripts\activate
   ```
5. **Start the server:**
   ```cmd
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

### ✅ Success Indicator
You will know it is working when you see this output in your terminal:
> `INFO: Application startup complete.`
> `INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`

Once you see that, leave that terminal window open! You can now use the app endlessly without it ever refusing to connect.
