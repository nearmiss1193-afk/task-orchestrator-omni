
import os
import sys

def build_solar():
    print("SOLAR BUILD...")
    
    html = """
<!DOCTYPE html>
<html>
<head>
<title>Solar AI</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 p-10 font-sans">
    <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-6xl font-black text-slate-900 mb-6">Stop Cooling Down Your Leads.</h1>
        <p class="text-2xl text-gray-600 mb-10">We install AI Receptionists for Solar Companies.</p>
        
        <div class="bg-white p-8 rounded-xl shadow-lg text-left mb-10">
            <h2 class="text-2xl font-bold mb-4 text-red-600">The Pain</h2>
            <ul class="list-disc pl-6 space-y-2">
                <li>Speed to lead is too slow.</li>
                <li>Voicemails get ignored.</li>
                <li>Leads are expensive ($50+).</li>
            </ul>
        </div>
        
        <a href="https://calendly.com/aiserviceco/audit" class="bg-amber-500 text-white text-xl font-bold py-4 px-10 rounded-full hover:bg-amber-600">
            Get Free Solar AI Audit
        </a>
    </div>
</body>
</html>
    """
    
    with open("output/solar_simple.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("DONE: output/solar_simple.html")

if __name__ == "__main__":
    build_solar()
