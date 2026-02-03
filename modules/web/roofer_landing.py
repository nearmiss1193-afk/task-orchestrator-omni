def get_roofer_landing_html(calendly_url="#", stripe_url="#"):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Service Co | Roofers: Capture Every Storm Lead Instantly.</title>
    <meta name="description" content="When the storm hits, your phone rings off the hook. Don't let 50% of them go to voicemail. Your AI Dispatcher books inspections 24/7.">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏠</text></svg>">
    
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
                    color: "rgb(234, 88, 12)", /* ORANGE for Roofing */
                    type: "pill",
                    title: "Book Inspection",
                    subtitle: "24/7 Live AI",
                    icon: "https://unpkg.com/lucide-static@0.321.0/icons/home.svg"
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
            --red: #ea580c; /* ORANGE for Roofing */
            --red-hover: #c2410c;
            --red-light: #fb923c;
            --red-glow: rgba(234, 88, 12, 0.3);
            --red-subtle: rgba(234, 88, 12, 0.1);
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
                <a href="#features" style="color:var(--gray-light); text-decoration:none;">Features</a>
                <a href="#roi" style="color:var(--gray-light); text-decoration:none;">ROI</a>
                <a href="{calendly_url}" class="btn-primary">Book Demo</a>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <div style="display:inline-block; padding:8px 16px; background:var(--gray-dark); border-radius:50px; font-size:13px; font-weight:600; margin-bottom:24px; color:var(--red-light);">
                🟠 Optimized for Roofing Sales
            </div>
            <h1>
                Capture Every<br>
                <span>Storm Lead Instantly.</span>
            </h1>
            <p>
                When a storm hits, you get 100 calls. You answer 20. We answer the other 80, qualify the insurance claim, and book the inspection on your calendar.
            </p>
            <div style="display:flex; justify-content:center; gap:16px;">
                <a href="{calendly_url}" class="btn-primary" style="font-size:18px; padding:16px 40px;">Get Your Storm AI</a>
                <a href="#" class="btn-primary" style="background:transparent; border:1px solid var(--gray-dark);">Hear a Sample Call ▶</a>
            </div>
        </div>
    </section>

    <section id="features">
        <div class="container">
            <div class="grid-3">
                <div class="card">
                    <div class="icon">🌪️</div>
                    <h3>Storm Surge Capacity</h3>
                    <p>Handle 1,000+ simultaneous calls. Whether it's hailed or just windy, you never miss a lead.</p>
                </div>
                <div class="card">
                    <div class="icon">📋</div>
                    <h3>Insurance Qualification</h3>
                    <p>"Do you have State Farm? When did the damage happen?" The AI asks the right questions before you drive out.</p>
                </div>
                <div class="card">
                    <div class="icon">📍</div>
                    <h3>Geo-Tagging</h3>
                    <p>The AI checks if the lead is in your service area. If they're 2 hours away, it politely declines.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="roi">
        <div class="container" style="text-align:center;">
            <h2>The Math is Simple.</h2>
            <p style="color:var(--gray-light);">One saved roof replacement pays for the software for 5 years.</p>
            
            <div class="grid-3">
                <div class="card">
                    <div class="icon">1</div>
                    <h3>Average Roof Profit</h3>
                    <h2>$3,500</h2>
                    <p>Net profit on a standard shingle replacement.</p>
                </div>
                <div class="card">
                    <div class="icon">2</div>
                    <h3>Missed Calls / Month</h3>
                    <h2>15+</h2>
                    <p>Conservative estimate for a busy season.</p>
                </div>
                <div class="card">
                    <div class="icon">3</div>
                    <h3>Lost Revenue</h3>
                    <h2>$52,500</h2>
                    <p>Money you are literally letting go down the drain.</p>
                </div>
            </div>
        </div>
    </section>

    <footer class="container">
        <p>&copy; 2026 AI Service Co. • Built for High-Performance Roofing Companies.</p>
    </footer>

</body>
</html>
    """
    return html
