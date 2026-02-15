import os
import sys
import platform
import subprocess

def run_build():
    app_name = "DiscordTerminator"
    main_script = "desktop_app.py"
    
    # Path separator for PyInstaller --add-data differs by OS
    # Windows uses ; Linux/Mac use :
    sep = ";" if platform.system() == "Windows" else ":"
    
    # Data to include: the web directory (contains backend logic and frontend build)
    # Format: "source_dir;target_dir" or "source_dir:target_dir"
    add_data = f"web{sep}web"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--name={app_name}",
        f"--add-data={add_data}",
        # Clear previous builds
        "--clean",
        # Use windowed mode for Mac/Windows
        "--windowed",
        # Exclude GI to avoid build errors on some Linux distros (using QT instead)
        "--exclude-module=gi",
        # Ensure webview requirements and Qt plugins are collected
        "--collect-all=webview",
        "--collect-all=PyQt5",
    ]
    
    # Add icon if it exists
    icon_path = "icon.png"
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    
    # Hidden imports that are often missed
    hidden_imports = [
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.loop.auto",
        "uvicorn.loop.asyncio",
        "uvicorn.loop.uvloop",
        "uvicorn.logging",
    ]
    
    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")
        
    cmd.append(main_script)
    
    print(f"Running build for {platform.system()}...")
    print(" ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful!")
        print(f"Executable can be found in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure current directory is the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_build()
