import sys
import time
import os
import json
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
    time.sleep(0.02)

console.print(Panel.fit('[bold magenta]PRIVATE ID INTELLIGENCE[/bold magenta]\n[green]TARGET ACQUISITION SYSTEM INITIALIZED[/green]', border_style='bright_blue'))
time.sleep(0.5)

if len(sys.argv) < 2:
    console.print('\n[bold red]USAGE:[/bold red] python insta.py <username>\n')
    sys.exit()

username = sys.argv[1]

# API कनेक्शन
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
        console.print(Panel.fit(f'[bold green]TARGET:[/bold green] {username}\n[bold cyan]STATUS:[/bold cyan] ALL DATA EXTRACTED', border_style='green'))
        
        # 1. मुख्य डेटा की सुंदर टेबल
        table = Table(title="🎯 Main Intelligence", border_style="bright_magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("User ID", str(user.get("id", "N/A")))
        table.add_row("Full Name", str(user.get("full_name", "N/A")))
        table.add_row("Biography", str(user.get("biography", "N/A")))
        table.add_row("Followers", str(user.get("follower_count", 0)))
        table.add_row("Following", str(user.get("following_count", 0)))
        table.add_row("Account Type", "Business/Creator" if user.get("account_type") == 2 else "Personal")
        table.add_row("Is Private?", "🔒 Yes" if user.get("is_private") else "🌐 No")
        table.add_row("Is Verified?", "✅ Yes" if user.get("is_verified") else "❌ No")
        
        console.print(table)
        
        # 2. पूरा छुपा हुआ RAW डेटा (Full Data Dump)
        console.print('\n[bold yellow]🧬 SHOWING COMPLETE RAW DATA DISCOVERED BY API:[/bold yellow]\n')
        
        # json.dumps इसे साफ़-साफ़Indent करके दिखाएगा ताकि आप एक-एक लाइन पढ़ सकें
        formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
        print(Fore.GREEN + formatted_json)
        
    else:
        console.print('[yellow]⚠ No user data found in the response.[/yellow]')

except json.JSONDecodeError:
    console.print('[red]❌ Failed to parse API response. Raw response below:[/red]')
    print(Fore.YELLOW + data.decode('utf-8'))
