import os
import sys
import json
import glob
import shutil
import subprocess
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="OpenDroneMap Pipeline")
    parser.add_argument(
        "input_dir", 
        type=str, 
        nargs="?", 
        help="Ścieżka do folderu z pendrive'a (ze zdjęciami JPG i JSON)"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir:
        print(" BŁĄD: Nie podano ścieżki do folderu!")
        print(" Użycie: python odm_pipeline.py <sciezka_do_folderu>")
        print(" Przykład: python odm_pipeline.py D:\\incoming")
        sys.exit(1)
        
    input_dir = args.input_dir
    if not os.path.isdir(input_dir):
        print(f"BLAD: Podana sciezka to nie jest folder: {input_dir}")
        sys.exit(1)
        
    print("=============================================")
    print("        OPEN DRONE MAP PIPELINE              ")
    print("=============================================")
    print(f"Katalog z pendrive/dysku: {input_dir}")
    
    print("\nFaza 1: Kopiowanie plików do folderu roboczego")
    
    workspace_dir = os.path.join(os.environ["USERPROFILE"], "ODM_Workspace")
    images_dir = os.path.join(workspace_dir, "images")
    geo_txt_path = os.path.join(workspace_dir, "geo.txt")
    
    if os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir)
    os.makedirs(images_dir)
    
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    jpg_files = glob.glob(os.path.join(input_dir, "*.jpg")) + glob.glob(os.path.join(input_dir, "images", "*.jpg"))
    
    if not jpg_files:
        print("BLAD: Nie znaleziono plików .jpg w podanym folderze!")
        sys.exit(1)
        
    print(f"-> Znaleziono {len(jpg_files)} zdjęć i {len(json_files)} plików GPS (.json).")
    print(f"-> Kopiowanie do: {workspace_dir}...")
    
    for jpg in jpg_files:
        shutil.copy2(jpg, os.path.join(images_dir, os.path.basename(jpg)))
        
    valid_records = 0
    with open(geo_txt_path, "w", encoding="utf-8") as f:
        f.write("EPSG:4326\n")
        for jf in sorted(json_files):
            try:
                with open(jf, "r", encoding="utf-8") as json_in:
                    data = json.load(json_in)
                    frame = data.get("frame")
                    gps = data.get("gps", {})
                    lat, lon, alt = gps.get("lat"), gps.get("lon"), gps.get("alt_msl")
                    if frame and lat is not None and lon is not None and alt is not None:
                        f.write(f"{frame} {lon} {lat} {alt}\n")
                        valid_records += 1
            except Exception:
                pass
    
    print(f"-> Utworzono plik geo.txt (dodano {valid_records} wpisów GPS).")
    
    print("\nFaza 2: Uruchamianie OpenDroneMap (to zajmie chwilę)...")
    docker_odm_cmd = [
        "docker", "run", "--rm",
        "-v", f"{workspace_dir}:/datasets/code",
        "opendronemap/odm",
        "--project-path", "/datasets", "code",
        "--fast-orthophoto",
        "--feature-type", "sift",
        "--feature-quality", "medium",
        "--min-num-features", "3000",
        "--matcher-neighbors", "8",
        "--use-hybrid-bundle-adjustment",
        "--gps-accuracy", "5",
        "--orthophoto-resolution", "6",
        "--orthophoto-compression", "JPEG",
        "--optimize-disk-space",
        "--max-concurrency", "12"
    ]
    
    try:
        subprocess.run(docker_odm_cmd, check=True)
    except subprocess.CalledProcessError:
        print("\nBLAD: Proces OpenDroneMap zakończył się błędem!")
        sys.exit(1)
        
    print("\nFaza 3: Zbieranie plików")
    desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
    date_str = datetime.now().strftime("%H%M")
    
    output_folder = os.path.join(desktop_dir, f"Wyniki_Mapowania_{date_str}")
    os.makedirs(output_folder, exist_ok=True)
    
    src_tif = os.path.join(workspace_dir, "odm_orthophoto", "odm_orthophoto.tif")
    src_report = os.path.join(workspace_dir, "odm_report", "report.pdf")
    src_benchmark = os.path.join(workspace_dir, "benchmark.txt")
    
    if os.path.exists(src_tif):
        shutil.copy2(src_tif, os.path.join(output_folder, "mapa.tif"))
        print(f"-> Zapisano mapę z koordynatami (TIF)")
        
    if os.path.exists(src_report):
        shutil.copy2(src_report, os.path.join(output_folder, "raport_jakosci.pdf"))
        print(f"-> Zapisano raport PDF (raport_jakosci.pdf)")
        
    if os.path.exists(src_benchmark):
        shutil.copy2(src_benchmark, os.path.join(output_folder, "benchmark_czasowy.txt"))
        print(f"-> Zapisano log czasowy (benchmark_czasowy.txt)")
        
    shutil.rmtree(workspace_dir, ignore_errors=True)
        
    print(f"folder na Pulpicie: ")
    print(f" Wyniki_Mapowania_{date_str} ")

if __name__ == "__main__":
    main()
