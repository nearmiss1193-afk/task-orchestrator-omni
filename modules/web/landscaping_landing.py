def get_landscaping_landing_html(calendly_url="#", stripe_url="#"):
    title = "AI Landscaping Scheduler"
    hook = "Grow Your Lawn Care Biz."
    agent_name = "Green Thumb Gary"
    color = "rgb(34, 197, 94)" # Green
    icon = "🌳"
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | AI Service Co</title>
    <script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
    <script>
      var vapiInstance = null;
      try {{
          vapiInstance = window.vapiSDK.run({{
            apiKey: "3b065ff0-a721-4b66-8255-30b6b8d6daab",
            assistant: "c23c884d-0008-4b14-ad5d-530e98d0c9da", 
            config: {{
                idle: {{ color: "{color}", type: "pill", title: "Lawn Quote", subtitle: "{agent_name}", icon: "https://unpkg.com/lucide-static@0.321.0/icons/sprout.svg" }}
            }}
          }});
      }} catch (e) {{ console.error("Vapi Init Failed:", e); }}
    </script>
    <style>
        body {{ background: #0f172a; color: white; font-family: 'Inter', sans-serif; margin: 0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ font-size: 48px; font-weight: 900; line-height: 1.1; margin-bottom: 24px; }}
        .btn {{ background: {color}; color: black; padding: 16px 32px; border-radius: 8px; text-decoration: none; font-weight: 700; display: inline-block; }}
        .highlight {{ color: {color}; }}
    </style>
</head>
<body>
    <div class="container">
        <div style="margin-bottom: 20px; color: {color}; font-weight: 700; text-transform: uppercase;">{icon} {title}</div>
        <h1>{hook} <span class="highlight">Mow More.</span></h1>
        <p style="font-size: 20px; color: #94a3b8; max-width: 600px; margin-bottom: 40px;">
            Stop stopping the mower to answer the phone. {agent_name} quotes recurring maintenance plans and books cleanups while you work.
        </p>
        <a href="{stripe_url}" class="btn">Get Started ($497/mo)</a>
    </div>
</body>
</html>
    """
