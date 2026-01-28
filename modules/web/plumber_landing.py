def get_plumber_landing_html(calendly_url="#", stripe_url="#"):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Service Co | Plumbers: Stop Losing Emergency Jobs to Voicemail.</title>
    <meta name="description" content="80% of plumbing leads go to the first business that answers. Your AI dispatcher answers calls 24/7, quotes leaks instantly, and books jobs while you sleep.">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔧</text></svg>">
    
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
                    color: "rgb(220, 38, 38)", 
                    type: "pill",
                    title: "Emergency Dispatch",
                    subtitle: "24/7 Live AI",
                    icon: "https://unpkg.com/lucide-static@0.321.0/icons/wrench.svg"
                }
            }
          });
      } catch (e) {
          console.error("Vapi Init Failed:", e);
      }
    </script>
    
    <style>
        /* [Copying exact CSS from HVAC Landing to ensure visual consistency] */
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
            --red: #0ea5e9; /* SKY BLUE for Plumbing */
            --red-hover: #0284c7;
            --red-light: #38bdf8;
            --red-glow: rgba(14, 165, 233, 0.3);
            --red-subtle: rgba(14, 165, 233, 0.1);
        }
        
        body { font-family: 'Inter', sans-serif; background: var(--black); color: var(--white); margin: 0; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
        
        /* HEADER */
        header { position: fixed; width: 100%; top: 0; z-index: 1000; background: rgba(0,0,0,0.9); border-bottom: 1px solid var(--gray-dark); padding: 16px 0; backdrop-filter: blur(10px); }
        .header-content { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-weight: 800; font-size: 22px; color: var(--white); text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .logo span { color: var(--red); }
        .btn-primary { background: var(--red); color: var(--white); padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 700; transition: all 0.3s; }
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
                <a href="#how" style="color:var(--gray-light); text-decoration:none;">How it Works</a>
                <a href="#pricing" style="color:var(--gray-light); text-decoration:none;">Pricing</a>
                <a href="{calendly_url}" class="btn-primary">Book Demo</a>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <div style="display:inline-block; padding:8px 16px; background:var(--gray-dark); border-radius:50px; font-size:13px; font-weight:600; margin-bottom:24px; color:var(--red-light);">
                🟢 AI Dispatcher Active • 24/7 Availability
            </div>
            <h1>
                Stop Losing Emergency<br>
                <span>Jobs to Voicemail.</span>
            </h1>
            <p>
                Your new AI Dispatcher answers every call instantly, quotes standard leaks, helps schedule water heater swaps, and texts you the qualified job details.
            </p>
            <div style="display:flex; justify-content:center; gap:16px;">
                <a href="{calendly_url}" class="btn-primary" style="font-size:18px; padding:16px 40px;">Get Your AI Dispatcher</a>
                <a href="#" class="btn-primary" style="background:transparent; border:1px solid var(--gray-dark);">Hear a Sample Call ▶</a>
            </div>
        </div>
    </section>

    <section id="problem">
        <div class="container">
            <div class="grid-3">
                <div class="card">
                    <div class="icon">💸</div>
                    <h3>Missed Calls = Lost Cash</h3>
                    <p>If a pipe bursts at 2 AM, they call until someone answers. If that's not you, you just lost a $2,000 job.</p>
                </div>
                <div class="card">
                    <div class="icon">🥱</div>
                    <h3>Dispatcher Burnout</h3>
                    <p>Paying a human to sit by the phone 24/7 costs $60k/year. Your AI costs less than a single toilet install.</p>
                </div>
                <div class="card">
                    <div class="icon">📉</div>
                    <h3>The "Price Shopper" Trap</h3>
                    <p>Stop wasting time explaining your service fee. Your AI qualifies them before you ever pick up the phone.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="how">
        <div class="container" style="text-align:center;">
            <h2>How It Works</h2>
            <p style="color:var(--gray-light);">Setup takes 24 hours. No technical skills required.</p>
            
            <div class="grid-3">
                <div class="card">
                    <div class="icon">1</div>
                    <h3>We Clone Your Voice</h3>
                    <p>Or choose from our professional dispatchers. We train the AI on your prices and service area.</p>
                </div>
                <div class="card">
                    <div class="icon">2</div>
                    <h3>Forward Your Lines</h3>
                    <p>Set your phone to forward to the AI after 3 rings, or for all after-hours calls.</p>
                </div>
                <div class="card">
                    <div class="icon">3</div>
                    <h3>Wake Up to Jobs</h3>
                    <p>The AI texts you: "Booked John Doe for Water Heater estimate tomorrow at 8 AM."</p>
                </div>
            </div>
        </div>
    </section>

    <footer class="container">
        <p>&copy; 2026 AI Service Co. • Built for High-Performance Plumbing Businesses.</p>
    </footer>

</body>
</html>
    """
    return html
