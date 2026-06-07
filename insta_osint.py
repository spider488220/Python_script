
import sys
import os
import json
import time
import http.client
from colorama import Fore, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

init(autoreset=True)
console = Console()

banner = '''
██╗███╗   ██╗███████╗████████╗ █████╗ 
██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗
██║██╔██╗ ██║███████╗   ██║   ███████║
██║██║╚██╗██║╚════██║   ██║   ██╔══██║
██║██║ ╚████║███████║   ██║   ██║  ██║
╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝
'''

os.system('cls' if os.name == 'nt' else 'clear')
for line in banner.splitlines():
    print(Fore.CYAN + Style.BRIGHT + line)
    time.sleep(0.01)

console.print(Panel.fit('[bold magenta]PRIVATE ID INTELLIGENCE[/bold magenta]\n[green]ADVANCED DATA PARSING SYSTEM LIVE[/green]', border_style='bright_blue'))

if len(sys.argv) < 2:
    console.print('\n[bold red]USAGE:[/bold red] python insta.py <username>\n')
    sys.exit()

username = sys.argv[1]

# API कनेक्शन सेटअप
conn = http.client.HTTPSConnection('flashapi1.p.rapidapi.com')
headers = {
    'x-rapidapi-key': 'daaca6cabamshf95662099030c07p13eb80jsn54f756fd294d',
    'x-rapidapi-host': 'flashapi1.p.rapidapi.com',
    'Content-Type': 'application/json' 
}

endpoint = f'/ig/info_username/?user={username}&nocors=false'
conn.request('GET', endpoint, headers=headers)
res = conn.getresponse()
data = res.read()

try:
    # JSON डेटा लोड करना
    json_data = json.loads(data.decode('utf-8'))
    user = json_data.get('user', {})
    
    if user:
        console.print(Panel.fit(f'[bold green]TARGET:[/bold green] {username}\n[bold cyan]STATUS:[/bold cyan] EXTRACTING DEEP INTELLIGENCE', border_style='green'))
        
        # ----------------------------------------
        # टेबल 1: बुनियादी प्रोफाइल डेटा (Basic Info)
        # ----------------------------------------
        table_basic = Table(title="📊 Basic Profile Intelligence", border_style="cyan", show_lines=True)
        table_basic.add_column("Property", style="bold yellow")
        table_basic.add_column("Value", style="white")
        
        table_basic.add_row("Instagram Unique ID (PK)", str(user.get("pk_id" or "id", "N/A")))
        
        full_name = user.get("full_name", "N/A")
        if "Access delayed" in full_name:
            full_name = "[red]Hidden (Private/Delayed)[/red]"
        table_basic.add_row("Full Name Status", full_name)
        
        table_basic.add_row("Biography", str(user.get("biography", "N/A")))
        table_basic.add_row("Follower Count", str(user.get("follower_count", 0)))
        table_basic.add_row("Following Count", str(user.get("following_count", 0)))
        table_basic.add_row("Mutual Followers", str(user.get("mutual_followers_count", 0)))
        
        console.print(table_basic)
        console.print("\n")

        # ----------------------------------------
        # टेबल 2: मेटा और फेसबुक लिंकिंग डेटा (Meta & Meta-ID Info)
        # ----------------------------------------
        table_meta = Table(title="🔗 Meta & Linked Accounts Data", border_style="magenta", show_lines=True)
        table_meta.add_column("Linked Param", style="bold magenta")
        table_meta.add_column("Internal ID / Value", style="white")
        
        table_meta.add_row("Facebook ID v2 (fbid_v2)", str(user.get("fbid_v2", "N/A")))
        table_meta.add_row("Interop Messaging FBID", str(user.get("interop_messaging_user_fbid", "N/A")))
        table_meta.add_row("WhatsApp Linked?", "✅ Yes" if user.get("is_whatsapp_linked") else "❌ No")
        table_meta.add_row("FB Page Link on Profile?", "✅ Yes" if user.get("show_fb_page_link_on_profile") else "❌ No")
        table_meta.add_row("Facebook Onboarded Charity?", "✅ Yes" if user.get("is_facebook_onboarded_charity") else "❌ No")
        table_meta.add_row("Threads Profile URI", str(user.get("threads_profile_glyph_url", "N/A")))
        
        console.print(table_meta)
        console.print("\n")

        # ----------------------------------------
        # टेबल 3: प्राइवेसी और एडवांस्ड सेटिंग्स (Privacy & Meta Verified)
        # ----------------------------------------
        table_settings = Table(title="🔒 Privacy, Badges & Verification Status", border_style="green", show_lines=True)
        table_settings.add_column("Setting Metric", style="bold green")
        table_settings.add_column("Configuration", style="white")
        
        table_settings.add_row("Account Type", "Professional/Business" if user.get("account_type") == 1 or user.get("professional_conversion_suggested_account_type") == 2 else "Personal Account")
        table_settings.add_row("Is Private Account?", "🔒 True" if user.get("is_private") else "🌐 False (Public)")
        table_settings.add_row("Account Transparency Visible?", "✅ True" if user.get("show_account_transparency_details") else "❌ False")
        table_settings.add_row("Has Blue Badge (Verified)?", "✅ Verified" if user.get("show_blue_badge_on_main_profile") or user.get("is_verified") else "❌ Not Verified")
        table_settings.add_row("Is New to Instagram?", "⏳ Yes" if user.get("is_new_to_instagram") else "🚫 No (Old Account)")
        table_settings.add_row("Anonymous Profile Picture?", "👤 Yes" if user.get("has_anonymous_profile_picture") else "🖼️ No (Custom Avatar)")
        table_settings.add_row("Is Memorialized Account?", "⚠️ Yes (User Deceased)" if user.get("is_memorialized") else "✅ No (Active)")
        
        console.print(table_settings)
        console.print("\n")

        # ----------------------------------------
        # प्रोफाइल पिक्चर आउटपुट (HD URL Extraction)
        # ----------------------------------------
        pic_info = user.get("hd_profile_pic_url_info", {})
        pic_url = pic_info.get("url", "N/A")
        
        console.print(Panel(f"[bold gold1]📸 EXTRACTED HD PROFILE IMAGE URL ({pic_info.get('width', 810)}x{pic_info.get('height', 810)}):[/bold gold1]\n\n[blue]{pic_url}[/blue]", title="Media Assets", border_style="yellow"))
        
    else:
        console.print('[bold red]❌ Response received but "user" index missing or empty.[/bold red]')

except json.JSONDecodeError:
    console.print('[bold red]❌ Failed to parse data. Raw output instead:[/bold red]')
    print(data.decode('utf-8'))
