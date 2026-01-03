def get_solar_landing_html(calendly_url="#", stripe_url="#"):
    title = "AI Solar Consultant"
    hook = "Scale Your Solar Installs."
    agent_name = "Sunny Sam"
    color = "rgb(250, 204, 21)" # Yellow
    icon = "☀️"
    
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
                idle: {{ color: "{color}", type: "pill", title: "Solar Qualifier", subtitle: "{agent_name}", icon: "https://unpkg.com/lucide-static@0.321.0/icons/sun.svg" }}
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
        <h1>{hook} <span class="highlight">Automated.</span></h1>
        <p style="font-size: 20px; color: #94a3b8; max-width: 600px; margin-bottom: 40px;">
            Qualify leads instantly. {agent_name} checks roof eligibility, credit score, and energy bills on the first call.
        </p>
        <a href="{stripe_url}" class="btn">Start Qualifying ($497/mo)</a>
    </div>
</body>
</html>
    """
