
import json

def build_hvac_campaign():
    """
    Generates the 'Spartan Sequence' (Mission 01) for Polk County HVAC.
    """
    workflow = {
        "name": "Operation Polk Cooling (HVAC)",
        "trigger": {
            "type": "contact_tag_created",
            "tag": "campaign-hvac-polk"
        },
        "actions": [
            {
                "type": "email",
                "delay": "0",
                "subject": "missed calls at {{contact.company_name}}",
                "body": (
                    "hey {{contact.first_name}}, fast question. "
                    "i just called {{contact.company_name}} and it went to voicemail. "
                    "i tested 5 other HVAC guys in lakeland and 3 of them texted me back instantly with a booking link. "
                    "you're losing jobs to them right now. i recorded a 30s video showing how to fix this. want the link?"
                )
            },
            {
                "type": "wait",
                "duration": "2h"
            },
            {
                "type": "sms",
                "body": "hey {{contact.first_name}}, sent you an email about those missed calls. let me know if you want that video. - [My Name]"
            },
            {
                "type": "wait",
                "duration": "1d"
            },
            {
                "type": "email",
                "subject": "video for {{contact.company_name}}",
                "body": (
                    "hey {{contact.first_name}}, didn't hear back, but figured this was too important. "
                    "here is that video showing how the 'Missed Call Text Back' system captures the lead before they call the next guy on google. "
                    "https://hvac.aiserviceco.com. takes 5 mins to setup."
                )
            }
        ]
    }
    
    return workflow

if __name__ == "__main__":
    campaign = build_hvac_campaign()
    with open("hvac_workflow.json", "w") as f:
        json.dump(campaign, f, indent=2)
    print("✅ Workflow generated: hvac_workflow.json")
