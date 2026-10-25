"""
Script de construccion para empaquetar Automatizacion Legalizacion Facturas Tptes en:
1. Version Portable (Carpeta y archivo ZIP listos para usar en USB o red)
2. Instalador de Windows (.exe nativo con asistente y accesos directos)
3. Sincronizacion directa con las carpetas 'portable' e 'installable'
"""
import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def print_step(msg):
    print("\n" + "=" * 60)
    print(f" >> {msg}")
    print("=" * 60)

def main():
    skip_pyinstaller = "--skip-pyinstaller" in sys.argv
    root_dir = Path(__file__).resolve().parent
    dist_dir = root_dir / "dist"
    app_dist_dir = dist_dir / "LegalizacionFacturasTptes"
    spec_file = root_dir / "LegalizacionFacturasTptes.spec"

    if not skip_pyinstaller:
        print_step("Paso 1: Compilando con PyInstaller...")
        cmd_pyinstaller = [
            sys.executable,
            "-m", "PyInstaller",
            "--clean",
            "-y",
            str(spec_file)
        ]
        res = subprocess.run(cmd_pyinstaller, cwd=str(root_dir))
        if res.returncode != 0:
            print("ERROR: La compilacion con PyInstaller fallo.")
            sys.exit(1)
    else:
        print_step("Paso 1: Omitiendo compilacion PyInstaller (--skip-pyinstaller)...")

    print_step("Paso 2: Copiando recursos a la carpeta de distribucion...")

    # Copiar plantillas
    plantillas_src = root_dir / "plantillas"
    plantillas_dst = app_dist_dir / "plantillas"
    if plantillas_src.exists():
        if plantillas_dst.exists():
            shutil.rmtree(plantillas_dst)
        shutil.copytree(plantillas_src, plantillas_dst)
        print(f"[OK] plantillas copiadas a {plantillas_dst}")

    # Copiar config_personal.json
    config_src = root_dir / "config_personal.json"
    config_dst = app_dist_dir / "config_personal.json"
    if config_src.exists():
        shutil.copy2(config_src, config_dst)
        print(f"[OK] config_personal.json copiado a {config_dst}")

    # Copiar WEBDRIVER
    webdriver_src = root_dir / "WEBDRIVER"
    if not webdriver_src.exists():
        webdriver_src = root_dir / "utils" / "WEBDRIVER"
    if webdriver_src.exists():
        webdriver_dst = app_dist_dir / "WEBDRIVER"
        if webdriver_dst.exists():
            shutil.rmtree(webdriver_dst)
        shutil.copytree(webdriver_src, webdriver_dst)
        print(f"[OK] WEBDRIVER copiado a {webdriver_dst}")

    # Copiar icono y leeme
    for extra_file in ["app_icon.ico", "LEEME_PORTABLE.txt"]:
        src = root_dir / extra_file
        if src.exists():
            shutil.copy2(src, app_dist_dir / extra_file)
            print(f"[OK] {extra_file} copiado")

    print_step("Paso 3: Creando archivo comprimido ZIP (Version Portable)...")
    zip_filename = dist_dir / "LegalizacionFacturasTptes_Portable_v1.0.zip"
    if zip_filename.exists():
        zip_filename.unlink()

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for file_path in app_dist_dir.rglob('*'):
            arcname = Path("LegalizacionFacturasTptes") / file_path.relative_to(app_dist_dir)
            zipf.write(file_path, arcname)

    zip_size_mb = zip_filename.stat().st_size / (1024 * 1024)
    print(f"[OK] Version Portable generada: {zip_filename} ({zip_size_mb:.2f} MB)")

    print_step("Paso 4: Generando Instalador para Windows (.exe con Inno Setup)...")
    iscc_candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
        shutil.which("iscc")
    ]
    iscc_path = None
    for cand in iscc_candidates:
        if cand and Path(cand).exists():
            iscc_path = Path(cand)
            break

    installer_created = False
    if iscc_path:
        print(f"Compilador Inno Setup encontrado: {iscc_path}")
        iss_file = root_dir / "installer.iss"
        cmd_iscc = [str(iscc_path), str(iss_file)]
        res_iscc = subprocess.run(cmd_iscc, cwd=str(root_dir))
        if res_iscc.returncode == 0:
            installer_path = dist_dir / "Instalador_LegalizacionFacturasTptes_v1.0.exe"
            if installer_path.exists():
                installer_size_mb = installer_path.stat().st_size / (1024 * 1024)
                print(f"[OK] Instalador generado: {installer_path} ({installer_size_mb:.2f} MB)")
                installer_created = True
        else:
            print("AVISO: Fallo al compilar el instalador con Inno Setup.")
    else:
        print("AVISO: No se encontro ISCC.exe.")

    print_step("Paso 5: Sincronizando carpetas 'portable' e 'installable'...")
    portable_root = root_dir / "portable"
    installable_root = root_dir / "installable"
    portable_root.mkdir(exist_ok=True)
    installable_root.mkdir(exist_ok=True)

    # Actualizar portable
    for item in app_dist_dir.iterdir():
        dest = portable_root / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    if zip_filename.exists():
        shutil.copy2(zip_filename, portable_root / zip_filename.name)
    print(f"[OK] Carpeta 'portable' actualizada en: {portable_root}")

    # Actualizar installable
    if installer_created and installer_path.exists():
        shutil.copy2(installer_path, installable_root / installer_path.name)
        
        # Leeme instalacion
        leeme_inst = """=====================================================
  INSTALADOR - LEGALIZACION FACTURAS TPTES
=====================================================

INSTRUCCIONES DE INSTALACION:
1. Lleva el archivo "Instalador_LegalizacionFacturasTptes_v1.0.exe" a la PC donde deseas usar el programa.
2. Haz doble clic en el instalador y sigue el asistente.
3. No requiere permisos de administrador.
4. Al finalizar, encontraras el acceso directo en tu Escritorio y en el Menu Inicio con su icono oficial.
"""
        with open(installable_root / "LEEME_INSTALACION.txt", "w", encoding="utf-8") as f:
            f.write(leeme_inst)
        print(f"[OK] Carpeta 'installable' actualizada en: {installable_root}")

    print_step("RESUMEN DE GENERACION")
    print(f"1. Carpeta ejecutable: {app_dist_dir / 'LegalizacionFacturasTptes.exe'}")
    print(f"2. Archivo Portable (.ZIP): {zip_filename}")
    if installer_created:
        print(f"3. Instalador de Windows (.EXE): {dist_dir / 'Instalador_LegalizacionFacturasTptes_v1.0.exe'}")
    print("4. Carpetas finales:")
    print(f"   -> {portable_root}")
    print(f"   -> {installable_root}")
    print("=" * 60)

if __name__ == "__main__":
    main()
