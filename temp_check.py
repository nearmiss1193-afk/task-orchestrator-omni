import importlib.util, os
spec = importlib.util.spec_from_file_location('master_verify', r'c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified\\master_verify.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
checks = [
    ('GHL API', mod.verify_ghl_api),
    ('Vapi Sarah', mod.verify_vapi_sarah),
    ('Resend Email', mod.verify_resend_email),
    ('Landing Pages', mod.verify_landing_pages),
    ('Stripe Checkout', mod.verify_stripe_checkout),
    ('Supabase', mod.verify_supabase),
    ('GHL Workflows', mod.verify_ghl_workflows),
    ('Dashboard', mod.verify_dashboard),
]
for name, fn in checks:
    success, msg = fn()
    print(f'{name}:', '✅' if success else '❌', msg)
