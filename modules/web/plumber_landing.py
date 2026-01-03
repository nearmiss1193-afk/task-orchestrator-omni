def get_plumber_landing_html(calendly_url="#", stripe_url="#"):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Plumber Dispatch | Stop Losing Emergency Jobs</title>
    <meta name="description" content="Plumbers lose $500 emergency jobs to voicemail every night. Our AI Dispatcher answers 24/7, quotes prices, and books jobs instantly.">
    
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
            apiKey: "3b065ff0-a721-4b66-8255-30b6b8d6daab", // Public Key
            assistant: "c23c884d-0008-4b14-ad5d-530e98d0c9da", // Assistant ID (Reusing Office Manager for now)
            config: {
                position: "bottom-right",
                offset: "40px",
                width: "50px",
                height: "50px",
                idle: {
                    color: "rgb(37, 99, 235)", // Plumber Blue
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
        /* ========== CSS RESET & VARIABLES ========== */
        *, *::before, *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --black: #0f172a; /* Slate 900 */
            --black-soft: #1e293b; /* Slate 800 */
            --dark: #020617; /* Slate 950 */
            --dark-card: #1e293b;
            --gray-dark: #334155;
            --gray-mid: #475569;
            --gray: #64748b;
            --gray-light: #94a3b8;
            --gray-lighter: #cbd5e1;
            --white: #ffffff;
            --off-white: #f1f5f9;
            --blue: #2563eb; /* Blue 600 */
            --blue-hover: #1d4ed8;
            --blue-light: #3b82f6;
            --blue-glow: rgba(37, 99, 235, 0.3);
            --blue-subtle: rgba(37, 99, 235, 0.1);
        }
        
        html {
            scroll-behavior: smooth;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--white);
            background: var(--dark);
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }
        
        /* ========== HEADER ========== */
        header {
            background: rgba(2, 6, 23, 0.95);
            backdrop-filter: blur(20px);
            padding: 16px 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid var(--gray-dark);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 22px;
            font-weight: 800;
            color: var(--white);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .logo-icon {
            width: 36px;
            height: 36px;
            background: var(--blue);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .logo span {
            color: var(--blue);
        }
        
        .header-nav {
            display: flex;
            gap: 32px;
            align-items: center;
        }
        
        .header-nav a {
            color: var(--gray-light);
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .header-nav a:hover {
            color: var(--white);
        }
        
        .header-cta-group {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .header-phone {
            color: var(--white);
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 10px 16px;
            border: 1px solid var(--gray-dark);
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .header-phone:hover {
            border-color: var(--blue);
            color: var(--blue);
        }
        
        .header-cta {
            background: var(--blue);
            color: var(--white);
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s;
            border: 2px solid var(--blue);
        }
        
        .header-cta:hover {
            background: var(--blue-hover);
            border-color: var(--blue-hover);
            transform: translateY(-1px);
        }
        
        /* ========== HERO SECTION ========== */
        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 140px 0 100px;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 30%, var(--blue-subtle) 0%, transparent 50%),
                        radial-gradient(circle at 70% 70%, rgba(255,255,255,0.02) 0%, transparent 50%);
            animation: heroGlow 15s ease-in-out infinite alternate;
        }
        
        @keyframes heroGlow {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-5%, -5%) rotate(5deg); }
        }
        
        .hero-content {
            position: relative;
            z-index: 2;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            align-items: center;
        }
        
        .hero-text {
            max-width: 600px;
        }
        
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--black-soft);
            border: 1px solid var(--gray-dark);
            color: var(--gray-light);
            padding: 8px 16px;
            border-radius: 100px;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 24px;
        }
        
        .hero-badge-dot {
            width: 8px;
            height: 8px;
            background: var(--blue);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        .hero h1 {
            font-size: 56px;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 24px;
            letter-spacing: -0.02em;
        }
        
        .hero h1 .highlight {
            color: var(--blue);
            position: relative;
        }
        
        .hero-subtitle {
            font-size: 20px;
            color: var(--gray-light);
            margin-bottom: 16px;
            line-height: 1.6;
        }
        
        .hero-proof {
            font-size: 15px;
            color: var(--gray);
            margin-bottom: 32px;
            padding-left: 16px;
            border-left: 2px solid var(--blue);
        }
        
        .hero-cta-group {
            display: flex;
            gap: 16px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        
        .btn-primary {
            background: var(--blue);
            color: var(--white);
            padding: 16px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 700;
            transition: all 0.3s;
            border: 2px solid var(--blue);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary:hover {
            background: var(--blue-hover);
            border-color: var(--blue-hover);
            transform: translateY(-2px);
            box-shadow: 0 10px 40px var(--blue-glow);
        }
        
        .btn-secondary {
            background: transparent;
            color: var(--white);
            padding: 16px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
            border: 2px solid var(--gray-dark);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-secondary:hover {
            border-color: var(--white);
            background: rgba(255,255,255,0.05);
        }
        
        .hero-trust {
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
        }
        
        .trust-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: var(--gray-light);
        }
        
        .trust-item svg {
            width: 18px;
            height: 18px;
            color: var(--blue);
        }
        
        .hero-stats-card {
            background: var(--black-soft);
            border: 1px solid var(--gray-dark);
            border-radius: 16px;
            padding: 32px;
            position: relative;
            overflow: hidden;
        }
        
        .hero-stats-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--blue), transparent);
        }
        
        .stats-card-title {
            font-size: 14px;
            color: var(--gray);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 24px;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            border-bottom: 1px solid var(--gray-dark);
        }
        
        .stat-row:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: var(--gray-light);
            font-size: 15px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 800;
            color: var(--white);
        }
        
        .stat-value.negative {
            color: #ef4444; /* Red */
        }
        
        .stat-value.positive {
            color: #22c55e;
        }
        
        /* ========== SOLUTION SECTION ========== */
        .solution-section {
            padding: 100px 0;
            background: var(--black-soft);
        }
        
        .section-header {
            text-align: center;
            margin-bottom: 48px;
        }
        
        .section-label {
            display: inline-block;
            background: var(--blue-subtle);
            color: var(--blue);
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
        }
        
        .section-title {
            font-size: 40px;
            font-weight: 800;
            margin-bottom: 16px;
            letter-spacing: -0.02em;
        }
        
        .section-subtitle {
            font-size: 18px;
            color: var(--gray-light);
            max-width: 600px;
            margin: 0 auto;
        }
        
        .solution-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-top: 48px;
        }
        
        .solution-card {
            background: var(--dark);
            border: 1px solid var(--gray-dark);
            border-radius: 16px;
            padding: 32px 24px;
            text-align: center;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .solution-card h3 {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 12px;
            color: var(--white);
        }
        
        .solution-card p {
            color: var(--gray-light);
            font-size: 15px;
        }

        .solution-icon {
            font-size: 40px;
            margin-bottom: 20px;
        }
        
    </style>
</head>
<body>

    <!-- HEADER -->
    <header>
        <div class="container header-content">
            <a href="#" class="logo">
                <div class="logo-icon">🔧</div>
                AI Service Co | <span>Plumber</span>
            </a>
            <nav class="header-nav">
                <a href="#how-it-works">Dispatcher AI</a>
                <a href="#pricing">Pricing</a>
                <a href="#demo">Live Demo</a>
            </nav>
            <div class="header-cta-group">
                <a href="tel:+15550000000" class="header-phone">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                    (555) 000-0000
                </a>
                <a href="{calendly_url}" class="header-cta">Book Demo</a>
            </div>
        </div>
    </header>

    <!-- HERO -->
    <section class="hero">
        <div class="container hero-content">
            <div class="hero-text">
                <div class="hero-badge">
                    <div class="hero-badge-dot"></div>
                    <span>AI Dispatcher Active • 24/7/365</span>
                </div>
                <h1>Stop Losing <span class="highlight">$500</span> Emergency Jobs to Voicemail.</h1>
                <p class="hero-subtitle">
                    Your current process misses 30% of calls. Dispatch Dan answers instantly, quotes leak repairs, and books jobs directly into ServiceTitan.
                </p>
                <div class="hero-proof">
                    "We saved 12 jobs last weekend alone. That's $6k in pure profit." - <strong>Mike's Plumbing (Tampa)</strong>
                </div>
                <div class="hero-cta-group">
                    <a href="{stripe_url}" class="btn-primary">Get Started ($497/mo)</a>
                    <a href="#demo" class="btn-secondary">Test the AI</a>
                </div>
                <div class="hero-trust">
                    <div class="trust-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        Simulates ServiceTitan
                    </div>
                    <div class="trust-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        Instant SMS Follow-up
                    </div>
                </div>
            </div>
            
            <div class="hero-visual">
                <div class="hero-stats-card">
                    <div class="stats-card-title">Live Dispatch Metrics</div>
                    
                    <div class="stat-row">
                        <span class="stat-label">Missed Call Rate</span>
                        <div class="stat-value negative">28% <span style="font-size: 14px; font-weight: 500; color: #64748b;">(Human)</span></div>
                    </div>
                    
                    <div class="stat-row">
                        <span class="stat-label">AI Pickup Rate</span>
                        <div class="stat-value positive">100% <span style="font-size: 14px; font-weight: 500; color: #64748b;">(Instant)</span></div>
                    </div>
                    
                    <div class="stat-row">
                        <span class="stat-label">Jobs Rescued (Wk)</span>
                        <div class="stat-value">14 <span style="font-size: 14px; font-weight: 500; color: #64748b; color: #22c55e;">(+$7,400)</span></div>
                    </div>
                    
                    <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--gray-dark); font-size: 13px; color: var(--gray);">
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                            <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%;"></div>
                            Dispatch Dan just booked a Water Heater in Austin, TX
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%;"></div>
                            Dispatch Dan just quoted a Leak Detection in Miami, FL
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- FEATURES -->
    <section class="solution-section">
        <div class="container">
            <div class="section-header">
                <span class="section-label">Automated Dispatch</span>
                <h2 class="section-title">Your New Best Employee</h2>
                <p class="section-subtitle">Dispatch Dan handles the phones so your techs can turn wrenches.</p>
            </div>
            
            <div class="solution-grid">
                <div class="solution-card">
                    <div class="solution-icon">🚑</div>
                    <h3>Emergency Triage</h3>
                    <p>Dan identifies emergencies vs routine calls. "Is water actively flooding?" -> Routes to On-Call Tech immediately.</p>
                </div>
                <div class="solution-card">
                    <div class="solution-icon">📅</div>
                    <h3>Smart Scheduling</h3>
                    <p>Books appointments directly into your calendar based on technician availability and job type.</p>
                </div>
                <div class="solution-card">
                    <div class="solution-icon">💰</div>
                    <h3>Price Estimates</h3>
                    <p>Gives ballpark ranges for common items (Water Heaters, Toilets) to filter out price shoppers automatically.</p>
                </div>
            </div>
        </div>
    </section>

</body>
</html>
    """
    return html
