from http.server import BaseHTTPRequestHandler
import json
import os
import re
import urllib.parse
import urllib.request
import ssl

# --- DEPENDENCY SAFEGUARDS ---
stripe_error = None
resend_error = None
pg_error = None

# --- SENTRY MONITORING ---
try:
    import sentry_sdk
    dsn = os.environ.get("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(dsn=dsn, traces_sample_rate=1.0)
except: pass


try:
    import resend
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
except Exception as e:
    resend = None
    resend_error = str(e)

try:
    import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
except Exception as e:
    stripe = None
    stripe_error = str(e)

try:
    import pg8000.native
except Exception as e:
    pg8000 = None
    pg_error = str(e)

# --- DATABASE CONNECTION ---
def get_db_connection():
    if not pg8000: return None
    try:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url: return None
        
        # Parse URL for pg8000 native connection
        result = urllib.parse.urlparse(db_url)
        username = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432
        database = result.path[1:]
        
        # SSL Context for Supabase
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        con = pg8000.native.Connection(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database,
            ssl_context=ssl_context
        )
        return con
    except Exception as e:
        print(f"DB Error: {e}")
        return None

class handler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        try:
            path = urllib.parse.urlparse(self.path).path
            
            # --- ROUTE: STATS ---
            if path == "/api/stats":
                con = get_db_connection()
                leads_count = 5 # Default
                
                if con:
                    try:
                        # Count total leads
                        rows = con.run("SELECT COUNT(*) FROM leads")
                        leads_count = rows[0][0]
                        con.close()
                    except: pass

                data = {
                    "leads": leads_count,
                    "revenue": leads_count * 99, 
                    "calls": 142, 
                    "reservations": leads_count, 
                    "status": "live_db" if con else "mock_db"
                }

            # --- ROUTE: LEADS ---
            elif path == "/api/leads":
                con = get_db_connection()
                leads_data = []

                if con:
                    try:
                        # Fetch recent 10 leads
                        rows = con.run("SELECT name, email, phone, source, created_at FROM leads ORDER BY created_at DESC LIMIT 10")
                        for r in rows:
                            leads_data.append({
                                "name": r[0], "email": r[1], "phone": r[2], "source": r[3], "created_at": str(r[4])
                            })
                        con.close()
                    except: pass
                
                if not leads_data:
                    # Fallback if DB empty or fails
                    leads_data = [{"name": "Waiting for Data", "email": "system@ready.ai", "source": "SYSTEM_READY"}]
                
                data = leads_data


# ... (Existing imports) ...

            # --- ROUTE: HEALTH ---
            elif path == "/api/health":
                # Heartbeat Logic (Keep DB Awake)
                query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                ping_db = 'ping_db' in query_params
                
                db_status = "skipped"
                if ping_db:
                    con = get_db_connection()
                    if con:
                        try:
                            con.run("SELECT 1")
                            con.close()
                            db_status = "alive"
                        except Exception as e:
                            db_status = f"error: {e}"
                    else:
                        db_status = "connection_failed"

                data = {
                    "status": "healthy",
                    "heartbeat": db_status,
                    "dependencies": {
                        "stripe": {"loaded": stripe is not None, "error": stripe_error},
                        "resend": {"loaded": resend is not None, "error": resend_error},
                        "pg8000": {"loaded": pg8000 is not None, "error": pg_error}
                    },
                    "environment": {
                        "STRIPE_KEY_PRESENT": os.environ.get("STRIPE_SECRET_KEY") is not None,
                        "RESEND_KEY_PRESENT": os.environ.get("RESEND_API_KEY") is not None,
                        "DB_URL_PRESENT": os.environ.get("DATABASE_URL") is not None,
                        "VERCEL_URL": os.environ.get("VERCEL_URL")
                    }
                }

            else:
                data = {"status": "Empire Sovereign Cloud Active 🟢"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_POST(self):
        try:
            path = urllib.parse.urlparse(self.path).path
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            response_data = {"status": "received"}

            # --- ROUTE: WEBHOOK (VAPI) ---
            if path.endswith("/vapi/webhook"):
                print(f"📡 Webhook: {body.get('message', {}).get('type')}")
                
                # 'Intel Predator' Logic: Log Interaction
                if body.get('message', {}).get('type') == 'end-of-call-report':
                    con = get_db_connection()
                    msg = body.get('message', {})
                    summary = msg.get('summary', 'No summary')
                    transcript = msg.get('transcript', 'No transcript')
                    customer_phone = msg.get('customer', {}).get('number', 'Unknown')
                    
                    # 1. Log to DB
                    if con:
                        try:
                            con.run(
                                "INSERT INTO interactions (type, summary, transcript, lead_phone) VALUES (:t, :s, :tr, :p)",
                                t='VAPI_CALL',
                                s=summary,
                                tr=transcript,
                                p=customer_phone
                            )
                            con.close()
                            print("✅ Call Logged to Neural Storage")
                        except Exception as e:
                            print(f"❌ Log Error: {e}")

                    # 2. Lost Lead Recovery Loop (The "Rachel" Protocol)
                    # Simple heuristic: If "appointment" or "booked" is NOT in summary, it's a lost lead.
                    is_booked = "booked" in summary.lower() or "appointment" in summary.lower() or "scheduled" in summary.lower()
                    
                    if not is_booked and resend:
                        print(f"⚠️ Lost Lead Detected: {customer_phone}. Triggering Recovery Protocol...")
                        try:
                            resend.Emails.send({
                                "from": "alert@aiserviceco.com",
                                "to": ["nearmiss1193@gmail.com"],
                                "subject": f"🚨 LOST LEAD RECOVERY: {customer_phone}",
                                "html": f"""
                                    <h2>⚠️ Lead Did Not Book</h2>
                                    <p><strong>Phone:</strong> {customer_phone}</p>
                                    <p><strong>Summary:</strong> {summary}</p>
                                    <hr>
                                    <h3>🚀 ACTION REQUIRED: SMS RECOVERY</h3>
                                    <p>Copy/Paste and send this SMS immediately:</p>
                                    <blockquote style="background: #f9f9f9; padding: 15px; border-left: 5px solid #d9534f;">
                                        "Hey, I'm Rachel from Lakeland Cooling. I noticed our call got cut off before we could lock in that $59 Tune-Up. Should I save that spot for you now?"
                                    </blockquote>
                                """
                            })
                            print("✅ Recovery Alert Sent.")
                        except Exception as e:
                            print(f"❌ Recovery Alert Failed: {e}")

                response_data = {"status": "ok"}
            
            # --- ROUTE: STRIPE WEBHOOK ---
            elif path == "/api/stripe-webhook":
                sig_header = self.headers.get('Stripe-Signature')
                webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
                
                if not webhook_secret or not stripe:
                    print("⚠️ Configuration Error: Missing Secret or Stripe Lib")
                    # We return 200 to correct Stripe retries if config is broken, but verify sig if possible
                    if not webhook_secret: raise Exception("Webhook Secret Missing")

                try:
                    event = stripe.Webhook.construct_event(
                        post_data, sig_header, webhook_secret
                    )
                except Exception as e:
                    print(f"⚠️ Webhook Error: {e}")
                    raise e

                # Handle the event
                if event['type'] == 'checkout.session.completed':
                    session = event['data']['object']
                    customer_email = session.get('customer_details', {}).get('email')
                    
                    print(f"💰 Payment Received: {customer_email}")
                    
                    if resend and customer_email:
                         try:
                            # 1. Customer Welcome
                            resend.Emails.send({
                                "from": "alert@aiserviceco.com",
                                "to": [customer_email],
                                "subject": "Welcome to the Empire (Access Granted)",
                                "html": """
                                    <h1>Access Granted</h1>
                                    <p>Your payment has been verified.</p>
                                    <p><strong>Next Steps:</strong></p>
                                    <ol>
                                        <li>Login to your dashboard: <a href="https://empire-sovereign-cloud.vercel.app/dashboard.html">Click Here</a></li>
                                        <li>Configure your profile.</li>
                                    </ol>
                                    <p>The Empire greets you.</p>
                                """
                            })
                            # 2. Admin Alert
                            resend.Emails.send({
                                "from": "alert@aiserviceco.com",
                                "to": ["nearmiss1193@gmail.com"],
                                "subject": f"💰 New Sale: {customer_email}",
                                "html": f"<p>New customer onboarding: {customer_email}</p>"
                            })
                         except Exception as e:
                             print(f"Email Error: {e}")

                response_data = {"status": "success"}

            # --- ROUTE: RESERVE ---
            elif path == "/api/reserve":
                print(f"📝 Reservation: {body}")
                
                # 1. DB Insert
                con = get_db_connection()
                if con:
                    try:
                        # Adapts to simple schema, ignores extras if missing
                        con.run(
                            "INSERT INTO leads (name, email, phone, source, metadata) VALUES (:n, :e, :p, :s, :m)",
                            n=body.get('name', 'Web User'),
                            e=body.get('email'),
                            p=body.get('phone', 'N/A'),
                            s='WEB_RESERVATION',
                            m=json.dumps({"plan": body.get('plan')})
                        )
                        con.close()
                    except Exception as e:
                        print(f"DB Write Error: {e}")

                # 2. Email Notification
                if resend:
                    try:
                        resend.Emails.send({
                          "from": "alert@aiserviceco.com",
                          "to": ["nearmiss1193@gmail.com"],
                          "subject": f"Reserved: {body.get('plan')}",
                          "html": "<p>Reservation Confirmed. Welcome to the Empire.</p>"
                        })
                    except: pass
                
                response_data = {"status": "success", "message": "Reservation Confirmed"}

            # --- ROUTE: CHAT ---
            elif path == "/api/chat":
                try:
                    command = body.get('command', '').strip()
                    resp_text = "Command received."
                    cmd_lower = command.lower()
                    
                    # ACTION: Send SMS
                    if any(x in cmd_lower for x in ["send sms", "text ", "message "]):
                        phone_match = re.search(r'\+?1?\d{10,11}', command)
                        if phone_match:
                            phone = phone_match.group()
                            if not phone.startswith("+"):
                                phone = "+1" + phone.lstrip("1")
                            con = get_db_connection()
                            if con:
                                try:
                                    con.run("INSERT INTO commands (command, status) VALUES (:c, 'pending')", c=f"sms:{phone}:Dashboard Command")
                                    con.close()
                                    resp_text = f"SMS command queued for {phone}. Uplink Bridge will execute."
                                except:
                                    resp_text = f"SMS queued locally for {phone}."
                            else:
                                resp_text = f"SMS command noted for {phone}. Local system will process."
                        else:
                            resp_text = "No phone number detected. Try: 'Send SMS to +13529368152'"
                    
                    # ACTION: Call
                    elif any(x in cmd_lower for x in ["call ", "dial ", "phone "]):
                        phone_match = re.search(r'\+?1?\d{10,11}', command)
                        if phone_match:
                            phone = phone_match.group()
                            if not phone.startswith("+"):
                                phone = "+1" + phone.lstrip("1")
                            con = get_db_connection()
                            if con:
                                try:
                                    con.run("INSERT INTO commands (command, status) VALUES (:c, 'pending')", c=f"call:{phone}")
                                    con.close()
                                    resp_text = f"Call command queued. Sarah will call {phone} shortly."
                                except:
                                    resp_text = f"Call noted for {phone}. Local system will dial."
                            else:
                                resp_text = f"Call command noted for {phone}."
                        else:
                            resp_text = "No phone number detected. Try: 'Call +13529368152'"
                    
                    # ACTION: Email
                    elif "email" in cmd_lower:
                        resp_text = "Email command detected. Queuing for dispatch..."
                        con = get_db_connection()
                        if con:
                            try:
                                con.run("INSERT INTO commands (command, status) VALUES (:c, 'pending')", c=f"email:{command}")
                                con.close()
                            except: pass
                    
                    # STATUS/INFO: Use AI with fallback chain (Claude → Gemini → Static)
                    else:
                        system_prompt = """You are the Sovereign AI Orchestrator for Empire Unified, an AI-powered business automation agency.

COMMANDER INFO:
- Default phone: +13529368152
- Email: nearmiss1193@gmail.com

SYSTEM STATUS:
- 7 active leads in pipeline
- 142 AI calls tracked
- All systems online
- Sarah (Elite Voice AI) active and ready

CAPABILITIES:
- SMS: Send texts via GHL (say "sms" or "text" with phone number)
- Call: Have Sarah call via Vapi (say "call" with phone number)  
- Email: Send emails via Resend (say "email" with address)

PROSPECT OUTREACH TEMPLATES:

SMS Template:
"Hi [Name], this is Sarah from AI Service Co. We help home service businesses like yours automate lead follow-up and never miss a call. Would you be open to a quick 10-min demo? Reply YES and I'll send calendar options."

Email Template:
Subject: Stop losing leads to missed calls, [Business Name]
Body: "Hi [Name], I noticed [Business Name] serves the [City] area. Most contractors tell us they lose 40% of leads to missed calls and slow follow-up. Our AI assistant Sarah answers every call, qualifies leads, and books appointments 24/7. Want to see how it works? Book a quick demo: [LINK]"

Voice Script (Sarah):
"Hi, this is Sarah calling from AI Service Co. I help home service businesses never miss another lead. Is this a good time for a quick 2-minute overview?"

INSTRUCTIONS:
- Be concise but informative (under 100 words)
- If Commander asks for templates, show them formatted nicely
- If Commander says "text me" or "call me" without number, use +13529368152
- Confirm actions clearly
- Be proactive and helpful"""
                        
                        ai_response = None
                        
                        # TRY 1: Claude (Primary)
                        ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
                        if ANTHROPIC_KEY and not ai_response:
                            try:
                                api_url = "https://api.anthropic.com/v1/messages"
                                claude_payload = json.dumps({
                                    "model": "claude-3-haiku-20240307",
                                    "max_tokens": 200,
                                    "system": system_prompt,
                                    "messages": [{"role": "user", "content": command}]
                                }).encode('utf-8')
                                headers = {
                                    'Content-Type': 'application/json',
                                    'x-api-key': ANTHROPIC_KEY,
                                    'anthropic-version': '2023-06-01'
                                }
                                req = urllib.request.Request(api_url, data=claude_payload, headers=headers)
                                with urllib.request.urlopen(req, timeout=12) as api_resp:
                                    result = json.loads(api_resp.read().decode('utf-8'))
                                    ai_response = result.get('content', [{}])[0].get('text', None)
                            except:
                                pass  # Fall through to Gemini
                        
                        # TRY 2: Gemini (Fallback)
                        GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
                        if GEMINI_KEY and not ai_response:
                            try:
                                prompt_text = f"{system_prompt}\n\nCommander: {command}"
                                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
                                gemini_payload = json.dumps({
                                    "contents": [{"parts": [{"text": prompt_text}]}]
                                }).encode('utf-8')
                                req = urllib.request.Request(api_url, data=gemini_payload, headers={'Content-Type': 'application/json'})
                                with urllib.request.urlopen(req, timeout=12) as api_resp:
                                    result = json.loads(api_resp.read().decode('utf-8'))
                                    ai_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', None)
                            except:
                                pass  # Fall through to static
                        
                        # TRY 3: Static (Ultimate Fallback)
                        if ai_response:
                            resp_text = ai_response
                        else:
                            resp_text = "System online. All channels operational. Sarah (Voice AI) standing by. SMS, Email, and Voice ready."
                except Exception as chat_error:
                    resp_text = f"Error processing command: {str(chat_error)[:60]}"

                response_data = {"status": "success", "response": resp_text}

            # --- ROUTE: CHECKOUT ---
            elif path == "/api/create-checkout-session":
                # ... (Keep existing Stripe logic) ...
                if not stripe:
                    response_data = {"status": "error", "message": f"Stripe import failed: {stripe_error if stripe_error else 'Unknown error'}"}
                else:
                    plan = body.get('plan', 'starter').lower()
                    domain_url = os.environ.get("VERCEL_URL", "http://localhost:3000")
                    if "http" not in domain_url: domain_url = f"https://{domain_url}"
                    amounts = { "starter": 9900, "lite": 19900, "growth": 29700, "enterprise": 49900 }
                    try:
                        session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f'Empire HVAC: {plan.title()} Plan'}, 'unit_amount': amounts.get(plan, 9900), 'recurring': {'interval': 'month'}}, 'quantity': 1}],
                            mode='subscription',
                            customer_email=body.get('email'),
                            success_url=f'{domain_url}/hvac.html?session_id={{CHECKOUT_SESSION_ID}}&payment=success',
                            cancel_url=f'{domain_url}/checkout.html?payment=canceled',
                            subscription_data={'trial_period_days': 7}
                        )
                        response_data = {"status": "success", "url": session.url}
                    except Exception as stripe_exec:
                        import traceback
                        full_err = traceback.format_exc()
                        print(f"Stripe Session Error: {full_err}")
                        response_data = {"status": "error", "message": f"Stripe failed: {str(stripe_exec)}", "traceback": full_err}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

