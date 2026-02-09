# Vapi.ai Setup Guide (Office Manager Agent)

Follow these steps exactly to connect your Voice Agent to the Backend.

## 1. Get Your Tools Configuration

1. Open the file **`vapi_tools_config.json`** in your project folder (or ask me to display it).
2. **Copy** the entire content (the list making up the JSON `[...]`).

## 2. Configure Vapi Dashboard

1. Log in to **[dashboard.vapi.ai](https://dashboard.vapi.ai)**.
2. Go to **Assistants** (Left Sidebar).
3. Click **"Create Assistant"** (or select your existing Office Manager).
4. **Name:** `Office Manager Enterprise`.
5. **Transcriber:** `Deepgram` (recommended for speed) or `Talkstats`.
6. **Model:** `GPT-4o` (or `Claude 3.5 Sonnet`).
7. **System Prompt:**

    ```text
    You are an efficient, professional Office Manager for a busy executive.
    Your job is to manage inventory and take tasks over the phone.
    - If I say "we are out of X", use the check_inventory or update_inventory tool.
    - If I say "remind me to X", use the add_task tool.
    - Be concise. Do not ramble.
    ```

## 3. Connect the Brain (Tools)

1. Scroll down to the **"Tools"** section.
2. Click **"Add Tool"** -> Select **"Function"**.
3. **IMPORTANT:** Look for a place to paste the **JSON Definition**.
    * If there is a visual builder, look for "Edit JSON" or "Schema".
    * Paste the content of `vapi_tools_config.json` into the schema definitions.
4. **Server URL:**
    * You must set the "Server URL" for these tools to your Modal Endpoint:
    * `https://nearmiss1193-afk--ghl-omni-automation-office-voice-tool.modal.run`
    * *Note:* Vapi might ask for a "Server URL" at the Assistant level or Tool level. Set it where requested.

## 4. Test It

1. Click the **"Talk"** button (Microphone icon) in Vapi.
2. Say: *"Check the inventory for paper."*
3. It should hit your backend and reply: *"I couldn't find paper..."*
4. Say: *"Add 50 units of paper to inventory."*
5. It should reply: *"Created new item paper with 50 units."*

**You are now live.**
