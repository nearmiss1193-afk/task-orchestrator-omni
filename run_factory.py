
from modules.media.video_factory import create_ken_burns_loop
import os

if os.path.exists("assets/generated/social_mockup.png"):
    create_ken_burns_loop('assets/generated/social_mockup.png', 'assets/loop_social.mp4')
else:
    print("Social Mockup missing")

if os.path.exists("assets/generated/ads_mockup.png"):
    create_ken_burns_loop('assets/generated/ads_mockup.png', 'assets/loop_ads.mp4')
