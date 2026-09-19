# mapowanie-ODM-gepard
Mapowanie na podstawie folderu `incoming` (pliki .jpg i metadane .json) z systemu Gepard, oparte na silniku OpenDroneMap.

## 🚀 Jak korzystać z ODM Pipeline

Ten skrypt automatyzuje proces generowania ortofotomap na podstawie zdjęć lotniczych.

### 📋 Wymagania wstępne

Zanim zaczniesz, upewnij się, że spełniasz dwa podstawowe warunki:
1. **Docker:** Musisz mieć zainstalowaną i **uruchomioną** aplikację Docker na swoim komputerze.
2. **Obraz ODM:** Pobierz oficjalny obraz OpenDroneMap, wpisując w terminalu:
   ```bash
   docker pull opendronemap/odm
   ```

### 🛠️ Uruchamianie skryptu

Pipeline potrzebuje do działania plików z drona (zdjęcia `.jpg` oraz pliki metadanych `.json`). Powinny one znajdować się w jednym folderze.

Aby wystartować proces, otwórz terminal i uruchom skrypt, podając mu ścieżkę do tego folderu. 

*Przykład uruchomienia (podmień ścieżki na właściwe dla Twojego komputera):*
```bash
python "C:\Users\szymo\Desktop\PREZENT DLA BARTKA\Dla_Kolegi_Generator_Map\odm_pipeline.py" "D:\Sciezka_do_zdjec_z_drona\incoming"
```
*(Wyniki w postaci mapy, raportu i czasu wykonania zapiszą się automatycznie na Pulpicie w specjalnym folderze np. `Wyniki_Mapowania_1430`)*

### ⚙️ Co oznaczają flagi użyte w skrypcie?

Proces przetwarzania w pliku `odm_pipeline.py` został wstępnie skonfigurowany specjalnymi parametrami (flagami), żeby był możliwie wydajny. Jeśli zechcesz, możesz je edytować w pliku skryptu. 

Oto krótkie, ludzkie wyjaśnienie, za co odpowiadają poszczególne parametry:

* `--fast-orthophoto` – Tryb przyspieszony. Skupia się na wygenerowaniu mapy płaskiej (ortofotomapy) i pomija tworzenie bardzo ciężkich, precyzyjnych modeli 3D.
* `--feature-type sift` – Typ algorytmu używanego do szukania "punktów charakterystycznych" na zdjęciach, żeby je ze sobą połączyć. SIFT to bardzo solidny i sprawdzony standard w fotogrametrii.
* `--feature-quality medium` – Jakość szukania punktów dopasowania. `medium` to świetny kompromis między szybkością a dokładnością, chroni przed zacinaniem sprzętu.
* `--min-num-features 3000` – Oznacza, że skrypt ma szukać co najmniej 3000 wspólnych punktów odniesienia dla każdego zdjęcia. To pomaga dobrze i stabilnie "posklejać" mapę.
* `--matcher-neighbors 8` – Mówi programowi, z iloma najbliższymi przestrzennie sąsiadującymi zdjęciami ma porównywać dane ujęcie. Wartość 8 zazwyczaj wystarcza i zapobiega niepotrzebnie długim obliczeniom.
* `--use-hybrid-bundle-adjustment` – Ulepszona matematyka układająca zdjęcia (hybrydowe wyrównanie bloku). Lepiej radzi sobie m.in. z długimi prostymi przelotami drona wzdłuż jednej osi, poprawiając dokładność.
* `--gps-accuracy 5` – Program traktuje współrzędne GPS zaszyte w plikach `.json` z tolerancją błędu rzędu 5 metrów (wie, na ile ufać pozycji z drona w procesie kalibracji).
* `--orthophoto-resolution 6` – Docelowa rozdzielczość gotowej mapy wynosi ok. 6 centymetrów na piksel. Rozsądne ustawienie – dobre detale, ale nie powoduje gigantycznego rozmiaru pliku końcowego.
* `--orthophoto-compression JPEG` – Gotowy, wielki plik z mapą (.TIF) zostanie skompresowany używając JPEG. Dzięki temu waży wielokrotnie mniej, a jakość pozostaje świetna.
* `--optimize-disk-space` – Zmusza program do aktywnego kasowania niepotrzebnych, śmieciowych plików roboczych w trakcie procesu, oszczędzając miejsce na Twoim dysku.
* `--max-concurrency 12` – Pozwala na robienie obliczeń równolegle na maksymalnie 12 rdzeniach/wątkach procesora. Im wyższa wartość (zależna od mocy komputera), tym szybciej zadziała cały proces.
