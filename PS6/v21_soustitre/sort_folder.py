import os
import shutil
import datetime
from collections import Counter
from colorama import Fore, Style, init
from tqdm import tqdm
import sys

init(autoreset=True)

folder = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.realpath(__file__))
actual_dir = os.listdir(folder)

ext_to_dir = {
    '.png': 'Images',
    '.jpg': 'Images',
    '.jpeg': 'Images',
    '.webp': 'Images',
    '.gif': 'Images',
    '.bmp': 'Images',
    '.tiff': 'Images',
    '.ico': 'Images',
    '.svg': 'Images',
    '.xls': 'Excel',
    '.xlsx': 'Excel',
    '.csv': 'Excel',
    '.doc': 'Documents',
    '.docx': 'Documents',
    '.pdf': 'Documents',
    '.zip': 'Zip',
    '.rar': 'Zip',
    '.7z': 'Zip',
    '.mp3': 'Music',
    '.wav': 'Music',
    '.ogg': 'Music',
    '.mp4': 'Videos',
    '.avi': 'Videos',
    '.mov': 'Videos',
    '.exe': 'Installers',
    '.msi': 'Installers',
    '.py': 'Scripts',
    '.html': 'Scripts',
    '.css': 'Scripts',
    '.js': 'Scripts',
    '.json': 'Scripts',
    '.php': 'Scripts',
    '.twig': 'Scripts',
    '.local': 'Scripts',
    '.log': 'Logs',
    '.txt': 'Text',
    '.md': 'Text',
    '.db': 'Databases',
    '.sql': 'Databases'
}

stats = Counter()

emojis = {
    'Images': '🖼️',
    'Excel': '📊',
    'Documents': '📄',
    'Zip': '🗜️',
    'Music': '🎵',
    'Videos': '🎬',
    'Installers': '💾',
    'Scripts': '💻',
    'Logs': '📋',
    'Text': '📝',
    'Databases': '🗄️'
}

for file in tqdm(actual_dir, desc="Tri en cours", ncols=100):
    file_path = os.path.join(folder, file)
    if os.path.isfile(file_path):
        ext = os.path.splitext(file)[1].lower()
        if ext in ext_to_dir:
            dir_name = ext_to_dir[ext]
            emoji = emojis.get(dir_name, '')
            dir_path = os.path.join(folder, dir_name)
            file_date = os.path.getmtime(file_path)
            folder_date = datetime.date.fromtimestamp(file_date).strftime('%m-%Y')
            date_path = os.path.join(dir_path, folder_date)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            if not os.path.exists(date_path):
                os.mkdir(date_path)
            shutil.move(file_path, os.path.join(date_path, file))
            stats[dir_name] += 1
            print(Fore.GREEN + f"{emoji} Déplacé: {file} → {dir_name}/{folder_date}/")
        
        else:
            dir_name = 'Autres'
            emoji = '❔'
            ext_folder = os.path.join(folder, dir_name, ext[1:] or 'sans_extension')
            os.makedirs(ext_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(ext_folder, file))
            stats[dir_name] += 1
            print(Fore.YELLOW + f"{emoji} Déplacé: {file} → {dir_name}/{ext[1:]}/")


print(Style.BRIGHT + "\nRésumé du tri :")
for k, v in stats.items():
    print(f"{emojis.get(k, '')} {k}: {v} fichier(s)")
print(Fore.CYAN + "\n🎉 Tri terminé ! Bravo ! 🎉")

