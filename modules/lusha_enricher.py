"""
Lusha API Integration for Lead Enrichment.
Provides verified emails and direct dial phone numbers.
"""
import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

LUSHA_API_KEY = os.getenv("LUSHA_API_KEY")
LUSHA_BASE_URL = "https://api.lusha.com"


class LushaEnricher:
    """Enrich leads with verified contact information from Lusha."""
    
    def __init__(self):
        self.api_key = LUSHA_API_KEY
        self.headers = {
            "api_key": self.api_key,
            "Content-Type": "application/json"
        }
        self.credits_used = 0
    
    def enrich_person(
        self,
        first_name: str,
        last_name: str,
        company: str,
        property_name: str = "email"  # email, phoneNumbers, or both
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich a person's contact info using Lusha.
        
        Args:
            first_name: Person's first name
            last_name: Person's last name
            company: Company name or domain
            property_name: What to retrieve (email, phoneNumbers, or both)
        
        Returns:
            Dict with enriched data or None if not found
        """
        try:
            params = {
                "firstName": first_name,
                "lastName": last_name,
                "company": company,
                "property": property_name
            }
            
            response = requests.get(
                f"{LUSHA_BASE_URL}/person",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.credits_used += 1
                print(f"🔍 [LUSHA] Enriched: {first_name} {last_name} @ {company}")
                return {
                    "email": data.get("emailAddresses", [{}])[0].get("email"),
                    "phone": data.get("phoneNumbers", [{}])[0].get("localizedNumber"),
                    "linkedin": data.get("socialNetworks", {}).get("linkedin"),
                    "title": data.get("title"),
                    "full_data": data
                }
            elif response.status_code == 404:
                print(f"🔍 [LUSHA] No data found for {first_name} {last_name}")
                return None
            elif response.status_code == 402:
                print(f"🔍 [LUSHA] ⚠️ Out of credits!")
                return None
            else:
                print(f"🔍 [LUSHA] Error: {response.status_code} - {response.text[:100]}")
                return None
                
        except Exception as e:
            print(f"🔍 [LUSHA] Exception: {e}")
            return None
    
    def enrich_company(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get company information from Lusha.
        
        Args:
            domain: Company domain (e.g., 'example.com')
        
        Returns:
            Dict with company data or None
        """
        try:
            response = requests.get(
                f"{LUSHA_BASE_URL}/company",
                headers=self.headers,
                params={"domain": domain},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🏢 [LUSHA] Company enriched: {domain}")
                return {
                    "name": data.get("name"),
                    "industry": data.get("industry"),
                    "size": data.get("size"),
                    "location": data.get("location"),
                    "full_data": data
                }
            else:
                return None
                
        except Exception as e:
            print(f"🏢 [LUSHA] Company lookup error: {e}")
            return None
    
    def get_credits_balance(self) -> Optional[int]:
        """Check remaining Lusha credits."""
        try:
            response = requests.get(
                f"{LUSHA_BASE_URL}/account",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("credits", {}).get("remaining")
        except:
            pass
        return None


# Singleton for easy import
lusha = LushaEnricher()


def enrich_with_lusha(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to enrich a lead dict with Lusha data.
    Falls back gracefully if Lusha fails.
    """
    if not lead.get("first_name") or not lead.get("company"):
        return lead
    
    result = lusha.enrich_person(
        first_name=lead.get("first_name", ""),
        last_name=lead.get("last_name", ""),
        company=lead.get("company", ""),
        property_name="both"
    )
    
    if result:
        lead["lusha_email"] = result.get("email")
        lead["lusha_phone"] = result.get("phone")
        lead["lusha_linkedin"] = result.get("linkedin")
        lead["enriched_by"] = "lusha"
    
    return lead


if __name__ == "__main__":
    print("🔍 Testing Lusha Integration...")
    
    # Check credits
    credits = lusha.get_credits_balance()
    print(f"   Credits remaining: {credits}")
    
    # Test enrichment (uses 1 credit)
    # result = lusha.enrich_person("Elon", "Musk", "Tesla")
    # print(f"   Test result: {result}")
    
    print("✅ Lusha module ready!")
