import PyInstaller.__main__
import os

# Check if directories exist before adding them
data_files = []

# Add images if it exists
if os.path.exists('images'):
    data_files.append('--add-data=images;images')

# Add config if it exists
if os.path.exists('config'):
    data_files.append('--add-data=config;config')

# Build the arguments list
args = [
    'src/main.py',
    '--onedir',
    '--windowed',
    '--name=HaywardTechSuite',
    '--uac-admin',
    '--hidden-import=psutil',
    '--hidden-import=yaml',
    '--hidden-import=customtkinter',
    '--clean',
] + data_files

# Add icon if it exists (check common locations)
icon_paths = ['icon.ico', 'images/icon.ico', 'src/icon.ico']
for icon_path in icon_paths:
    if os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
        print(f"Using icon: {icon_path}")
        break

print("Building with PyInstaller...")
print(f"Arguments: {args}")

PyInstaller.__main__.run(args)

print("\n✅ Build complete! Check the 'dist' folder for HaywardTechSuite.exe")
