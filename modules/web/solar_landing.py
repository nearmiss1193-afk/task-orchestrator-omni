def get_solar_landing_html(calendly_url="#", stripe_url="#"):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Service Co | Solar: Qualify Leads While You Sleep.</title>
    <meta name="description" content="Stop calling leads who can't afford solar. Your AI Dispatcher qualifies homeowners, checks shade, and books appointments only for decision makers.">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>☀️</text></svg>">
    
    <!-- Vapi Voice Widget -->
    <script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
    <script>
      var vapiInstance = null;
      try {
          vapiInstance = window.vapiSDK.run({
            apiKey: "3b065ff0-a721-4b66-8255-30b6b8d6daab", 
            assistant: "c23c884d-0008-4b14-ad5d-530e98d0c9da", 
            config: {
                position: "bottom-right",
                offset: "40px",
                width: "50px",
                height: "50px",
                idle: {
                    color: "rgb(234, 179, 8)", /* YELLOW for Solar */
                    type: "pill",
                    title: "Solar Qualifier",
                    subtitle: "Get Your Savings",
                    icon: "https://unpkg.com/lucide-static@0.321.0/icons/sun.svg"
                }
            }
          });
      } catch (e) {
          console.error("Vapi Init Failed:", e);
      }
    </script>
    
    <style>
        :root {
            --black: #000000;
            --black-soft: #0a0a0a;
            --dark: #111111;
            --dark-card: #161616;
            --gray-dark: #222222;
            --gray-mid: #333333;
            --gray: #666666;
            --gray-light: #999999;
            --gray-lighter: #cccccc;
            --white: #ffffff;
            --red: #eab308; /* YELLOW for Solar */
            --red-hover: #ca8a04;
            --red-light: #fcd34d;
            --red-glow: rgba(234, 179, 8, 0.3);
            --red-subtle: rgba(234, 179, 8, 0.1);
        }
        
        body { font-family: 'Inter', sans-serif; background: var(--black); color: var(--white); margin: 0; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
        
        /* HEADER */
        header { position: fixed; width: 100%; top: 0; z-index: 1000; background: rgba(0,0,0,0.9); border-bottom: 1px solid var(--gray-dark); padding: 16px 0; backdrop-filter: blur(10px); }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-weight: 800; font-size: 22px; color: var(--white); text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .logo span { color: var(--red); }
        .btn-primary { background: var(--red); color: var(--black); padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 700; transition: all 0.3s; }
        .btn-primary:hover { background: var(--red-hover); transform: translateY(-2px); box-shadow: 0 10px 20px var(--red-glow); }

        /* HERO */
        .hero { padding: 180px 0 100px; text-align: center; position: relative; overflow: hidden; }
        .hero h1 { font-size: 64px; font-weight: 900; line-height: 1.1; margin-bottom: 24px; }
        .hero h1 span { color: var(--red); }
        .hero p { font-size: 20px; color: var(--gray-light); max-width: 700px; margin: 0 auto 40px; }
        
        /* SECTIONS */
        section { padding: 100px 0; border-bottom: 1px solid var(--gray-dark); }
        h2 { font-size: 40px; font-weight: 800; margin-bottom: 16px; }
        
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; margin-top: 48px; }
        .card { background: var(--dark-card); border: 1px solid var(--gray-dark); padding: 32px; border-radius: 16px; transition: 0.3s; }
        .card:hover { border-color: var(--red); transform: translateY(-5px); }
        .icon { font-size: 32px; margin-bottom: 20px; color: var(--red); }
        
        /* FOOTER */
        footer { padding: 60px 0; text-align: center; color: var(--gray); font-size: 14px; }
    </style>
</head>
<body>

    <header>
        <div class="container header-content">
            <a href="#" class="logo"><span>AI</span> Service Co.</a>
            <div style="display:flex; gap:20px; align-items:center;">
                <a href="#process" style="color:var(--gray-light); text-decoration:none;">Process</a>
                <a href="#savings" style="color:var(--gray-light); text-decoration:none;">Savings</a>
                <a href="{calendly_url}" class="btn-primary">Book Demo</a>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <div style="display:inline-block; padding:8px 16px; background:var(--gray-dark); border-radius:50px; font-size:13px; font-weight:600; margin-bottom:24px; color:var(--red-light);">
                🟡 Intelligent Solar Sales
            </div>
            <h1>
                Qualify Leads<br>
                <span>While You Sleep.</span>
            </h1>
            <p>
                Stop chasing homeowners with $80 electric bills. Your AI Dispatcher qualifies credit, shade, and energy usage before you ever knock on the door.
            </p>
            <div style="display:flex; justify-content:center; gap:16px;">
                <a href="{calendly_url}" class="btn-primary" style="font-size:18px; padding:16px 40px;">Get Your Solar AI</a>
                <a href="#" class="btn-primary" style="background:transparent; border:1px solid var(--gray-dark); color:var(--white);">Compare ROI ▶</a>
            </div>
        </div>
    </section>

    <section id="process">
        <div class="container">
            <div class="grid-3">
                <div class="card">
                    <div class="icon">🔌</div>
                    <h3>Bill Analysis</h3>
                    <p>"Is your average bill over $150?" The AI filters out the non-buyers instantly.</p>
                </div>
                <div class="card">
                    <div class="icon">☀️</div>
                    <h3>Roof Suitability</h3>
                    <p>It checks for tree coverage and roof age by asking the homeowner directly.</p>
                </div>
                <div class="card">
                    <div class="icon">📅</div>
                    <h3>Appointment Setting</h3>
                    <p>It books a "Kitchen Table Close" directly on your sales rep's Google Calendar.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="savings">
        <div class="container" style="text-align:center;">
            <h2>Stop Buying Bad Leads.</h2>
            <p style="color:var(--gray-light);">The AI costs less than 2 leads from Angi.</p>
            
            <div class="grid-3">
                <div class="card">
                    <div class="icon">1</div>
                    <h3>Cost Per Lead</h3>
                    <h2>$0.50</h2>
                    <p>Using AI to call your aged data.</p>
                </div>
                <div class="card">
                    <div class="icon">2</div>
                    <h3>Set Rate</h3>
                    <h2>15%</h2>
                    <p>From cold data to booked appointment.</p>
                </div>
                <div class="card">
                    <div class="icon">3</div>
                    <h3>Your ROI</h3>
                    <h2>40x</h2>
                    <p>Unmatched in the industry.</p>
                </div>
            </div>
        </div>
    </section>

    <footer class="container">
        <p>&copy; 2026 AI Service Co. • Built for Modern Solar Teams.</p>
    </footer>

</body>
</html>
    """
    return html
