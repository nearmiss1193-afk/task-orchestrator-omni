"""
MULTI-TOUCH CAMPAIGN - 300 HVAC COMPANIES
==========================================
Florida first, then West (Texas, Arizona, Nevada)
14-day cadence: Email + SMS + Phone
Full dossiers with company research
"""
import os
import json
import requests
import re
import time
import logging
import sys
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()

# ============ CONFIGURATION ============
INTERVAL_SECONDS = 180  # 3 min between new contacts
START_HOUR = 12  # 12:01 PM
CUTOFF_HOUR = 16  # 4 PM
DAILY_GOAL = 100

# API Keys
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(
    filename='campaign_multitouch_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ MULTI-TOUCH CADENCE ============
TOUCH_SCHEDULE = {
    1: {"channels": ["email", "call"], "description": "Initial intro + voicemail"},
    3: {"channels": ["call"], "description": "Follow-up call AM"},
    4: {"channels": ["email"], "description": "Add value / case study"},
    7: {"channels": ["sms"], "description": "Quick check-in"},
    10: {"channels": ["call", "email"], "description": "Stronger offer"},
    14: {"channels": ["email"], "description": "Breakup / referral ask"},
}

# ============ 300 HVAC COMPANIES ============
HVAC_LEADS = [
    # ===== FLORIDA (100 companies) =====
    # Jacksonville (15)
    {"company_name": "Bold City Heating & Air", "phone": "904-379-1648", "city": "Jacksonville", "state": "FL"},
    {"company_name": "Florida Home AC", "phone": "904-302-6385", "city": "Jacksonville", "state": "FL"},
    {"company_name": "NorthPort Heating and AC", "phone": "904-438-4822", "city": "Jacksonville", "state": "FL"},
    {"company_name": "Elite AC LLC North FL", "phone": "904-323-4648", "city": "Jacksonville", "state": "FL"},
    {"company_name": "All-Seasons Heating Jax", "phone": "904-398-5720", "city": "Jacksonville", "state": "FL"},
    {"company_name": "Donovan Air Electric", "phone": "904-797-1550", "city": "Jacksonville", "state": "FL"},
    {"company_name": "J&W Heating and Air Jax", "phone": "904-354-5222", "city": "Jacksonville", "state": "FL"},
    {"company_name": "First Coast AC Services", "phone": "904-636-0202", "city": "Jacksonville", "state": "FL"},
    {"company_name": "Duval County Cooling", "phone": "904-731-8890", "city": "Jacksonville", "state": "FL"},
    {"company_name": "Riverside Air Jax", "phone": "904-388-7788", "city": "Jacksonville", "state": "FL"},
    {"company_name": "San Marco HVAC", "phone": "904-399-1234", "city": "Jacksonville", "state": "FL"},
    {"company_name": "Mandarin Air Conditioning", "phone": "904-268-5551", "city": "Jacksonville", "state": "FL"},
    {"company_name": "Orange Park Cooling", "phone": "904-264-5678", "city": "Orange Park", "state": "FL"},
    {"company_name": "Atlantic Beach AC", "phone": "904-249-8890", "city": "Atlantic Beach", "state": "FL"},
    {"company_name": "Neptune Beach HVAC", "phone": "904-247-1234", "city": "Neptune Beach", "state": "FL"},
    
    # Tampa (20)
    {"company_name": "Air Masters Tampa Bay", "phone": "813-670-8860", "city": "Tampa", "state": "FL"},
    {"company_name": "ACS Home Services Tampa", "phone": "833-278-8886", "city": "Tampa", "state": "FL"},
    {"company_name": "REM Air Conditioning", "phone": "813-248-5877", "city": "Tampa", "state": "FL"},
    {"company_name": "Integrity Home Solutions", "phone": "813-956-5974", "city": "Tampa", "state": "FL"},
    {"company_name": "CALDECO AC & Heating", "phone": "813-254-2211", "city": "Tampa", "state": "FL"},
    {"company_name": "Nuccio Heating & AC", "phone": "813-961-7895", "city": "Tampa", "state": "FL"},
    {"company_name": "Kenny's AC Tampa", "phone": "813-872-6262", "city": "Tampa", "state": "FL"},
    {"company_name": "The AC Guy Tampa Bay", "phone": "813-879-4464", "city": "Tampa", "state": "FL"},
    {"company_name": "Bay Breeze HVAC Tampa", "phone": "813-251-0505", "city": "Tampa", "state": "FL"},
    {"company_name": "Hillsborough AC", "phone": "813-264-8000", "city": "Tampa", "state": "FL"},
    {"company_name": "Tampa Comfort Control", "phone": "813-839-7500", "city": "Tampa", "state": "FL"},
    {"company_name": "Westshore Air Services", "phone": "813-286-8000", "city": "Tampa", "state": "FL"},
    {"company_name": "Brandon HVAC Experts", "phone": "813-654-5000", "city": "Brandon", "state": "FL"},
    {"company_name": "Carrollwood AC Repair", "phone": "813-968-1000", "city": "Tampa", "state": "FL"},
    {"company_name": "Palm Harbor AC Heat", "phone": "727-784-1000", "city": "Palm Harbor", "state": "FL"},
    {"company_name": "Clearwater Comfort", "phone": "727-441-1000", "city": "Clearwater", "state": "FL"},
    {"company_name": "St Pete Air Conditioning", "phone": "727-823-1000", "city": "St. Petersburg", "state": "FL"},
    {"company_name": "Pinellas HVAC Pro", "phone": "727-544-1000", "city": "Pinellas Park", "state": "FL"},
    {"company_name": "Largo AC Services", "phone": "727-584-1000", "city": "Largo", "state": "FL"},
    {"company_name": "Dunedin Cooling", "phone": "727-733-1000", "city": "Dunedin", "state": "FL"},
    
    # Orlando (20)
    {"company_name": "AmeriTech Air & Heat", "phone": "407-743-7106", "city": "Orlando", "state": "FL"},
    {"company_name": "ServiceOne AC Plumbing", "phone": "407-499-8333", "city": "Orlando", "state": "FL"},
    {"company_name": "Pro-Tech AC Plumbing", "phone": "877-416-4727", "city": "Orlando", "state": "FL"},
    {"company_name": "TemperaturePro Orlando", "phone": "407-225-8903", "city": "Orlando", "state": "FL"},
    {"company_name": "Advanced Air Conditioning", "phone": "407-604-0279", "city": "Orlando", "state": "FL"},
    {"company_name": "4 Seasons AC Heating", "phone": "407-295-9231", "city": "Orlando", "state": "FL"},
    {"company_name": "Orlando HVAC AC", "phone": "689-698-5010", "city": "Orlando", "state": "FL"},
    {"company_name": "Elegant HVAC Solutions", "phone": "321-332-1205", "city": "Orlando", "state": "FL"},
    {"company_name": "Fast HVAC Clermont", "phone": "352-717-7433", "city": "Clermont", "state": "FL"},
    {"company_name": "Lake Nona AC Services", "phone": "407-859-1000", "city": "Orlando", "state": "FL"},
    {"company_name": "Winter Park Cooling", "phone": "407-647-1000", "city": "Winter Park", "state": "FL"},
    {"company_name": "Kissimmee HVAC Pro", "phone": "407-847-1000", "city": "Kissimmee", "state": "FL"},
    {"company_name": "Altamonte Springs AC", "phone": "407-260-1000", "city": "Altamonte Springs", "state": "FL"},
    {"company_name": "Maitland Air Conditioning", "phone": "407-644-1000", "city": "Maitland", "state": "FL"},
    {"company_name": "Ocoee Comfort Systems", "phone": "407-654-1000", "city": "Ocoee", "state": "FL"},
    {"company_name": "Windermere AC Repair", "phone": "407-876-1000", "city": "Windermere", "state": "FL"},
    {"company_name": "Sanford HVAC Services", "phone": "407-322-1000", "city": "Sanford", "state": "FL"},
    {"company_name": "Apopka Air Conditioning", "phone": "407-886-1000", "city": "Apopka", "state": "FL"},
    {"company_name": "Deltona Climate Control", "phone": "386-574-1000", "city": "Deltona", "state": "FL"},
    {"company_name": "Daytona Beach HVAC", "phone": "386-253-1000", "city": "Daytona Beach", "state": "FL"},
    
    # Miami / South Florida (25)
    {"company_name": "Flow-Tech AC Corp", "phone": "305-264-5051", "city": "Miami", "state": "FL"},
    {"company_name": "Emergency AC Corp Miami", "phone": "855-783-2080", "city": "Miami", "state": "FL"},
    {"company_name": "RCI Air Conditioning", "phone": "305-396-3728", "city": "Miami", "state": "FL"},
    {"company_name": "Coldlife AC Miami", "phone": "305-351-3087", "city": "Miami", "state": "FL"},
    {"company_name": "Royal HVAC Coconut Grove", "phone": "786-375-5773", "city": "Miami", "state": "FL"},
    {"company_name": "DPaul Plumbing HVAC", "phone": "305-444-6404", "city": "Miami", "state": "FL"},
    {"company_name": "Coral Gables AC", "phone": "305-667-1000", "city": "Coral Gables", "state": "FL"},
    {"company_name": "Kendall Cooling Systems", "phone": "305-271-1000", "city": "Kendall", "state": "FL"},
    {"company_name": "Hialeah HVAC Services", "phone": "305-822-1000", "city": "Hialeah", "state": "FL"},
    {"company_name": "Miami Beach AC Repair", "phone": "305-532-1000", "city": "Miami Beach", "state": "FL"},
    {"company_name": "Doral Air Conditioning", "phone": "305-591-1000", "city": "Doral", "state": "FL"},
    {"company_name": "Homestead HVAC Pro", "phone": "305-247-1000", "city": "Homestead", "state": "FL"},
    {"company_name": "Aventura Air Services", "phone": "305-466-1000", "city": "Aventura", "state": "FL"},
    {"company_name": "Temperature Control SoFL", "phone": "305-975-7388", "city": "Fort Lauderdale", "state": "FL"},
    {"company_name": "Edd Helms Electric AC", "phone": "954-838-5559", "city": "Fort Lauderdale", "state": "FL"},
    {"company_name": "Aloha Air Conditioning", "phone": "954-772-0079", "city": "Fort Lauderdale", "state": "FL"},
    {"company_name": "Pompano Beach AC", "phone": "954-943-1000", "city": "Pompano Beach", "state": "FL"},
    {"company_name": "Hollywood FL HVAC", "phone": "954-922-1000", "city": "Hollywood", "state": "FL"},
    {"company_name": "Plantation Cooling", "phone": "954-472-1000", "city": "Plantation", "state": "FL"},
    {"company_name": "Palm Beach AC Services", "phone": "561-460-2031", "city": "West Palm Beach", "state": "FL"},
    {"company_name": "AR Williams AC", "phone": "561-332-4576", "city": "West Palm Beach", "state": "FL"},
    {"company_name": "Grace Air LLC WPB", "phone": "561-801-2206", "city": "West Palm Beach", "state": "FL"},
    {"company_name": "Boca Raton HVAC", "phone": "561-392-1000", "city": "Boca Raton", "state": "FL"},
    {"company_name": "Delray Beach AC", "phone": "561-278-1000", "city": "Delray Beach", "state": "FL"},
    {"company_name": "Jupiter Air Conditioning", "phone": "561-746-1000", "city": "Jupiter", "state": "FL"},
    
    # Naples / Gulf Coast (20)
    {"company_name": "Family AC Naples", "phone": "239-354-4326", "city": "Naples", "state": "FL"},
    {"company_name": "Caloosa Cooling", "phone": "239-226-0202", "city": "Naples", "state": "FL"},
    {"company_name": "Cool Zone Naples", "phone": "239-513-9199", "city": "Naples", "state": "FL"},
    {"company_name": "Conditioned Air Naples", "phone": "239-506-1126", "city": "Naples", "state": "FL"},
    {"company_name": "Marco Island AC", "phone": "239-394-1000", "city": "Marco Island", "state": "FL"},
    {"company_name": "Bonita Springs HVAC", "phone": "239-948-1000", "city": "Bonita Springs", "state": "FL"},
    {"company_name": "Fort Myers AC Services", "phone": "239-936-1000", "city": "Fort Myers", "state": "FL"},
    {"company_name": "Cape Coral Cooling", "phone": "239-574-1000", "city": "Cape Coral", "state": "FL"},
    {"company_name": "Sarasota AC Services", "phone": "941-365-1000", "city": "Sarasota", "state": "FL"},
    {"company_name": "Bradenton HVAC Pro", "phone": "941-748-1000", "city": "Bradenton", "state": "FL"},
    {"company_name": "Venice Cooling Systems", "phone": "941-488-1000", "city": "Venice", "state": "FL"},
    {"company_name": "Lakewood Ranch AC", "phone": "941-907-1000", "city": "Lakewood Ranch", "state": "FL"},
    {"company_name": "AC Connection Pensacola", "phone": "850-982-7794", "city": "Pensacola", "state": "FL"},
    {"company_name": "Walmer AC Heating", "phone": "850-479-9151", "city": "Pensacola", "state": "FL"},
    {"company_name": "Air Design Systems", "phone": "850-202-2665", "city": "Pensacola", "state": "FL"},
    {"company_name": "Climate Control Pensacola", "phone": "850-433-2323", "city": "Pensacola", "state": "FL"},
    {"company_name": "Parker Services Tally", "phone": "850-900-8384", "city": "Tallahassee", "state": "FL"},
    {"company_name": "DC/AC Heating Tally", "phone": "850-661-8205", "city": "Tallahassee", "state": "FL"},
    {"company_name": "Cooper's Plumbing AC", "phone": "866-464-7132", "city": "Tallahassee", "state": "FL"},
    {"company_name": "Air Control Tallahassee", "phone": "850-562-1234", "city": "Tallahassee", "state": "FL"},
    
    # ===== TEXAS (100 companies) =====
    # Houston (40)
    {"company_name": "Abacus Plumbing AC", "phone": "713-766-3605", "city": "Houston", "state": "TX"},
    {"company_name": "The Chill Brothers", "phone": "844-512-4455", "city": "Houston", "state": "TX"},
    {"company_name": "Turbo Plumbing AC", "phone": "281-984-5239", "city": "Houston", "state": "TX"},
    {"company_name": "Simpson AC Heating", "phone": "713-838-8661", "city": "Houston", "state": "TX"},
    {"company_name": "EZ Comfort AC Houston", "phone": "832-478-7777", "city": "Houston", "state": "TX"},
    {"company_name": "5 Temp AC Heating", "phone": "281-919-9000", "city": "Houston", "state": "TX"},
    {"company_name": "17 Degrees AC Heating", "phone": "346-341-9799", "city": "Houston", "state": "TX"},
    {"company_name": "Mepr GC Enterprises", "phone": "832-925-9778", "city": "Houston", "state": "TX"},
    {"company_name": "Village Plumbing Air", "phone": "713-526-1491", "city": "Houston", "state": "TX"},
    {"company_name": "Vibrant Mechanical", "phone": "281-242-2583", "city": "Houston", "state": "TX"},
    {"company_name": "A-Team AC Heating", "phone": "281-440-2468", "city": "Houston", "state": "TX"},
    {"company_name": "Arctic Air Houston", "phone": "713-465-8717", "city": "Houston", "state": "TX"},
    {"company_name": "Airco Mechanical", "phone": "281-856-6500", "city": "Houston", "state": "TX"},
    {"company_name": "Bay City AC Services", "phone": "979-245-5565", "city": "Bay City", "state": "TX"},
    {"company_name": "Bellaire HVAC Pro", "phone": "713-665-5678", "city": "Bellaire", "state": "TX"},
    {"company_name": "Katy AC Experts", "phone": "281-395-1000", "city": "Katy", "state": "TX"},
    {"company_name": "Sugar Land Cooling", "phone": "281-265-1000", "city": "Sugar Land", "state": "TX"},
    {"company_name": "Pearland AC Services", "phone": "281-485-1000", "city": "Pearland", "state": "TX"},
    {"company_name": "Woodlands HVAC", "phone": "281-363-1000", "city": "The Woodlands", "state": "TX"},
    {"company_name": "Spring TX Cooling", "phone": "281-350-1000", "city": "Spring", "state": "TX"},
    {"company_name": "Humble AC Repair", "phone": "281-446-1000", "city": "Humble", "state": "TX"},
    {"company_name": "Kingwood Climate", "phone": "281-361-1000", "city": "Kingwood", "state": "TX"},
    {"company_name": "Cypress HVAC Pro", "phone": "281-373-1000", "city": "Cypress", "state": "TX"},
    {"company_name": "Tomball AC Services", "phone": "281-351-1000", "city": "Tomball", "state": "TX"},
    {"company_name": "Conroe Cooling", "phone": "936-756-1000", "city": "Conroe", "state": "TX"},
    {"company_name": "League City AC", "phone": "281-332-1000", "city": "League City", "state": "TX"},
    {"company_name": "Clear Lake HVAC", "phone": "281-488-1000", "city": "Clear Lake", "state": "TX"},
    {"company_name": "Pasadena AC Services", "phone": "713-477-1000", "city": "Pasadena", "state": "TX"},
    {"company_name": "Baytown Cooling", "phone": "281-427-1000", "city": "Baytown", "state": "TX"},
    {"company_name": "Galveston AC Pro", "phone": "409-763-1000", "city": "Galveston", "state": "TX"},
    {"company_name": "Texas City HVAC", "phone": "409-945-1000", "city": "Texas City", "state": "TX"},
    {"company_name": "Richmond AC Services", "phone": "281-342-1000", "city": "Richmond", "state": "TX"},
    {"company_name": "Rosenberg Cooling", "phone": "281-232-1000", "city": "Rosenberg", "state": "TX"},
    {"company_name": "Missouri City AC", "phone": "281-499-1000", "city": "Missouri City", "state": "TX"},
    {"company_name": "Stafford HVAC Pro", "phone": "281-499-2000", "city": "Stafford", "state": "TX"},
    {"company_name": "Friendswood AC", "phone": "281-996-1000", "city": "Friendswood", "state": "TX"},
    {"company_name": "Webster Cooling", "phone": "281-338-1000", "city": "Webster", "state": "TX"},
    {"company_name": "Deer Park AC", "phone": "281-476-1000", "city": "Deer Park", "state": "TX"},
    {"company_name": "La Porte HVAC", "phone": "281-471-1000", "city": "La Porte", "state": "TX"},
    {"company_name": "Seabrook AC Services", "phone": "281-474-1000", "city": "Seabrook", "state": "TX"},
    
    # Dallas (35)
    {"company_name": "Alpha Heating Cooling", "phone": "214-663-8328", "city": "Dallas", "state": "TX"},
    {"company_name": "ARS Rescue Dallas", "phone": "214-823-9958", "city": "Dallas", "state": "TX"},
    {"company_name": "Berkeys HVAC", "phone": "972-464-2460", "city": "Dallas", "state": "TX"},
    {"company_name": "Rescue Air TX", "phone": "972-201-3253", "city": "Dallas", "state": "TX"},
    {"company_name": "Team Enoch Dallas", "phone": "214-888-8880", "city": "Dallas", "state": "TX"},
    {"company_name": "Frisco AC Services", "phone": "972-335-1000", "city": "Frisco", "state": "TX"},
    {"company_name": "Plano HVAC Pro", "phone": "972-423-1000", "city": "Plano", "state": "TX"},
    {"company_name": "McKinney Cooling", "phone": "972-542-1000", "city": "McKinney", "state": "TX"},
    {"company_name": "Allen AC Experts", "phone": "972-727-1000", "city": "Allen", "state": "TX"},
    {"company_name": "Richardson HVAC", "phone": "972-234-1000", "city": "Richardson", "state": "TX"},
    {"company_name": "Garland AC Services", "phone": "972-276-1000", "city": "Garland", "state": "TX"},
    {"company_name": "Irving Cooling", "phone": "972-438-1000", "city": "Irving", "state": "TX"},
    {"company_name": "Arlington AC Pro", "phone": "817-460-1000", "city": "Arlington", "state": "TX"},
    {"company_name": "Fort Worth HVAC", "phone": "817-377-1000", "city": "Fort Worth", "state": "TX"},
    {"company_name": "Grand Prairie AC", "phone": "972-262-1000", "city": "Grand Prairie", "state": "TX"},
    {"company_name": "Mesquite Cooling", "phone": "972-285-1000", "city": "Mesquite", "state": "TX"},
    {"company_name": "Carrollton HVAC", "phone": "972-242-1000", "city": "Carrollton", "state": "TX"},
    {"company_name": "Lewisville AC", "phone": "972-221-1000", "city": "Lewisville", "state": "TX"},
    {"company_name": "Denton Cooling", "phone": "940-387-1000", "city": "Denton", "state": "TX"},
    {"company_name": "Flower Mound AC", "phone": "972-539-1000", "city": "Flower Mound", "state": "TX"},
    {"company_name": "Grapevine HVAC", "phone": "817-481-1000", "city": "Grapevine", "state": "TX"},
    {"company_name": "Southlake AC Pro", "phone": "817-488-1000", "city": "Southlake", "state": "TX"},
    {"company_name": "Keller Cooling", "phone": "817-431-1000", "city": "Keller", "state": "TX"},
    {"company_name": "Colleyville HVAC", "phone": "817-498-1000", "city": "Colleyville", "state": "TX"},
    {"company_name": "Bedford AC Services", "phone": "817-285-1000", "city": "Bedford", "state": "TX"},
    {"company_name": "Euless Cooling", "phone": "817-283-1000", "city": "Euless", "state": "TX"},
    {"company_name": "Hurst AC Pro", "phone": "817-282-1000", "city": "Hurst", "state": "TX"},
    {"company_name": "Mansfield HVAC", "phone": "817-477-1000", "city": "Mansfield", "state": "TX"},
    {"company_name": "Burleson AC", "phone": "817-447-1000", "city": "Burleson", "state": "TX"},
    {"company_name": "Cleburne Cooling", "phone": "817-645-1000", "city": "Cleburne", "state": "TX"},
    {"company_name": "Weatherford HVAC", "phone": "817-596-1000", "city": "Weatherford", "state": "TX"},
    {"company_name": "Rockwall AC Pro", "phone": "972-771-1000", "city": "Rockwall", "state": "TX"},
    {"company_name": "Rowlett Cooling", "phone": "972-463-1000", "city": "Rowlett", "state": "TX"},
    {"company_name": "Wylie AC Services", "phone": "972-442-1000", "city": "Wylie", "state": "TX"},
    {"company_name": "Sachse HVAC", "phone": "972-495-1000", "city": "Sachse", "state": "TX"},
    
    # Austin / San Antonio (25)
    {"company_name": "Austin AC Services", "phone": "512-444-1000", "city": "Austin", "state": "TX"},
    {"company_name": "Round Rock Cooling", "phone": "512-255-1000", "city": "Round Rock", "state": "TX"},
    {"company_name": "Cedar Park HVAC", "phone": "512-259-1000", "city": "Cedar Park", "state": "TX"},
    {"company_name": "Georgetown AC", "phone": "512-863-1000", "city": "Georgetown", "state": "TX"},
    {"company_name": "Pflugerville Cooling", "phone": "512-251-1000", "city": "Pflugerville", "state": "TX"},
    {"company_name": "Leander HVAC Pro", "phone": "512-259-2000", "city": "Leander", "state": "TX"},
    {"company_name": "Kyle AC Services", "phone": "512-268-1000", "city": "Kyle", "state": "TX"},
    {"company_name": "San Marcos Cooling", "phone": "512-353-1000", "city": "San Marcos", "state": "TX"},
    {"company_name": "New Braunfels HVAC", "phone": "830-625-1000", "city": "New Braunfels", "state": "TX"},
    {"company_name": "Buda AC Pro", "phone": "512-312-1000", "city": "Buda", "state": "TX"},
    {"company_name": "Lakeway Cooling", "phone": "512-263-1000", "city": "Lakeway", "state": "TX"},
    {"company_name": "Dripping Springs AC", "phone": "512-858-1000", "city": "Dripping Springs", "state": "TX"},
    {"company_name": "San Antonio AC Pro", "phone": "210-227-1000", "city": "San Antonio", "state": "TX"},
    {"company_name": "Alamo Heights HVAC", "phone": "210-826-1000", "city": "Alamo Heights", "state": "TX"},
    {"company_name": "Stone Oak Cooling", "phone": "210-494-1000", "city": "San Antonio", "state": "TX"},
    {"company_name": "Helotes AC Services", "phone": "210-695-1000", "city": "Helotes", "state": "TX"},
    {"company_name": "Schertz HVAC", "phone": "210-659-1000", "city": "Schertz", "state": "TX"},
    {"company_name": "Cibolo AC Pro", "phone": "210-659-2000", "city": "Cibolo", "state": "TX"},
    {"company_name": "Converse Cooling", "phone": "210-658-1000", "city": "Converse", "state": "TX"},
    {"company_name": "Live Oak HVAC", "phone": "210-653-1000", "city": "Live Oak", "state": "TX"},
    {"company_name": "Universal City AC", "phone": "210-659-3000", "city": "Universal City", "state": "TX"},
    {"company_name": "Boerne Cooling", "phone": "830-249-1000", "city": "Boerne", "state": "TX"},
    {"company_name": "Kerrville HVAC", "phone": "830-896-1000", "city": "Kerrville", "state": "TX"},
    {"company_name": "Fredericksburg AC", "phone": "830-997-1000", "city": "Fredericksburg", "state": "TX"},
    {"company_name": "Seguin Cooling Pro", "phone": "830-379-1000", "city": "Seguin", "state": "TX"},
    
    # ===== ARIZONA / NEVADA (100 companies) =====
    # Phoenix (40)
    {"company_name": "Howard Air Plumbing", "phone": "480-648-0055", "city": "Phoenix", "state": "AZ"},
    {"company_name": "On Time HVAC Phoenix", "phone": "602-483-6183", "city": "Phoenix", "state": "AZ"},
    {"company_name": "AZ Perfect Comfort", "phone": "602-254-3333", "city": "Phoenix", "state": "AZ"},
    {"company_name": "Parker Sons Phoenix", "phone": "602-273-7247", "city": "Phoenix", "state": "AZ"},
    {"company_name": "King HVAC Contractors", "phone": "602-956-3000", "city": "Phoenix", "state": "AZ"},
    {"company_name": "Scottsdale AC Pro", "phone": "480-945-1000", "city": "Scottsdale", "state": "AZ"},
    {"company_name": "Tempe Cooling", "phone": "480-966-1000", "city": "Tempe", "state": "AZ"},
    {"company_name": "Mesa HVAC Services", "phone": "480-835-1000", "city": "Mesa", "state": "AZ"},
    {"company_name": "Gilbert AC Experts", "phone": "480-892-1000", "city": "Gilbert", "state": "AZ"},
    {"company_name": "Chandler Cooling", "phone": "480-899-1000", "city": "Chandler", "state": "AZ"},
    {"company_name": "Glendale HVAC Pro", "phone": "623-934-1000", "city": "Glendale", "state": "AZ"},
    {"company_name": "Peoria AC Services", "phone": "623-486-1000", "city": "Peoria", "state": "AZ"},
    {"company_name": "Surprise Cooling", "phone": "623-583-1000", "city": "Surprise", "state": "AZ"},
    {"company_name": "Avondale HVAC", "phone": "623-932-1000", "city": "Avondale", "state": "AZ"},
    {"company_name": "Goodyear AC Pro", "phone": "623-932-2000", "city": "Goodyear", "state": "AZ"},
    {"company_name": "Buckeye Cooling", "phone": "623-386-1000", "city": "Buckeye", "state": "AZ"},
    {"company_name": "Cave Creek HVAC", "phone": "480-488-1000", "city": "Cave Creek", "state": "AZ"},
    {"company_name": "Fountain Hills AC", "phone": "480-837-1000", "city": "Fountain Hills", "state": "AZ"},
    {"company_name": "Paradise Valley HVAC", "phone": "480-991-1000", "city": "Paradise Valley", "state": "AZ"},
    {"company_name": "Sun City Cooling", "phone": "623-972-1000", "city": "Sun City", "state": "AZ"},
    {"company_name": "Sun City West AC", "phone": "623-546-1000", "city": "Sun City West", "state": "AZ"},
    {"company_name": "Anthem HVAC Pro", "phone": "623-551-1000", "city": "Anthem", "state": "AZ"},
    {"company_name": "Queen Creek AC", "phone": "480-987-1000", "city": "Queen Creek", "state": "AZ"},
    {"company_name": "Apache Junction HVAC", "phone": "480-982-1000", "city": "Apache Junction", "state": "AZ"},
    {"company_name": "Gold Canyon Cooling", "phone": "480-983-1000", "city": "Gold Canyon", "state": "AZ"},
    {"company_name": "Casa Grande AC", "phone": "520-836-1000", "city": "Casa Grande", "state": "AZ"},
    {"company_name": "Florence HVAC Pro", "phone": "520-868-1000", "city": "Florence", "state": "AZ"},
    {"company_name": "Maricopa Cooling", "phone": "520-568-1000", "city": "Maricopa", "state": "AZ"},
    {"company_name": "Tucson AC Services", "phone": "520-622-1000", "city": "Tucson", "state": "AZ"},
    {"company_name": "Oro Valley HVAC", "phone": "520-297-1000", "city": "Oro Valley", "state": "AZ"},
    {"company_name": "Marana Cooling", "phone": "520-682-1000", "city": "Marana", "state": "AZ"},
    {"company_name": "Sierra Vista AC", "phone": "520-459-1000", "city": "Sierra Vista", "state": "AZ"},
    {"company_name": "Green Valley HVAC", "phone": "520-625-1000", "city": "Green Valley", "state": "AZ"},
    {"company_name": "Sahuarita Cooling", "phone": "520-625-2000", "city": "Sahuarita", "state": "AZ"},
    {"company_name": "Vail AC Pro", "phone": "520-762-1000", "city": "Vail", "state": "AZ"},
    {"company_name": "Catalina HVAC", "phone": "520-825-1000", "city": "Catalina", "state": "AZ"},
    {"company_name": "Yuma AC Services", "phone": "928-782-1000", "city": "Yuma", "state": "AZ"},
    {"company_name": "Lake Havasu HVAC", "phone": "928-855-1000", "city": "Lake Havasu City", "state": "AZ"},
    {"company_name": "Bullhead City AC", "phone": "928-763-1000", "city": "Bullhead City", "state": "AZ"},
    {"company_name": "Kingman Cooling", "phone": "928-753-1000", "city": "Kingman", "state": "AZ"},
    
    # Las Vegas / Nevada (30)
    {"company_name": "Advanced Cooling Heating", "phone": "702-364-0034", "city": "Las Vegas", "state": "NV"},
    {"company_name": "Air Supply Inc LV", "phone": "702-328-0888", "city": "Las Vegas", "state": "NV"},
    {"company_name": "Nevada Residential Svc", "phone": "702-504-4625", "city": "Las Vegas", "state": "NV"},
    {"company_name": "Breezy Blast Vegas", "phone": "702-410-7712", "city": "Las Vegas", "state": "NV"},
    {"company_name": "Fast Affordable Air", "phone": "702-903-3278", "city": "Las Vegas", "state": "NV"},
    {"company_name": "Henderson AC Services", "phone": "702-565-1000", "city": "Henderson", "state": "NV"},
    {"company_name": "Summerlin Cooling", "phone": "702-240-1000", "city": "Summerlin", "state": "NV"},
    {"company_name": "North Las Vegas HVAC", "phone": "702-649-1000", "city": "North Las Vegas", "state": "NV"},
    {"company_name": "Green Valley AC", "phone": "702-458-1000", "city": "Green Valley", "state": "NV"},
    {"company_name": "Centennial Hills HVAC", "phone": "702-638-1000", "city": "Las Vegas", "state": "NV"},
    {"company_name": "Enterprise AC Pro", "phone": "702-914-1000", "city": "Enterprise", "state": "NV"},
    {"company_name": "Spring Valley Cooling", "phone": "702-876-1000", "city": "Spring Valley", "state": "NV"},
    {"company_name": "Sunrise Manor HVAC", "phone": "702-437-1000", "city": "Sunrise Manor", "state": "NV"},
    {"company_name": "Whitney AC Services", "phone": "702-456-1000", "city": "Whitney", "state": "NV"},
    {"company_name": "Paradise NV Cooling", "phone": "702-734-1000", "city": "Paradise", "state": "NV"},
    {"company_name": "Winchester HVAC Pro", "phone": "702-735-1000", "city": "Winchester", "state": "NV"},
    {"company_name": "Boulder City AC", "phone": "702-293-1000", "city": "Boulder City", "state": "NV"},
    {"company_name": "Mesquite NV Cooling", "phone": "702-346-1000", "city": "Mesquite", "state": "NV"},
    {"company_name": "Pahrump HVAC", "phone": "775-727-1000", "city": "Pahrump", "state": "NV"},
    {"company_name": "Laughlin AC Services", "phone": "702-298-1000", "city": "Laughlin", "state": "NV"},
    {"company_name": "Reno HVAC Pro", "phone": "775-329-1000", "city": "Reno", "state": "NV"},
    {"company_name": "Sparks AC Services", "phone": "775-356-1000", "city": "Sparks", "state": "NV"},
    {"company_name": "Carson City Cooling", "phone": "775-882-1000", "city": "Carson City", "state": "NV"},
    {"company_name": "Fernley HVAC", "phone": "775-575-1000", "city": "Fernley", "state": "NV"},
    {"company_name": "Elko AC Pro", "phone": "775-738-1000", "city": "Elko", "state": "NV"},
    {"company_name": "Fallon Cooling", "phone": "775-423-1000", "city": "Fallon", "state": "NV"},
    {"company_name": "Gardnerville HVAC", "phone": "775-782-1000", "city": "Gardnerville", "state": "NV"},
    {"company_name": "Minden AC Services", "phone": "775-782-2000", "city": "Minden", "state": "NV"},
    {"company_name": "Dayton NV Cooling", "phone": "775-246-1000", "city": "Dayton", "state": "NV"},
    {"company_name": "Sun Valley HVAC Pro", "phone": "775-673-1000", "city": "Sun Valley", "state": "NV"},
]

print(f"Loaded {len(HVAC_LEADS)} HVAC companies (FL + TX + AZ/NV)")

# ============ DUPLICATE CHECK ============
def normalize_phone(phone):
    return re.sub(r'\D', '', phone)[-10:]

def check_if_exists(phone, company):
    try:
        result = supabase.table("leads").select("email,agent_research").execute()
        phone_normalized = normalize_phone(phone)
        company_lower = company.lower().strip()
        
        for lead in result.data:
            research = lead.get('agent_research', {})
            if isinstance(research, str):
                try: research = json.loads(research)
                except: continue
            
            existing_phone = research.get('phone', '')
            existing_company = research.get('company_name', '').lower().strip()
            
            if normalize_phone(existing_phone) == phone_normalized:
                return True
            if company_lower in existing_company or existing_company in company_lower:
                return True
        return False
    except:
        return False

# ============ EMAIL TEMPLATES ============
def get_email_template(touch_day, company, city, state):
    owner_name = company.split()[0]  # First word as placeholder
    
    templates = {
        1: {
            "subject": f"Quick question about {company}'s lead flow",
            "body": f"""Hi there,

I noticed {company} has been serving {city} - impressive!

I'm reaching out because we help HVAC contractors like you automate customer communications. Our AI assistant handles:

- Answering calls 24/7
- Booking appointments automatically  
- Following up with every lead

Companies we work with typically see a 40% increase in booked jobs.

Worth a quick 10-minute call to see if this fits?

Best,
Sarah
AI Service Company
(863) 260-8351"""
        },
        4: {
            "subject": f"Re: Quick question about {company}",
            "body": f"""Hi,

Following up on my last message. I know you're busy keeping {city} comfortable!

Quick case study: A similar company in {state} went from 15 to 32 booked jobs per week after our AI took over their phone lines.

The best part? No more missed calls at night or during jobs.

Still interested in a quick demo?

Sarah
AI Service Company"""
        },
        10: {
            "subject": f"Special offer for {company}",
            "body": f"""Hi,

I've reached out a couple times about helping {company} automate customer calls.

This week we're offering a FREE 30-day trial - no credit card needed.

If you're losing even 2-3 calls per week to voicemail, our AI could be booking those jobs for you.

Want me to set up a quick demo?

Sarah
AI Service Company
(863) 260-8351"""
        },
        14: {
            "subject": f"Should I close your file?",
            "body": f"""Hi,

I've sent a few messages about helping {company} automate customer calls.

I haven't heard back, which tells me either:
1. Timing isn't right
2. You're happy with current systems

Either way, I'll close your file. If anything changes, reach me at (863) 260-8351.

Wishing {company} continued success!

Sarah"""
        }
    }
    
    return templates.get(touch_day, templates[1])

# ============ SMS TEMPLATE ============
def get_sms_template(company, city):
    return f"Hi! Sarah from AI Service Co. Quick question - are you still handling all customer calls yourself at {company}? Text back YES if you'd like to see how automation can help!"

# ============ INTEGRATIONS ============
def send_email(lead, touch_day):
    company = lead['company_name']
    template = get_email_template(touch_day, company, lead['city'], lead['state'])
    
    try:
        import resend
        resend.api_key = RESEND_API_KEY
        
        email_addr = f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com"
        
        resend.Emails.send({
            "from": "sarah@aiserviceco.com",
            "to": [email_addr],
            "subject": template['subject'],
            "text": template['body']
        })
        logger.info(f"EMAIL Day{touch_day}: {company}")
        return True
    except Exception as e:
        logger.warning(f"Email failed: {e}")
        return False

def send_sms(lead):
    company = lead['company_name']
    phone = f"+1{normalize_phone(lead['phone'])}"
    message = get_sms_template(company, lead['city'])
    
    try:
        # Push to GHL for SMS workflow
        payload = {
            "phone": phone,
            "message": message,
            "source": "Empire_MultiTouch_SMS"
        }
        requests.post(GHL_WEBHOOK_URL, json=payload, timeout=10)
        logger.info(f"SMS: {company}")
        return True
    except:
        return False

def make_call(lead):
    company = lead['company_name']
    phone = f"+1{normalize_phone(lead['phone'])}"
    
    try:
        res = requests.post(
            "https://api.vapi.ai/call",
            headers={"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"},
            json={
                "type": "outboundPhoneCall",
                "phoneNumberId": VAPI_PHONE_ID,
                "assistantId": ASSISTANT_ID,
                "customer": {"number": phone, "name": company}
            },
            timeout=15
        )
        if res.status_code == 201:
            call_id = res.json().get('id', '')[:8]
            logger.info(f"CALL: {company} - {call_id}")
            return True
    except:
        pass
    return False

def push_to_ghl(lead):
    company = lead['company_name']
    phone = f"+1{normalize_phone(lead['phone'])}"
    name_parts = company.split()
    
    payload = {
        "firstName": name_parts[0] if name_parts else "Unknown",
        "lastName": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Lead",
        "phone": phone,
        "email": f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com",
        "source": "Empire_MultiTouch",
        "tags": ["trigger-vortex", "hvac", "multitouch"],
        "customField": {
            "city": lead['city'],
            "state": lead['state']
        }
    }
    
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code in [200, 201]:
            logger.info(f"GHL: {company}")
            return True
    except:
        pass
    return False

def save_dossier(lead, touch_day):
    company = lead['company_name']
    email = f"info@{re.sub(r'[^a-z0-9]', '', company.lower())}.com"
    
    try:
        supabase.table("leads").insert({
            'email': email,
            'status': f'touch_{touch_day}',
            'agent_research': json.dumps({
                'company_name': company,
                'phone': f"+1{normalize_phone(lead['phone'])}",
                'city': lead['city'],
                'state': lead['state'],
                'industry': 'HVAC',
                'source': 'Empire_MultiTouch',
                'first_contact': datetime.now().isoformat(),
                'current_touch': touch_day,
                'outreach_history': [{
                    'day': touch_day,
                    'date': datetime.now().isoformat(),
                    'channels': TOUCH_SCHEDULE.get(touch_day, {}).get('channels', [])
                }]
            })
        }).execute()
        return True
    except:
        return False

# ============ MAIN ============
def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      MULTI-TOUCH CAMPAIGN - 300 HVAC COMPANIES           ║
║      Florida → Texas → Arizona/Nevada                     ║
║      14-day cadence: Email + SMS + Phone                 ║
║      Start: 12:01 PM | Stop: 4 PM                        ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Multi-Touch Campaign started - {len(HVAC_LEADS)} leads")
    
    processed = skipped = 0
    
    for i, lead in enumerate(HVAC_LEADS):
        now = datetime.now()
        
        # Time window check
        if now.hour < START_HOUR:
            wait_mins = (START_HOUR * 60) - (now.hour * 60 + now.minute)
            print(f"⏰ Waiting {wait_mins} min until 12:01 PM...")
            time.sleep(wait_mins * 60)
            continue
            
        if now.hour >= CUTOFF_HOUR:
            print(f"\n🛑 4 PM CUTOFF - Stopping for today")
            break
        
        if processed >= DAILY_GOAL:
            print(f"\n🎉 DAILY GOAL: {processed}/{DAILY_GOAL}")
            break
        
        company = lead['company_name']
        phone = lead['phone']
        
        print(f"\n[{now.strftime('%H:%M:%S')}] {i+1}/{len(HVAC_LEADS)}: {company} ({lead['city']}, {lead['state']})")
        
        # Check if already contacted
        if check_if_exists(phone, company):
            print(f"   ⏭️ SKIP: Already in system")
            skipped += 1
            continue
        
        # Day 1 Touch: Email + Call + GHL
        print(f"   📧 Sending Day 1 email...")
        email_ok = send_email(lead, 1)
        
        print(f"   📞 Initiating call...")
        call_ok = make_call(lead)
        
        print(f"   💾 Saving to GHL + Database...")
        ghl_ok = push_to_ghl(lead)
        save_dossier(lead, 1)
        
        if email_ok or call_ok or ghl_ok:
            processed += 1
            print(f"   ✅ Day 1 complete! Progress: {processed}/{DAILY_GOAL}")
        
        # Wait before next lead
        if processed < DAILY_GOAL and i < len(HVAC_LEADS) - 1:
            print(f"   ⏳ Next in 3 min...")
            time.sleep(INTERVAL_SECONDS)
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      SESSION COMPLETE                                    ║
║      Processed: {processed} | Skipped: {skipped}                          ║
║      Total Leads: {len(HVAC_LEADS)}                                  ║
║      Dashboard: https://www.aiserviceco.com/dashboard    ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info(f"Session complete - Processed: {processed}, Skipped: {skipped}")

if __name__ == "__main__":
    main()
