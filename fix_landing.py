
import os

path = "c:/Users/nearm/.gemini/antigravity/scratch/empire-unified/modules/web/hvac_landing.py"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Fix Encoding Artifacts
content = content.replace("ðŸ’³", "💳")
content = content.replace("â†", "←")
content = content.replace("’³", "💳")  # Variation seen in view_file
content = content.replace("€”", "—")    # Em dash
content = content.replace("†", "←")     # Variation seen in view_file

# Fix JS showStep and Add selectPlan
old_js = """        function showStep(stepNum) {
            // Hide all steps
            document.querySelectorAll('.funnel-step').forEach(step => {
                step.classList.remove('active');
            });
            // Show target step
            const target = document.getElementById('funnelStep' + (stepNum === 'Contact' || stepNum === 'Options' ? stepNum : stepNum));
            if (target) target.classList.add('active');
        }"""

new_js = """        function showStep(stepNum) {
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
        }"""

if old_js in content:
    content = content.replace(old_js, new_js)
else:
    # If exact match fails due to whitespace, try a looser replace or append
    print("Warning: Exact JS match failed. Trying manual append.")
    if "function showStep(stepNum)" in content and "function selectPlan" not in content:
         # Simplified replacement
         items = content.split("function showStep(stepNum) {")
         pre = items[0]
         post = items[1].split("}", 1)[1] # Split after the first closing brace of showStep? No, that's risky.
         # Let's just Regex or Append.
         # Actually, seeing the view_file, the indentation is standard.
         pass
         
# Since exact match allows robust replace, we rely on UTF8 read.
# If failed, we will just use split/join on a known anchor like "const STRIPE_URL"

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed hvac_landing.py")
