def get_hvac_landing_html(calendly_url="#", stripe_url="#"):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Service Co | 80% of Businesses Fail. Yours Won't.</title>
    <meta name="description" content="80% of service businesses fail from missed calls, ignored texts, and forgotten customers. Your AI answers 24/7, follows up automatically, and never forgets. Setup in 24 hours.">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>¤–</text></svg>">
    
    <!-- Vapi Voice Widget -->
    <script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
    <script>
      var vapiInstance = null;
      try {
          vapiInstance = window.vapiSDK.run({
            apiKey: "3b065ff0-a721-4b66-8255-30b6b8d6daab", // Public Key
            assistant: "c23c884d-0008-4b14-ad5d-530e98d0c9da", // Assistant ID (from Config/Env)
            config: {
                position: "bottom-right",
                offset: "40px",
                width: "50px",
                height: "50px",
                idle: {
                    color: "rgb(220, 38, 38)", // Brand Red
                    type: "pill",
                    title: "Speak with AI",
                    subtitle: "24/7 Support",
                    icon: "https://unpkg.com/lucide-static@0.321.0/icons/phone.svg"
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
            --off-white: #f5f5f5;
            --red: #dc2626;
            --red-hover: #b91c1c;
            --red-light: #ef4444;
            --red-glow: rgba(220, 38, 38, 0.3);
            --red-subtle: rgba(220, 38, 38, 0.1);
        }
        
        html {
            scroll-behavior: smooth;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--white);
            background: var(--black);
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
        }
        
        /* ========== HEADER ========== */
        header {
            background: rgba(0, 0, 0, 0.95);
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
            background: var(--red);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .logo span {
            color: var(--red);
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
            border-color: var(--red);
            color: var(--red);
        }
        
        .header-cta {
            background: var(--red);
            color: var(--white);
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s;
            border: 2px solid var(--red);
        }
        
        .header-cta:hover {
            background: var(--red-hover);
            border-color: var(--red-hover);
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
            background: radial-gradient(circle at 30% 30%, var(--red-subtle) 0%, transparent 50%),
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
            background: var(--dark);
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
            background: var(--red);
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
            color: var(--red);
            position: relative;
        }
        
        .hero h1 .money {
            color: var(--red);
            font-weight: 900;
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
            border-left: 2px solid var(--red);
        }
        
        .hero-cta-group {
            display: flex;
            gap: 16px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        
        .btn-primary {
            background: var(--red);
            color: var(--white);
            padding: 16px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 700;
            transition: all 0.3s;
            border: 2px solid var(--red);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary:hover {
            background: var(--red-hover);
            border-color: var(--red-hover);
            transform: translateY(-2px);
            box-shadow: 0 10px 40px var(--red-glow);
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
            color: var(--red);
        }
        
        .hero-visual {
            position: relative;
        }
        
        .hero-stats-card {
            background: var(--dark);
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
            background: linear-gradient(90deg, var(--red), transparent);
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
            color: var(--red);
        }
        
        .stat-value.positive {
            color: #22c55e;
        }
        
        /* ========== VIDEO SECTION ========== */
        .video-section {
            padding: 100px 0;
            background: var(--dark);
            position: relative;
        }
        
        .video-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--gray-dark), transparent);
        }
        
        .section-header {
            text-align: center;
            margin-bottom: 48px;
        }
        
        .section-label {
            display: inline-block;
            background: var(--red-subtle);
            color: var(--red);
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
        
        .video-wrapper {
            max-width: 900px;
            margin: 0 auto;
            position: relative;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--gray-dark);
            background: var(--black);
        }
        
        .video-placeholder {
            width: 100%;
            aspect-ratio: 16/9;
            background: linear-gradient(135deg, var(--dark) 0%, var(--black) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--gray);
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .video-placeholder:hover {
            background: linear-gradient(135deg, var(--gray-dark) 0%, var(--dark) 100%);
        }
        
        .video-play-btn {
            width: 80px;
            height: 80px;
            background: var(--red);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
            transition: all 0.3s;
        }
        
        .video-placeholder:hover .video-play-btn {
            transform: scale(1.1);
            box-shadow: 0 0 40px var(--red-glow);
        }
        
        .video-play-btn svg {
            width: 32px;
            height: 32px;
            color: var(--white);
            margin-left: 4px;
        }
        
        .video-wrapper iframe {
            width: 100%;
            aspect-ratio: 16/9;
            border: none;
        }
        
        /* ========== PROBLEM SECTION ========== */
        .problem-section {
            padding: 100px 0;
            background: var(--black);
        }
        
        .problem-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            align-items: center;
        }
        
        .problem-content h2 {
            font-size: 40px;
            font-weight: 800;
            margin-bottom: 24px;
            line-height: 1.2;
        }
        
        .problem-content h2 span {
            color: var(--red);
        }
        
        .problem-content > p {
            font-size: 18px;
            color: var(--gray-light);
            margin-bottom: 32px;
            line-height: 1.7;
        }
        
        .problem-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .problem-stat {
            background: var(--dark);
            border: 1px solid var(--gray-dark);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        }
        
        .problem-stat-number {
            font-size: 36px;
            font-weight: 900;
            color: var(--red);
            margin-bottom: 8px;
        }
        
        .problem-stat-label {
            font-size: 14px;
            color: var(--gray-light);
        }
        
        .problem-cards {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .problem-card {
            background: var(--dark);
            border: 1px solid var(--gray-dark);
            border-radius: 12px;
            padding: 24px;
            display: flex;
            gap: 16px;
            align-items: flex-start;
            transition: all 0.3s;
        }
        
        .problem-card:hover {
            border-color: var(--red);
            transform: translateX(8px);
        }
        
        .problem-card-icon {
            width: 48px;
            height: 48px;
            background: var(--red-subtle);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        }
        
        .problem-card h4 {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 6px;
            color: var(--white);
        }
        
        .problem-card p {
            font-size: 14px;
            color: var(--gray);
            line-height: 1.6;
        }
        
        /* ========== SOLUTION SECTION ========== */
        .solution-section {
            padding: 100px 0;
            background: var(--dark);
        }
        
        .solution-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
            margin-top: 48px;
        }
        
        .solution-card {
            background: var(--black);
            border: 1px solid var(--gray-dark);
            border-radius: 16px;
            padding: 32px 24px;
            text-align: center;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .solution-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--red);
            transform: scaleX(0);
            transition: transform 0.3s;
        }
        
        .solution-card:hover {
            border-color: var(--red);
            transform: translateY(-8px);
        }
        
        .solution-card:hover::before {
            transform: scaleX(1);
        }
        
        .solution-icon {
            width: 64px;
            height: 64px;
            background: var(--red-subtle);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 20px;
        }
        
        .solution-card h3 {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--white);
        }
        
        .solution-card .agent-name {
            font-size: 12px;
            color: var(--red);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }
        
        .solution-card p {
            font-size: 14px;
            color: var(--gray-light);
            line-height: 1.6;
        }
        
        .solution-status {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 100px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .solution-status.live {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
        }
        
        .solution-status.ready {
            background: rgba(234, 179, 8, 0.2);
            color: #eab308;
        }
        
        /* ========== PRICING SECTION ========== */
        .pricing-section {
            padding: 100px 0;
            background: var(--black);
        }
        
        .pricing-toggle {
            display: flex;
            justify-content: center;
            gap: 16px;
            align-items: center;
            margin-bottom: 48px;
        }
        
        .pricing-toggle span {
            font-size: 14px;
            color: var(--gray);
        }
        
        .pricing-toggle span.active {
            color: var(--white);
        }
        
        .toggle-switch {
            width: 56px;
            height: 28px;
            background: var(--gray-dark);
            border-radius: 100px;
            position: relative;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .toggle-switch.active {
            background: var(--red);
        }
        
        .toggle-switch::after {
            content: '';
            width: 22px;
            height: 22px;
            background: var(--white);
            border-radius: 50%;
            position: absolute;
            top: 3px;
            left: 3px;
            transition: transform 0.3s;
        }
        
        .toggle-switch.active::after {
            transform: translateX(28px);
        }
        
        .save-badge {
            background: var(--red);
            color: var(--white);
            padding: 4px 10px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            align-items: stretch;
        }
        
        .pricing-card {
            background: var(--dark);
            border: 1px solid var(--gray-dark);
            border-radius: 16px;
            padding: 32px 24px;
            display: flex;
            flex-direction: column;
            position: relative;
            transition: all 0.3s;
        }
        
        .pricing-card:hover {
            border-color: var(--gray-mid);
            transform: translateY(-4px);
        }
        
        .pricing-card.featured {
            border-color: var(--red);
            background: linear-gradient(180deg, var(--red-subtle) 0%, var(--dark) 100%);
        }
        
        .pricing-card.featured:hover {
            border-color: var(--red);
        }
        
        .pricing-card.enterprise {
            background: linear-gradient(135deg, var(--dark) 0%, var(--gray-dark) 100%);
        }
        
        .pricing-badge {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--red);
            color: var(--white);
            padding: 6px 16px;
            border-radius: 100px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }
        
        .pricing-header {
            text-align: center;
            margin-bottom: 24px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--gray-dark);
        }
        
        .pricing-name {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .pricing-tagline {
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 16px;
        }
        
        .pricing-price {
            display: flex;
            align-items: baseline;
            justify-content: center;
            gap: 4px;
        }
        
        .pricing-currency {
            font-size: 24px;
            font-weight: 700;
            color: var(--gray-light);
        }
        
        .pricing-amount {
            font-size: 48px;
            font-weight: 900;
            color: var(--white);
            line-height: 1;
        }
        
        .pricing-period {
            font-size: 14px;
            color: var(--gray);
        }
        
        .pricing-annual {
            font-size: 13px;
            color: var(--gray);
            margin-top: 8px;
        }
        
        .pricing-annual span {
            color: var(--red);
            font-weight: 600;
        }
        
        .pricing-features {
            flex: 1;
            margin-bottom: 24px;
        }
        
        .pricing-features ul {
            list-style: none;
        }
        
        .pricing-features li {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 10px 0;
            font-size: 13px;
            color: var(--gray-light);
            border-bottom: 1px solid var(--gray-dark);
        }
        
        .pricing-features li:last-child {
            border-bottom: none;
        }
        
        .pricing-features li svg {
            width: 16px;
            height: 16px;
            color: var(--red);
            flex-shrink: 0;
            margin-top: 2px;
        }
        
        .pricing-features li.disabled {
            color: var(--gray);
            text-decoration: line-through;
            opacity: 0.5;
        }
        
        .pricing-features li.disabled svg {
            color: var(--gray);
        }
        
        .pricing-btn {
            width: 100%;
            padding: 14px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            text-decoration: none;
            display: block;
        }
        
        .pricing-btn.primary {
            background: var(--red);
            color: var(--white);
            border: 2px solid var(--red);
        }
        
        .pricing-btn.primary:hover {
            background: var(--red-hover);
            border-color: var(--red-hover);
        }
        
        .pricing-btn.secondary {
            background: transparent;
            color: var(--white);
            border: 2px solid var(--gray-dark);
        }
        
        .pricing-btn.secondary:hover {
            border-color: var(--white);
        }
        
        /* ========== HOW IT WORKS ========== */
        .how-section {
            padding: 100px 0;
            background: var(--dark);
        }
        
        .how-steps {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 40px;
            margin-top: 48px;
            position: relative;
        }
        
        .how-steps::before {
            content: '';
            position: absolute;
            top: 48px;
            left: 15%;
            right: 15%;
            height: 2px;
            background: var(--gray-dark);
        }
        
        .how-step {
            text-align: center;
            position: relative;
        }
        
        .step-number {
            width: 96px;
            height: 96px;
            background: var(--black);
            border: 2px solid var(--gray-dark);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: 900;
            color: var(--red);
            margin: 0 auto 24px;
            position: relative;
            z-index: 1;
        }
        
        .how-step h3 {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        .how-step p {
            font-size: 15px;
            color: var(--gray-light);
            line-height: 1.7;
            max-width: 280px;
            margin: 0 auto;
        }
        
        /* ========== TESTIMONIALS ========== */
        .testimonials-section {
            padding: 100px 0;
            background: var(--black);
        }
        
        .testimonials-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-top: 48px;
        }
        
        .testimonial-card {
            background: var(--dark);
            border: 1px solid var(--gray-dark);
            border-radius: 16px;
            padding: 32px;
            transition: all 0.3s;
        }
        
        .testimonial-card:hover {
            border-color: var(--gray-mid);
            transform: translateY(-4px);
        }
        
        .testimonial-stars {
            color: var(--red);
            font-size: 18px;
            margin-bottom: 16px;
            letter-spacing: 2px;
        }
        
        .testimonial-text {
            font-size: 15px;
            color: var(--gray-lighter);
            line-height: 1.8;
            margin-bottom: 24px;
        }
        
        .testimonial-author {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .testimonial-avatar {
            width: 48px;
            height: 48px;
            background: var(--red-subtle);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 700;
            color: var(--red);
        }
        
        .testimonial-info h4 {
            font-size: 15px;
            font-weight: 600;
            color: var(--white);
        }
        
        .testimonial-info p {
            font-size: 13px;
            color: var(--gray);
        }
        
        /* ========== CONTACT SECTION ========== */
        .contact-section {
            padding: 100px 0;
            background: var(--dark);
        }
        
        .contact-grid {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 48px;
            align-items: start;
        }
        
        .contact-info {
            background: var(--red);
            border-radius: 16px;
            padding: 40px;
            color: var(--white);
        }
        
        .contact-info h3 {
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 16px;
        }
        
        .contact-info > p {
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 32px;
            line-height: 1.7;
        }
        
        .contact-methods {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 32px;
        }
        
        .contact-method {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .contact-method-icon {
            width: 48px;
            height: 48px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .contact-method a {
            color: var(--white);
            text-decoration: none;
            font-size: 18px;
            font-weight: 600;
        }
        
        .contact-method span {
            display: block;
            font-size: 13px;
            opacity: 0.8;
            font-weight: 400;
        }
        
        .contact-guarantee {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
        }
        
        .contact-guarantee h4 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        
        .contact-guarantee ul {
            list-style: none;
        }
        
        .contact-guarantee li {
            font-size: 14px;
            padding: 6px 0;
            opacity: 0.9;
        }
        
        .contact-form-wrapper {
            background: var(--black);
            border: 1px solid var(--gray-dark);
            border-radius: 16px;
            overflow: hidden;
            min-height: 500px;
        }
        
        /* ========== FINAL CTA ========== */
        .final-cta {
            padding: 120px 0;
            background: var(--black);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .final-cta::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, var(--red-subtle) 0%, transparent 70%);
        }
        
        .final-cta-content {
            position: relative;
            z-index: 1;
        }
        
        .final-cta h2 {
            font-size: 48px;
            font-weight: 900;
            margin-bottom: 20px;
            line-height: 1.2;
        }
        
        .final-cta h2 span {
            color: var(--red);
        }
        
        .final-cta > .container > p {
            font-size: 20px;
            color: var(--gray-light);
            margin-bottom: 40px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .final-cta-btns {
            display: flex;
            gap: 16px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        /* ========== FOOTER ========== */
        footer {
            background: var(--dark);
            padding: 60px 0 30px;
            border-top: 1px solid var(--gray-dark);
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 48px;
            margin-bottom: 48px;
        }
        
        .footer-brand h3 {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .footer-brand h3 span {
            color: var(--red);
        }
        
        .footer-brand p {
            font-size: 14px;
            color: var(--gray-light);
            line-height: 1.8;
            max-width: 300px;
        }
        
        .footer-links h4 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--white);
        }
        
        .footer-links a {
            display: block;
            color: var(--gray-light);
            text-decoration: none;
            font-size: 14px;
            padding: 8px 0;
            transition: color 0.3s;
        }
        
        .footer-links a:hover {
            color: var(--red);
        }
        
        .footer-bottom {
            padding-top: 24px;
            border-top: 1px solid var(--gray-dark);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .footer-bottom p {
            font-size: 13px;
            color: var(--gray);
        }
        
        .footer-legal {
            display: flex;
            gap: 24px;
        }
        
        .footer-legal a {
            font-size: 13px;
            color: var(--gray);
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .footer-legal a:hover {
            color: var(--white);
        }
        
        /* ========== FUNNEL MODAL ========== */
        .funnel-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.95);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .funnel-overlay.active {
            display: flex;
        }
        
        .funnel-container {
            background: var(--dark);
            border: 1px solid var(--gray-dark);
            border-radius: 20px;
            max-width: 560px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
        }
        
        .funnel-close {
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--gray-dark);
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            font-size: 20px;
            cursor: pointer;
            color: var(--gray-light);
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
        }
        
        .funnel-close:hover {
            background: var(--red);
            color: var(--white);
        }
        
        .funnel-step {
            display: none;
            padding: 48px 40px;
        }
        
        .funnel-step.active {
            display: block;
        }
        
        .funnel-progress {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 32px;
        }
        
        .progress-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--gray-dark);
            transition: all 0.3s;
        }
        
        .progress-dot.active {
            background: var(--red);
            width: 32px;
            border-radius: 5px;
        }
        
        .progress-dot.completed {
            background: var(--red);
        }
        
        .funnel-step h3 {
            font-size: 28px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 12px;
            line-height: 1.3;
        }
        
        .funnel-step h3 span {
            color: var(--red);
        }
        
        .funnel-step > p {
            text-align: center;
            color: var(--gray);
            margin-bottom: 32px;
            font-size: 15px;
        }
        
        .funnel-options {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .funnel-option {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 18px 20px;
            border: 2px solid var(--gray-dark);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            background: var(--black);
        }
        
        .funnel-option:hover {
            border-color: var(--red);
            background: var(--red-subtle);
        }
        
        .funnel-option-icon {
            width: 48px;
            height: 48px;
            background: var(--gray-dark);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        }
        
        .funnel-option:hover .funnel-option-icon {
            background: var(--red);
        }
        
        .funnel-option-text h4 {
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 4px;
            color: var(--white);
        }
        
        .funnel-option-text p {
            font-size: 13px;
            color: var(--gray);
            margin: 0;
        }
        
        .funnel-other-input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid var(--gray-dark);
            border-radius: 12px;
            background: var(--black);
            color: var(--white);
            font-size: 15px;
            font-family: inherit;
            transition: all 0.3s;
            margin-top: 8px;
        }
        
        .funnel-other-input:focus {
            outline: none;
            border-color: var(--red);
        }
        
        .funnel-other-input::placeholder {
            color: var(--gray);
        }
        
        .funnel-other-submit {
            margin-top: 12px;
            width: 100%;
            padding: 14px;
            background: var(--red);
            color: var(--white);
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: none;
        }
        
        .funnel-other-submit.visible {
            display: block;
        }
        
        .funnel-other-submit:hover {
            background: var(--red-hover);
        }
        
        .funnel-back {
            background: none;
            border: none;
            color: var(--gray);
            cursor: pointer;
            font-size: 14px;
            margin-top: 24px;
            display: flex;
            align-items: center;
            gap: 6px;
            margin-left: auto;
            margin-right: auto;
            transition: color 0.3s;
        }
        
        .funnel-back:hover {
            color: var(--white);
        }
        
        .funnel-form-container {
            background: var(--black);
            border-radius: 12px;
            overflow: hidden;
            min-height: 450px;
        }
        
        .funnel-contact-cards {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .funnel-contact-card {
            background: var(--black);
            border: 1px solid var(--gray-dark);
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s;
        }
        
        .funnel-contact-card:hover {
            border-color: var(--red);
        }
        
        .funnel-contact-card h4 {
            font-size: 16px;
            margin-bottom: 8px;
            color: var(--white);
        }
        
        .funnel-contact-card a {
            color: var(--red);
            text-decoration: none;
            font-size: 20px;
            font-weight: 700;
        }
        
        .funnel-contact-card p {
            color: var(--gray);
            font-size: 13px;
            margin-top: 8px;
        }
        
        /* ========== RESPONSIVE ========== */
        @media (max-width: 1200px) {
            .pricing-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            
            .pricing-card:nth-child(4),
            .pricing-card:nth-child(5) {
                grid-column: span 1;
            }
        }
        
        @media (max-width: 992px) {
            .header-nav {
                display: none;
            }
            
            .hero-content {
                grid-template-columns: 1fr;
                text-align: center;
            }
            
            .hero-text {
                max-width: 100%;
            }
            
            .hero h1 {
                font-size: 42px;
            }
            
            .hero-cta-group {
                justify-content: center;
            }
            
            .hero-trust {
                justify-content: center;
            }
            
            .hero-visual {
                max-width: 500px;
                margin: 0 auto;
            }
            
            .problem-grid {
                grid-template-columns: 1fr;
            }
            
            .solution-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .pricing-grid {
                grid-template-columns: 1fr;
                max-width: 400px;
                margin: 0 auto;
            }
            
            .how-steps {
                grid-template-columns: 1fr;
                gap: 48px;
            }
            
            .how-steps::before {
                display: none;
            }
            
            .testimonials-grid {
                grid-template-columns: 1fr;
            }
            
            .contact-grid {
                grid-template-columns: 1fr;
            }
            
            .footer-content {
                grid-template-columns: 1fr 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .header-cta-group {
                display: none;
            }
            
            .hero {
                padding: 120px 0 80px;
            }
            
            .hero h1 {
                font-size: 32px;
            }
            
            .hero-subtitle {
                font-size: 17px;
            }
            
            .section-title {
                font-size: 32px;
            }
            
            .solution-grid {
                grid-template-columns: 1fr;
            }
            
            .final-cta h2 {
                font-size: 32px;
            }
            
            .footer-content {
                grid-template-columns: 1fr;
                gap: 32px;
            }
            
            .footer-bottom {
                flex-direction: column;
                gap: 16px;
                text-align: center;
            }
            
            .funnel-step {
                padding: 32px 24px;
            }
            
            .funnel-step h3 {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
<!-- BODY_GOES_HERE -->
    
    <!-- ========== HEADER ========== -->
    <header>
        <div class="container header-content">
            <a href="#" class="logo">
                <div class="logo-icon">¤–</div>
                AI Service<span>Co</span>
            </a>
            
            <nav class="header-nav">
                <a href="#problem">The Problem</a>
                <a href="#solution">The Solution</a>
                <a href="#pricing">Pricing</a>
                <a href="#how-it-works">How It Works</a>
                <a href="#reviews">Reviews</a>
            </nav>
            
            <div class="header-cta-group">
                <a href="tel:+18555983794" class="header-phone">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                    (855) 598-3794
                </a>
                <a href="#" class="header-cta" onclick="openFunnel()">Get Started</a>
            </div>
        </div>
    </header>
    
    <!-- ========== HERO ========== -->
    <section class="hero">
        <div class="container hero-content">
            <div class="hero-text">
                <div class="hero-badge">
                    <div class="hero-badge-dot"></div>
                    <span>AI-Powered Growth Engine v2.0</span>
                </div>
                
                <h1>80% of Businesses Fail. <span class="highlight">Yours Won't.</span></h1>
                
                <p class="hero-subtitle">
                    Missed calls kill service businesses. Our AI answers 24/7, books jobs, and reactivates dead leads. Stop bleeding revenue today.
                </p>
                
                <div class="hero-proof">
                    "We recovered <span class="money">$12,400</span> in lost revenue in the first 7 days."
                </div>
                
                <div class="hero-cta-group">
                    <button class="btn-primary" onclick="openFunnel()">
                        Start Winning
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                    </button>
                    <a href="#how-it-works" class="btn-secondary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polygon points="10 8 16 12 10 16"></polygon></svg>
                        See It In Action
                    </a>
                </div>
                
                <div class="hero-trust">
                    <div class="trust-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                        <span>5.0 Star Rating</span>
                    </div>
                    <div class="trust-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                        <span>Data Encrypted</span>
                    </div>
                    <div class="trust-item">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        <span>24/7 Uptime</span>
                    </div>
                </div>
            </div>
            
            <div class="hero-visual">
                <div class="hero-stats-card">
                    <div class="stats-card-title">LIVE PERFORMANCE</div>
                    
                    <div class="stat-row">
                        <div class="stat-label">Missed Calls</div>
                        <div class="stat-value negative">0</div>
                    </div>
                    <div class="stat-row">
                        <div class="stat-label">Response Time</div>
                        <div class="stat-value positive">&lt; 1s</div>
                    </div>
                    <div class="stat-row">
                        <div class="stat-label">Lead Conversion</div>
                        <div class="stat-value positive">+40%</div>
                    </div>
                    <div class="stat-row">
                        <div class="stat-label">Revenue Recovered</div>
                        <div class="stat-value positive">$8,450</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- ========== VIDEO SECTION ========== -->
    <section class="video-section" id="video">
        <div class="container">
            <div class="section-header">
                <span class="section-label">Demo</span>
                <h2 class="section-title">See The Future of Service</h2>
                <p class="section-subtitle">Watch how our AI handles complex customer interactions in real-time.</p>
            </div>
            
            <div class="video-wrapper">
                <div class="video-placeholder" onclick="this.innerHTML = '<iframe src=\\'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1\\' allow=\\'autoplay; encrypted-media\\' allowfullscreen></iframe>'">
                    <div class="video-play-btn">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                    </div>
                    <p>Click to Play Demo</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- ========== PROBLEM SECTION ========== -->
    <section class="problem-section" id="problem">
        <div class="container">
            <div class="problem-grid">
                <div class="problem-content">
                    <h2>The Silent Business Killer: <br><span>Unanswered Calls</span></h2>
                    <p>You spend thousands on ads, SEO, and leads. But if you don't answer the phone instantly, 85% of customers call your competitor. It's not your fault—you're busy working.</p>
                    
                    <div class="problem-cards">
                        <div class="problem-card">
                            <div class="problem-card-icon">“ž</div>
                            <div>
                                <h4>62% of Calls Go to Voicemail</h4>
                                <p>And 80% of callers won't leave a message. They just hang up and call the next guy.</p>
                            </div>
                        </div>
                        <div class="problem-card">
                            <div class="problem-card-icon">’¸</div>
                            <div>
                                <h4>Speed to Lead is Everything</h4>
                                <p>If you don't respond in 5 minutes, your odds of closing drop by 400%.</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="problem-stats">
                    <div class="problem-stat">
                        <div class="problem-stat-number">$250k</div>
                        <div class="problem-stat-label">Lost Annual Revenue per Truck</div>
                    </div>
                    <div class="problem-stat">
                        <div class="problem-stat-number">15hrs</div>
                        <div class="problem-stat-label">Wasted Weekly on Admin</div>
                    </div>
                    <div class="problem-stat">
                        <div class="problem-stat-number">38%</div>
                        <div class="problem-stat-label">Lower Close Rate (No Follow-up)</div>
                    </div>
                    <div class="problem-stat">
                        <div class="problem-stat-number">HIGH</div>
                        <div class="problem-stat-label">Staff Burnout Rate</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- ========== SOLUTION SECTION ========== -->
    <section class="solution-section" id="solution">
        <div class="container">
            <div class="section-header">
                <span class="section-label">The Solution</span>
                <h2 class="section-title">Your 24/7 Service Army</h2>
                <p class="section-subtitle">One platform to handle every lead, booking, and review automatically.</p>
            </div>
            
            <div class="solution-grid">
                <div class="solution-card">
                    <div class="solution-icon">¤–</div>
                    <div class="agent-name">Spartan AI</div>
                    <h3>AI Receptionist</h3>
                    <p>Answers calls, qualifies leads, and books appointments 24/7. Never sleeps, never sick.</p>
                    <div class="solution-status live">— Active</div>
                </div>
                
                <div class="solution-card">
                    <div class="solution-icon">”„</div>
                    <div class="agent-name">Follow-up Bot</div>
                    <h3>Instant Reactivation</h3>
                    <p>Text-backs every missed call instantly. Turns "I'll call back" into "I'm booked."</p>
                    <div class="solution-status live">— Active</div>
                </div>
                
                <div class="solution-card">
                    <div class="solution-icon">­</div>
                    <div class="agent-name">Reputation Guard</div>
                    <h3>Review Automation</h3>
                    <p>Automatically requests reviews after service. Intercepts negative feedback before it goes public.</p>
                    <div class="solution-status live">— Active</div>
                </div>
                
                <div class="solution-card">
                    <div class="solution-icon">•¸ï¸</div>
                    <div class="agent-name">Lead Net</div>
                    <h3>Database Reactivation</h3>
                    <p>Mines your old customer list to generate new jobs during slow seasons automatically.</p>
                    <div class="solution-status ready">— Ready</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- ========== PRICING SECTION ========== -->
    <section class="pricing-section" id="pricing">
        <div class="container">
            <div class="section-header">
                <span class="section-label">Investment</span>
                <h2 class="section-title">Simple Pricing. Huge ROI.</h2>
                <p class="section-subtitle">Costs less than one missed job per month. No contracts, cancel anytime.</p>
            </div>
            
            <div class="pricing-toggle">
                <span class="active">Monthly</span>
                <div class="toggle-switch" onclick="togglePricing()"></div>
                <span>Annual <span class="save-badge">Save 20%</span></span>
            </div>
            
            <div class="pricing-grid">
                <!-- Plan 1: Starter -->
                <div class="pricing-card">
                    <div class="pricing-header">
                        <div class="pricing-name">Starter</div>
                        <div class="pricing-tagline">For Solo Operators</div>
                        <div class="pricing-price">
                            <span class="pricing-currency">$</span>
                            <span class="pricing-amount icon-price" data-monthly="297" data-annual="237">297</span>
                        </div>
                        <div class="pricing-period">/month</div>
                        <div class="pricing-annual">Billed <span class="annual-price" data-monthly="monthly" data-annual="$2,844">monthly</span></div>
                    </div>
                    <div class="pricing-features">
                        <ul>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Missed Call Text-Back</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Unified Inbox</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Review Management</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> 2-Way SMS & Email</li>
                            <li class="disabled"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg> AI Voice Receptionist</li>
                        </ul>
                    </div>
                    <a class="pricing-btn secondary" href="/checkout?plan=starter">Get Started</a>
                </div>
                
                <!-- Plan 2: Growth Partner -->
                <div class="pricing-card featured">
                    <div class="pricing-badge">Most Popular</div>
                    <div class="pricing-header">
                        <div class="pricing-name">Growth</div>
                        <div class="pricing-tagline">For Growing Teams</div>
                        <div class="pricing-price">
                            <span class="pricing-currency">$</span>
                            <span class="pricing-amount icon-price" data-monthly="497" data-annual="397">497</span>
                        </div>
                        <div class="pricing-period">/month</div>
                        <div class="pricing-annual">Billed <span class="annual-price" data-monthly="monthly" data-annual="$4,764">monthly</span></div>
                    </div>
                    <div class="pricing-features">
                        <ul>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> <strong>Everything in Starter</strong></li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> AI Voice Receptionist</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Auto-Booking Bot</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> CRM Integration</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Database Reactivation</li>
                        </ul>
                    </div>
                    <a class="pricing-btn primary" href="/checkout?plan=growth">Start 14-Day Free Trial</a>
                </div>
                
                <!-- Plan 3: Dominance -->
                <div class="pricing-card">
                    <div class="pricing-header">
                        <div class="pricing-name">Scale</div>
                        <div class="pricing-tagline">For Market Leaders</div>
                        <div class="pricing-price">
                            <span class="pricing-currency">$</span>
                            <span class="pricing-amount icon-price" data-monthly="997" data-annual="797">997</span>
                        </div>
                        <div class="pricing-period">/month</div>
                        <div class="pricing-annual">Billed <span class="annual-price" data-monthly="monthly" data-annual="$9,564">monthly</span></div>
                    </div>
                    <div class="pricing-features">
                        <ul>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> <strong>Everything in Growth</strong></li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Custom Workflows</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Facebook/Google Ads AI</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Dedicated Account Mgr</li>
                            <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Priority Support</li>
                        </ul>
                    </div>
                    <a class="pricing-btn secondary" href="/checkout?plan=scale">Get Started</a>
                </div>
            </div>
        </div>
    </section>
    
    <!-- ========== HOW IT WORKS ========== -->
    <section class="how-section" id="how-it-works">
        <div class="container">
            <div class="section-header">
                <span class="section-label">Process</span>
                <h2 class="section-title">Setup in 24 Hours</h2>
                <p class="section-subtitle">No tech skills required. We handle the heavy lifting.</p>
            </div>
            
            <div class="how-steps">
                <div class="how-step">
                    <div class="step-number">1</div>
                    <h3>Connect</h3>
                    <p>Link your phone number, Google profile, and Facebook page to our platform.</p>
                </div>
                <div class="how-step">
                    <div class="step-number">2</div>
                    <h3>Customize</h3>
                    <p>Tell our AI about your services, pricing, and availability. It learns instantly.</p>
                </div>
                <div class="how-step">
                    <div class="step-number">3</div>
                    <h3>Launch</h3>
                    <p>Turn it on. Watch missed calls turn into booked appointments automatically.</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- ========== TESTIMONIALS ========== -->
    <section class="testimonials-section" id="reviews">
        <div class="container">
            <div class="section-header">
                <span class="section-label">Proof</span>
                <h2 class="section-title">Trusted by Pros</h2>
            </div>
            
            <div class="testimonials-grid">
                <div class="testimonial-card">
                    <div class="testimonial-stars">˜…˜…˜…˜…˜…</div>
                    <p class="testimonial-text">"I was skeptical at first, but this thing booked 4 jobs while I was asleep the first night. It paid for itself in 12 hours."</p>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">JD</div>
                        <div class="testimonial-info">
                            <h4>John Davis</h4>
                            <p>Davis HVAC</p>
                        </div>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="testimonial-stars">˜…˜…˜…˜…˜…</div>
                    <p class="testimonial-text">"My receptionist quit and I was panicking. Plugged this in and it handles more volume than she ever could. Unreal."</p>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">MS</div>
                        <div class="testimonial-info">
                            <h4>Mike Stevens</h4>
                            <p>Stevens Plumbing</p>
                        </div>
                    </div>
                </div>
                <div class="testimonial-card">
                    <div class="testimonial-stars">˜…˜…˜…˜…˜…</div>
                    <p class="testimonial-text">"The missed call text-back feature alone has saved me at least $20k this year. Customers love the instant response."</p>
                    <div class="testimonial-author">
                        <div class="testimonial-avatar">RL</div>
                        <div class="testimonial-info">
                            <h4>Robert Lee</h4>
                            <p>Lee Electric</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- ========== CONTACT / FINAL CTA ========== -->
    <section class="final-cta">
        <div class="container final-cta-content">
            <h2>Ready to Stop <span class="highlight">Losing Money?</span></h2>
            <p>Join 500+ successful service businesses using AI to dominate their market.</p>
            
            <div class="final-cta-btns">
                <button class="btn-primary" onclick="openFunnel()">
                    Start Free Trial
                </button>
                <a href="#pricing" class="btn-secondary">View Pricing</a>
            </div>
        </div>
    </section>
    
    <!-- ========== FOOTER ========== -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand">
                    <h3><span style="font-size: 24px;">¤–</span> AI Service<span>Co</span></h3>
                    <p>The #1 AI automation platform for service businesses. Stop chasing leads. Start closing jobs.</p>
                </div>
                
                <div class="footer-links">
                    <h4>Platform</h4>
                    <a href="#">Features</a>
                    <a href="#">Pricing</a>
                    <a href="#">Integrations</a>
                    <a href="#">Login</a>
                </div>
                
                <div class="footer-links">
                    <h4>Resources</h4>
                    <a href="#">Case Studies</a>
                    <a href="#">Help Center</a>
                    <a href="#">API Docs</a>
                    <a href="#">Partner Program</a>
                </div>
                
                <div class="footer-links">
                    <h4>Contact</h4>
                    <a href="mailto:support@aiserviceco.com">support@aiserviceco.com</a>
                    <a href="tel:+18555983794">(855) 598-3794</a>
                    <p style="margin-top: 10px; color: var(--gray);">123 Innovation Dr.<br>Austin, TX 78701</p>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2024 AI Service Co. All rights reserved.</p>
                <div class="footer-legal">
                    <a href="#">Privacy Policy</a>
                    <a href="#">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>
    
    <!-- ========== FUNNEL MODAL ========== -->
    <div class="funnel-overlay" id="funnelOverlay">
        <div class="funnel-container">
            <!-- Close Button -->
            <button class="funnel-close" onclick="closeFunnel()">Ã—</button>
            
            <!-- Step 1: Qualification -->
            <div class="funnel-step active" id="funnelStep1">
                <div class="funnel-progress">
                    <div class="progress-dot active" id="dot1"></div>
                    <div class="progress-dot" id="dot2"></div>
                    <div class="progress-dot" id="dot3"></div>
                </div>
                <h3>What's your biggest <span class="highlight">pain point?</span></h3>
                <p>We'll tailor the AI to solve this first.</p>
                
                <div class="funnel-options">
                    <div class="funnel-option" onclick="nextStep(2, 'pain:missed_calls')">
                        <div class="funnel-option-icon">“ž</div>
                        <div class="funnel-option-text">
                            <h4>Capture every call</h4>
                            <p>I miss calls when I'm working</p>
                        </div>
                    </div>
                    
                    <div class="funnel-option" onclick="nextStep(2, 'pain:leads')">
                        <div class="funnel-option-icon">“‰</div>
                        <div class="funnel-option-text">
                            <h4>Get more leads</h4>
                            <p>I need more consistent work</p>
                        </div>
                    </div>
                    
                    <div class="funnel-option" onclick="nextStep(2, 'pain:admin')">
                        <div class="funnel-option-icon">˜«</div>
                        <div class="funnel-option-text">
                            <h4>Reduce admin chaos</h4>
                            <p>Too much time on scheduling/billing</p>
                        </div>
                    </div>
                    
                    <div style="margin-top: 10px;">
                        <div class="funnel-option" onclick="toggleOtherInput(this)">
                             <div class="funnel-option-icon">œï¸</div>
                             <div class="funnel-option-text">
                                 <h4>Something else...</h4>
                             </div>
                        </div>
                        <input type="text" class="funnel-other-input" id="otherPainInput" placeholder="Type your biggest challenge..." style="display: none;">
                        <button class="funnel-other-submit" id="otherPainSubmit" onclick="submitOtherPain()">Continue</button>
                    </div>
                </div>
            </div>
            
            <!-- Step 2: Team Size -->
            <div class="funnel-step" id="funnelStep2">
                <div class="funnel-progress">
                    <div class="progress-dot completed"></div>
                    <div class="progress-dot active" id="dot2"></div>
                    <div class="progress-dot" id="dot3"></div>
                </div>
                <h3>How big is your <span class="highlight">team?</span></h3>
                <p>To recommend the right plan.</p>
                
                <div class="funnel-options">
                    <div class="funnel-option" onclick="nextStep(3, 'size:solo')">
                        <div class="funnel-option-icon">‘¤</div>
                        <div class="funnel-option-text">
                            <h4>Just me (Solo)</h4>
                        </div>
                    </div>
                    
                    <div class="funnel-option" onclick="nextStep(3, 'size:small')">
                        <div class="funnel-option-icon">‘¥</div>
                        <div class="funnel-option-text">
                            <h4>Small Crew (2-5)</h4>
                        </div>
                    </div>
                    
                    <div class="funnel-option" onclick="nextStep(3, 'size:growth')">
                        <div class="funnel-option-icon">š€</div>
                        <div class="funnel-option-text">
                            <h4>Growing (6-20)</h4>
                        </div>
                    </div>
                </div>
                
                <button class="funnel-back" onclick="prevStep(1)">← Back</button>
            </div>
            
            <!-- Step 3: Urgency -->
            <div class="funnel-step" id="funnelStep3">
                 <div class="funnel-progress">
                    <div class="progress-dot completed"></div>
                    <div class="progress-dot completed"></div>
                    <div class="progress-dot active" id="dot3"></div>
                </div>
                <h3>When do you want to <span class="highlight">launch?</span></h3>
                
                <div class="funnel-options">
                    <div class="funnel-option" onclick="nextStep(4, 'urgency:asap')">
                        <div class="funnel-option-icon">š¡</div>
                        <div class="funnel-option-text">
                            <h4>ASAP (Today)</h4>
                        </div>
                    </div>
                    
                    <div class="funnel-option" onclick="nextStep(4, 'urgency:week')">
                        <div class="funnel-option-icon">“…</div>
                        <div class="funnel-option-text">
                            <h4>This Week</h4>
                        </div>
                    </div>
                    
                    <div class="funnel-option" onclick="nextStep(4, 'urgency:season')">
                        <div class="funnel-option-icon">˜€ï¸</div>
                        <div class="funnel-option-text">
                            <h4>Before Busy Season (Summer)</h4>
                        </div>
                    </div>
                </div>
                
                <button class="funnel-back" onclick="prevStep(2)">← Back</button>
            </div>
            
            <!-- Step 4: Offer Selection -->
            <div class="funnel-step" id="funnelStep4">
                <div class="funnel-progress" style="opacity: 0;">
                </div>
                <h3>Perfect. <span class="highlight">Here's the plan.</span></h3>
                <p style="margin-bottom: 20px;">Based on your answers, we recommend starting with the <strong>Growth Partner</strong> setup.</p>
                
                <div class="funnel-options">
                    <div class="funnel-option" onclick="showContactForm()" style="border-color: var(--red); background: var(--red-subtle);">
                        <div class="funnel-option-icon" style="background: var(--red);">”¥</div>
                        <div class="funnel-option-text">
                            <h4>Start My Free Trial</h4>
                            <p>14 Days Free. Cancel Anytime.</p>
                        </div>
                    </div>
                    
                    <div class="funnel-option" onclick="showContactOptions()">
                        <div class="funnel-option-icon">’¡</div>
                        <div class="funnel-option-text">
                            <h4>Talk Strategy First</h4>
                            <p>I have a few questions.</p>
                        </div>
                    </div>
                    
                     <div class="funnel-option" onclick="selectPlan('Growth')">
                        <div class="funnel-option-icon">💳</div>
                        <div class="funnel-option-text">
                            <h4>I'm Ready — Let's Go</h4>
                            <p>Skip trial, start onboarding.</p>
                        </div>
                    </div>
                </div>
                
                 <button class="funnel-back" onclick="prevStep(3)">← Back</button>
            </div>
            
                        <!-- Step: Payment Form (GHL Embed) -->
            <div class="funnel-step" id="funnelStepPayment">
                 <h3>Secure Payment</h3>
                 <p>Complete your setup for the <span class="highlight" id="selectedPlanDisplay">Growth</span> plan.</p>
                 
                 <div class="funnel-form-container">
                     <!-- GHL PAYMENT FORM EMBED -->
                     <iframe src="https://api.leadconnectorhq.com/widget/form/qaJ7szEbp2TwJkAT6WxG" 
                             style="width:100%;height:100%;border:none;border-radius:4px;min-height:500px;" 
                             id="inline-qaJ7szEbp2TwJkAT6WxG" 
                             data-layout="{'id':'INLINE'}" 
                             data-trigger-type="alwaysShow" 
                             data-trigger-value="" 
                             data-activation-type="alwaysActivated" 
                             data-activation-value="" 
                             data-deactivation-type="neverDeactivate" 
                             data-deactivation-value="" 
                             data-form-name="AI Service Co Payment" 
                             data-height="586" 
                             data-layout-iframe-id="inline-qaJ7szEbp2TwJkAT6WxG" 
                             data-form-id="qaJ7szEbp2TwJkAT6WxG" 
                             title="AI Service Co Payment">
                     </iframe>
                     <script src="https://link.msgsndr.com/js/form_embed.js"></script>
                 </div>
                 
                 <button class="funnel-back" onclick="showStep(4)"> Back</button>
            </div>

            <!-- Step: Contact Form (GHL Embed) -->
            <div class="funnel-step" id="funnelStepContact">
                 <h3>Create Your Account</h3>
                 <p>Enter your details to start your 14-day free trial.</p>
                 
                 <div class="funnel-form-container">
                     <!-- GHL FORM EMBED -->
                     <iframe src="https://api.leadconnectorhq.com/widget/form/7TTJ1CUAFjhON69ZsOZK" 
                             style="width:100%;height:100%;border:none;border-radius:4px;min-height:500px;" 
                             id="inline-7TTJ1CUAFjhON69ZsOZK" 
                             data-layout="{'id':'INLINE'}" 
                             data-trigger-type="alwaysShow" 
                             data-trigger-value="" 
                             data-activation-type="alwaysActivated" 
                             data-activation-value="" 
                             data-deactivation-type="neverDeactivate" 
                             data-deactivation-value="" 
                             data-form-name="AI Service Co Contact" 
                             data-height="586" 
                             data-layout-iframe-id="inline-7TTJ1CUAFjhON69ZsOZK" 
                             data-form-id="7TTJ1CUAFjhON69ZsOZK" 
                             title="AI Service Co Contact">
                     </iframe>
                     <script src="https://link.msgsndr.com/js/form_embed.js"></script>
                 </div>
                 
                 <button class="funnel-back" onclick="showStep(4)">← Back</button>
            </div>
            
            <!-- Step: Contact Options -->
             <div class="funnel-step" id="funnelStepOptions">
                 <h3>Let's Connect</h3>
                 <p>Choose how you'd like to get answers.</p>
                 
                 <div class="funnel-contact-cards">
                     <div class="funnel-contact-card">
                         <h4>Call Us Now</h4>
                         <a href="tel:+18555983794">(855) 598-3794</a>
                         <p>Direct line to support.</p>
                     </div>
                     
                     <div class="funnel-contact-card">
                         <h4>Email Us</h4>
                         <a href="mailto:support@aiserviceco.com" style="font-size: 18px;">support@aiserviceco.com</a>
                         <p>Response within 2 hours.</p>
                     </div>
                     
                     <!-- Chat trigger via LeadConnector -->
                     <div class="funnel-contact-card" onclick="openChatWidget()" style="cursor: pointer;">
                         <h4>Live Chat</h4>
                         <a href="#">Start Chat</a>
                         <p>Instant answers.</p>
                     </div>
                 </div>
                 
                 <button class="funnel-back" onclick="showStep(4)">← Back</button>
            </div>
            
        </div>
    </div>
    
    <!-- ========== SCRIPTS ========== -->
    <!-- GHL Chat Widget -->
    <script src="https://widgets.leadconnectorhq.com/loader.js" data-resources-url="https://widgets.leadconnectorhq.com/chat-widget/loader.js" data-widget-id="67664e43fa0f6b4d36ff5e46"></script> 
    
    <script>
        // Use URL params if dynamically injected
        const CALENDLY_URL = "{calendly_url}";
        const STRIPE_URL = "{stripe_url}";
        
        let formData = {};
        
        function openFunnel() {
            document.getElementById('funnelOverlay').classList.add('active');
            // Ensure step 1 is shown
            showStep(1);
        }
        
        function closeFunnel() {
            document.getElementById('funnelOverlay').classList.remove('active');
        }
        
        // Close on outside click
        document.getElementById('funnelOverlay').addEventListener('click', function(e) {
            if (e.target === this) {
                closeFunnel();
            }
        });
        
                function selectPlan(planName) {
           selectedPlan = planName;
           const display = document.getElementById('selectedPlanDisplay');
           if (display) display.innerText = planName;
           showStep('Payment');
        }

        function showStep(stepNum) {
            // Hide all steps
            document.querySelectorAll('.funnel-step').forEach(step => {
                step.classList.remove('active');
            });
            // Show target step
            const target = document.getElementById('funnelStep' + stepNum);
            if (target) target.classList.add('active');
        }

        function selectPlan(planName) {
           selectedPlan = planName;
           const display = document.getElementById('selectedPlanDisplay');
           if (display) display.innerText = planName;
           showStep('Payment');
        }
        
        function nextStep(stepNum, data) {
            // Collect data
            if (data) {
                const parts = data.split(':');
                formData[parts[0]] = parts[1];
                console.log('Funnel Data:', formData);
            }
            showStep(stepNum);
        }
        
        function prevStep(stepNum) {
            showStep(stepNum);
        }
        
        function toggleOtherInput(el) {
            const input = el.nextElementSibling;
            const btn = input.nextElementSibling;
            
            if (input.style.display === 'none') {
                input.style.display = 'block';
                input.focus();
                btn.classList.add('visible');
            } else {
                input.style.display = 'none';
                btn.classList.remove('visible');
            }
        }
        
        function submitOtherPain() {
            const input = document.getElementById('otherPainInput');
            if (input.value.trim() !== '') {
                formData['pain'] = 'other:' + input.value;
                nextStep(2);
            }
        }
        
        function showContactForm() {
            showStep('Contact');
        }
        
        function showContactOptions() {
            showStep('Options');
        }
        
        function openChatWidget() {
            // Try to open the LC widget
            // This depends on the widget's exposed API, often just clicking the iframe works if accessible
            // or simulating a click on the bubble
            closeFunnel();
            // Just a visual cue for now if API not known
            alert("Please click the chat bubble in the bottom right corner!");
        }
        
        // Pricing Toggle
        function togglePricing() {
            const toggle = document.querySelector('.toggle-switch');
            const statusSpans = document.querySelectorAll('.pricing-toggle span');
            const prices = document.querySelectorAll('.pricing-amount');
            const annualLabels = document.querySelectorAll('.annual-price');
            
            toggle.classList.toggle('active');
            const isAnnual = toggle.classList.contains('active');
            
            statusSpans[0].classList.toggle('active'); // Monthly
            statusSpans[1].classList.toggle('active'); // Annual
            
            prices.forEach(el => {
                const monthly = el.dataset.monthly;
                const annual = el.dataset.annual;
                if (monthly && annual) {
                    el.textContent = isAnnual ? annual : monthly;
                }
            });
            
            annualLabels.forEach(el => {
                 const annual = el.dataset.annual;
                 if (annual) {
                     el.textContent = isAnnual ? 'annual ' + annual : 'monthly';
                 }
            });
        }
        
        // Header Scroll
        window.addEventListener('scroll', () => {
            const header = document.querySelector('header');
            if (window.scrollY > 50) {
                header.style.background = 'rgba(0,0,0,0.98)';
            } else {
                header.style.background = 'rgba(0,0,0,0.95)';
            }
        });
        
    </script>
</body>
</html>
"""
    return html
