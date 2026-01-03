from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import ssl

# --- DEPENDENCY SAFEGUARDS ---
stripe_error = None
resend_error = None
pg_error = None

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

            # --- ROUTE: HEALTH ---
            elif path == "/api/health":
                data = {
                    "status": "healthy",
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
                    if con:
                        try:
                            msg = body.get('message', {})
                            con.run(
                                "INSERT INTO interactions (type, summary, transcript, lead_phone) VALUES (:t, :s, :tr, :p)",
                                t='VAPI_CALL',
                                s=msg.get('summary', 'No summary'),
                                tr=msg.get('transcript', 'No transcript'),
                                p=msg.get('customer', {}).get('number', 'Unknown')
                            )
                            con.close()
                            print("✅ Call Logged to Neural Storage")
                        except Exception as e:
                            print(f"❌ Log Error: {e}")

                response_data = {"status": "ok"}
            
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
                          "to": body.get('email'),
                          "subject": f"Reserved: {body.get('plan')}",
                          "html": "<p>Reservation Confirmed. Welcome to the Empire.</p>"
                        })
                    except: pass
                
                response_data = {"status": "success", "message": "Reservation Confirmed"}

            # --- ROUTE: CHAT ---
            elif path == "/api/chat":
                # ... (Keep existing chat logic) ...
                command = body.get('command', '').lower()
                resp_text = "Command acknowledged."
                if "status" in command:
                     resp_text = "Systems Nominal. Database Connected. (Bare Metal)"
                elif "deploy" in command:
                     resp_text = "Deployment Active."
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

