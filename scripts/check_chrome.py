#!/usr/bin/env python
"""
Script para verificar si Chrome está instalado y proporcionar instrucciones.
"""

import subprocess
import sys
import platform


def check_chrome_installed():
    """Verifica si Chrome está instalado en el sistema."""
    print("🔍 Verificando instalación de Chrome...\n")

    chrome_paths = {
        'Linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ],
        'Darwin': [  # macOS
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        ],
        'Windows': [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
        ]
    }

    system = platform.system()
    paths_to_check = chrome_paths.get(system, chrome_paths['Linux'])

    import os
    for path in paths_to_check:
        if os.path.exists(path):
            print(f"✅ Chrome encontrado en: {path}")

            # Intentar obtener versión
            try:
                if system == 'Linux':
                    result = subprocess.run(
                        [path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"   Versión: {result.stdout.strip()}")
            except Exception:
                pass

            print("\n✅ Chrome está instalado correctamente")
            print("   Puedes usar Selenium sin problemas\n")
            return True

    print("❌ Chrome NO está instalado en el sistema\n")
    return False


def print_installation_instructions():
    """Imprime instrucciones de instalación según el sistema operativo."""
    system = platform.system()

    print("="*70)
    print("📦 INSTRUCCIONES DE INSTALACIÓN DE CHROME")
    print("="*70)

    if system == 'Linux':
        # Detectar distribución
        distro = "unknown"
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content or 'debian' in content:
                    distro = 'debian'
                elif 'fedora' in content or 'rhel' in content or 'centos' in content:
                    distro = 'fedora'
                elif 'arch' in content:
                    distro = 'arch'
        except Exception:
            pass

        print("\n🐧 Linux")

        if distro == 'debian':
            print("\n📥 Ubuntu/Debian:")
            print("```bash")
            print("# Añadir repositorio de Google Chrome")
            print("wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
            print('sudo sh -c \'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list\'')
            print()
            print("# Instalar Chrome")
            print("sudo apt update")
            print("sudo apt install google-chrome-stable")
            print("```")

        elif distro == 'fedora':
            print("\n📥 Fedora/RHEL/CentOS:")
            print("```bash")
            print("sudo dnf install google-chrome-stable")
            print("```")

        elif distro == 'arch':
            print("\n📥 Arch Linux:")
            print("```bash")
            print("yay -S google-chrome")
            print("# O usar chromium:")
            print("sudo pacman -S chromium")
            print("```")

        else:
            print("\n📥 Descarga desde:")
            print("   https://www.google.com/chrome/")

    elif system == 'Darwin':
        print("\n🍎 macOS")
        print("\n📥 Con Homebrew:")
        print("```bash")
        print("brew install --cask google-chrome")
        print("```")
        print("\n📥 Descarga manual:")
        print("   https://www.google.com/chrome/")

    elif system == 'Windows':
        print("\n🪟 Windows")
        print("\n📥 Descarga desde:")
        print("   https://www.google.com/chrome/")
        print("\nO ejecuta en PowerShell (como administrador):")
        print("```powershell")
        print("choco install googlechrome")
        print("```")

    print("\n" + "="*70)
    print()


def check_selenium_installed():
    """Verifica si Selenium está instalado."""
    print("🔍 Verificando instalación de Selenium...\n")

    try:
        import selenium
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ Selenium instalado correctamente")
        print(f"   Versión: {selenium.__version__}")
        print("✅ webdriver-manager instalado correctamente\n")
        return True
    except ImportError as e:
        print(f"❌ Falta dependencia: {str(e)}\n")
        print("📦 Instalar con:")
        print("   pip install selenium webdriver-manager\n")
        return False


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("🤖 VERIFICADOR DE REQUISITOS PARA SELENIUM")
    print("="*70)
    print()

    all_ok = True

    # Verificar Selenium
    if not check_selenium_installed():
        all_ok = False

    # Verificar Chrome
    if not check_chrome_installed():
        all_ok = False
        print_installation_instructions()

    if all_ok:
        print("="*70)
        print("🎉 ¡TODO LISTO!")
        print("="*70)
        print("\n✅ Selenium está instalado")
        print("✅ Chrome está instalado")
        print("\nPuedes ejecutar el scraper con:")
        print("   python scripts/quick_start.py")
        print("\n" + "="*70)
    else:
        print("="*70)
        print("⚠️  FALTAN REQUISITOS")
        print("="*70)
        print("\nInstala los requisitos faltantes y vuelve a ejecutar este script.")
        print("\n" + "="*70)
        sys.exit(1)


if __name__ == '__main__':
    main()
