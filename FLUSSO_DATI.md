# Flusso dei Dati - SimbioReader

## 1. Visione d'Insieme

SimbioReader è un lettore Python per i dati del **SIMBIO-SYS** (Spectrometer And Imagers For Mpo Bepicolombo Integrated Observatory System) della missione ESA BepiColombo. Il sistema gestisce il flusso di dati da file SIMBIO-SYS a informazioni strutturate, con supporto per visualizzazione e elaborazione.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FLUSSO PRINCIPALE DATI                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  FILE INPUT              PARSING              ELABORAZIONE            │
│  ┌──────────┐           ┌──────────┐        ┌──────────────┐        │
│  │ .lblx    │──────────▶│ XML      │───────▶│ SimbioReader │        │
│  │ .dat     │   DOM     │ Parser   │ Metadati    Object    │        │
│  │ .csv     │           └──────────┘        └──────────────┘        │
│  └──────────┘                                     │                  │
│                                                   ▼                  │
│                                           ┌──────────────┐           │
│                                           │ Data Objects │           │
│                                           ├──────────────┤           │
│                                           │ - Detector   │           │
│                                           │ - Filter     │           │
│                                           │ - HK         │           │
│                                           │ - Image Data │           │
│                                           └──────────────┘           │
│                                                   │                  │
│                          ┌────────────────────────┼────────────────┐│
│                          ▼                        ▼                ▼││
│                    ┌──────────┐          ┌──────────────┐   ┌─────────┐
│                    │ Display  │          │ Save Preview │   │ Export  │
│                    │ Rich     │          │ (PNG/TIF)    │   │ (XML)   │
│                    └──────────┘          └──────────────┘   └─────────┘
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Struttura dei Dati di Input

### 2.1 File di Label PDS (.lblx)

Il file `.lblx` è un file XML che contiene i metadati completi del prodotto SIMBIO-SYS:

```
sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.lblx
│
├── Informazioni Generali
│   ├── logical_identifier (LID)
│   ├── version_id
│   ├── title
│   ├── information_model_version
│   └── processing_level
│
├── Mission Phase
│   └── psa:Mission_Phase
│       └── psa:name (es: "Cruise - ICO")
│
├── Observation Area
│   ├── Time_Coordinates
│   │   ├── start_date_time
│   │   └── stop_date_time
│   ├── Target_Identification
│   │   ├── name
│   │   └── type
│   └── [per ogni canale]
│       ├── img:Imaging
│       │   ├── img:exposure_duration
│       │   ├── img:Optical_Filter
│       │   ├── img:Subframe
│       │   │   ├── img:first_line
│       │   │   ├── img:first_sample
│       │   │   ├── img:lines
│       │   │   ├── img:samples
│       │   │   ├── img:line_fov
│       │   │   └── img:sample_fov
│       │   └── [Spacecraft clock info]
│       └── geom:Geometry
│           └── [Informazioni geometriche]
│
└── File Areas
    ├── File_Area_Observational
    │   ├── File
    │   │   ├── file_name (es: "sim_cal_sc_stc_cruise_ico11_2024-04-08_001__0_1.dat")
    │   │   ├── creation_date_time
    │   │   ├── file_size
    │   │   └── md5_checksum
    │   └── Array_2D_Image o Array_3D_Spectrum
    │       ├── axes
    │       ├── Axis_Array (per ogni asse)
    │       │   ├── axis_name
    │       │   └── elements
    │       └── data_type (UnsignedLSB2, IEEE754LSBSingle)
    │
    └── File_Area_Browse (opzionale)
        └── [Preview images]
```

### 2.2 File di Dati Immagine (.dat, .qub)

Contiene i dati grezzi dell'immagine in formato binario:

- **Formato**: Binario little-endian
- **Dimensioni**: Dipendono dal tipo di canale
  - **STC/HRIC**: 2D array (lines × samples) o 3D per multispettrale
  - **VIHI**: 3D array (lines × samples × bands)
- **Tipo dato**:
  - `UnsignedLSB2`: int16 (per calibrazione)
  - `IEEE754LSBSingle`: float32 (per dati radiometrici)

### 2.3 File di Housekeeping (.csv)

Contiene dati telemetrici raccolti durante l'acquisizione:

```csv
Tempo di osservazione,Temperatura sensore,Voltaggio,Configurazione,...
2024-04-08T12:00:00,25.5,5.0,NORMAL,...
```

---

## 3. Flusso di Esecuzione Principale

### 3.1 Entry Point: Riga di Comando

```bash
simbioReader <file_path> [opzioni]
```

**Percorso nel codice**: `src/SimbioReader/__main__.py` → `src/SimbioReader/cli.py`

```python
if __name__ == "__main__":
    cli()
```

**Opzioni disponibili**:
- `--all`: Mostra tutte le informazioni
- `--hk`: Mostra i dati di housekeeping
- `--detector`: Mostra le informazioni del rilevatore
- `--data-structure`: Mostra la struttura dei dati
- `--filters`: Mostra le informazioni sui filtri (HRIC/STC)
- `--summarize`: Mostra solo il riassunto
- `-d, --debug`: Modalità debug
- `-v, --verbose`: Modalità verbose
- `--version`: Mostra la versione

### 3.2 Fase 1: Inizializzazione SimbioReader

**Metodo**: `SimbioReader.__init__()`

```
1. Accetta il percorso del file
2. Valida l'estensione (.lblx, .dat)
3. Individua il file label associato mediante label_name()
4. Verifica l'esistenza del file label
5. Procede con il parsing
```

**Codice chiave** (sr.py, linee ~550-630):

```python
class SimbioReader:
    def __init__(self, file_path: Path, ...):
        # Passo 1: Normalizza il percorso
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Passo 2: Ritrova il file label (.lblx)
        self.pdsLabel = self.label_name(file_path)
        
        # Passo 3: Verifica esistenza
        if self.pdsLabel is None or not self.pdsLabel.exists():
            raise FileNotFoundError(f"The file {self.pdsLabel} does not exist.")
```

### 3.3 Fase 2: Parsing del File Label XML

**Metodo**: `SimbioReader.__init__()` continua

```python
# Parsing XML
label = parse(self.pdsLabel.as_posix())

# Estrae i metadati principali
self.channel = getValue(label, "psa:identifier").lower()
self.level = getValue(label, "processing_level").lower()
self.lid = getValue(label, "logical_identifier")
self.version = getValue(label, "version_id")
self.title = getValue(label, "title")
self.dataModelVersion = getValue(label, "information_model_version")
```

**Validazione del canale**:
```python
if self.channel not in ["stc", "hric", "vihi"]:
    raise ValueError(f"Unknown channel '{self.channel}' found in label.")
```

### 3.4 Fase 3: Estrazione Metadati di Osservazione

**Cosa viene estratto**:

```python
# Informazioni temporali
obsArea = getElement(label, "Observation_Area")
timeCoords = getElement(obsArea, "Time_Coordinates")
self.startTime = parser.parse(getValue(timeCoords, "start_date_time"))
self.stopTime = parser.parse(getValue(timeCoords, "stop_date_time"))

# Spacecraft Clock Events (SCET)
self.start_scet = getValue(label, "psa:spacecraft_clock_start_count")
self.stop_scet = getValue(label, "psa:spacecraft_clock_start_count")

# Target Information
targetInfo = getElement(obsArea, "Target_Identification")
self.target = Target(
    name=getValue(targetInfo, "name"),
    target_type=getValue(targetInfo, "type")
)

# Mission Phase
mission_phase = getElement(label, "psa:Mission_Phase")
self.phaseName = getValue(mission_phase, "psa:name")
```

### 3.5 Fase 4: Creazione Oggetto Data

**Metodo**: `Data.__init__()` (sr.py, linee ~530-590)

L'oggetto `Data` gestisce l'accesso ai dati effettivi in base al canale:

```python
self.data = Data(
    channel=self.channel,
    level=self.level,
    source_path=self.pdsLabel.parent,
    file_obs=label.getElementsByTagName("File_Area_Observational"),
    imaging=label.getElementsByTagName("img:Imaging"),
    geometry=label.getElementsByTagName("geom:Geometry"),
    debug=debug,
    verbose=verbose,
    console=self.console,
)
```

**Logica interna di Data**:

```
┌─ Channel: STC o HRIC
│  ├─ Legge img:filter_name da imaging
│  ├─ Per ogni filtro crea un oggetto SimbioObject
│  ├─ Memorizza in self.filters (lista)
│  └─ Crea attributi dinamici (es: filter_pan_l, filter_pan_r)
│
└─ Channel: VIHI
   ├─ Crea oggetti SimbioObject per ogni segmento
   ├─ Memorizza in self.segments (lista)
   └─ Crea attributi dinamici (es: segment_001, segment_002)
```

### 3.6 Fase 5: Creazione Oggetto SimbioObject

**Metodo**: `SimbioObject.__init__()` (sr.py, linee ~200-370)

Per ogni filtro (STC/HRIC) o segmento (VIHI):

```python
class SimbioObject:
    def __init__(self, file_name, channel, imaging, geometry, file_obs, ...):
        # 1. Memorizza i parametri
        self.file_name = Path(file_name)
        self.channel = channel
        
        # 2. Estrae informazioni di imaging
        subFrame = getElement(imaging, "img:Subframe")
        self.firstLine = int(getValue(subFrame, "img:first_line"))
        self.firstSample = int(getValue(subFrame, "img:first_sample"))
        self.lines = int(getValue(subFrame, "img:lines"))
        self.samples = int(getValue(subFrame, "img:samples"))
        
        # 3. Estrae info geometriche
        self.lineFov = float(getValue(subFrame, "img:line_fov"))
        self.sampleFov = float(getValue(subFrame, "img:sample_fov"))
        
        # 4. Crea oggetto DataStructure
        self.data_structure = DataStructure(file_obs, self.channel)
        
        # 5. Estrae info del filtro (se non VIHI)
        if self.channel.upper() != "VIHI":
            flt = getElement(imaging, "img:Optical_Filter")
            self.filter = Filter(
                channel=self.channel,
                name=getValue(flt, "img:filter_name")
            )
        
        # 6. Crea oggetto Detector
        self.detector = Detector(imaging)
        
        # 7. CARICA I DATI BINARI
        # Determina il tipo di dato
        if self.data_structure.data_type == "UnsignedLSB2":
            dtype = np.int16
        elif self.data_structure.data_type == "IEEE754LSBSingle":
            dtype = np.float32
        
        # Legge l'intera immagine dal file binario
        if self.data_structure.axes == 3:
            self.img = np.fromfile(
                self.file_name,
                dtype=dtype,
                count=self.samples * self.lines * self.bands
            )
            if self.lines == 1:
                self.img.shape = (self.samples, self.bands)
            else:
                self.img.shape = (self.lines, self.samples, self.bands)
        else:
            self.img = np.fromfile(
                self.file_name,
                dtype=dtype,
                count=self.samples * self.lines
            )
            self.img.shape = (self.samples, self.lines)
```

**Validazione delle dimensioni**:

```python
if verbose or debug:
    # Calcola la dimensione attesa
    if self.data_structure.axes == 3:
        imgSize = (self.samples * self.lines * self.bands * 
                   data_types[self.data_structure.data_type]["bits"])
    else:
        imgSize = (self.samples * self.lines * 
                   data_types[self.data_structure.data_type]["bits"])
    
    # Verifica corrispondenza con file size
    if self.file_name.stat().st_size * 8 != imgSize:
        raise SizeError(self.file_name.stat().st_size * 8, imgSize)
```

### 3.7 Fase 6: Lettura Housekeeping (CSV)

**Metodo**: `Data.__init__()` - parsing CSV

```python
if file_name.suffix.lower() == ".csv":
    df = pd.read_csv(file_name, sep=",", header=0)
    self.hk = HK(df)
```

**Classe HK**:

```python
class HK:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        # Crea attributi dinamici da ogni colonna CSV
        for i in df.columns:
            val = df[i].values[0].strip() if isinstance(df[i].values[0], str) else df[i].values[0]
            setattr(self, i.strip().lower(), val)
```

---

## 4. Strutture Dati Principali

### 4.1 Classe `SimbioReader`

**Responsabilità**: Entry point principale, coordinamento del flusso

**Attributi principali**:
```python
├── pdsLabel: Path          # Percorso file label
├── channel: str            # "stc", "hric", "vihi"
├── level: str              # "raw", "cal", etc.
├── lid: str                # Logical IDentifier PDS
├── version: str            # Versione prodotto
├── title: str              # Titolo osservazione
├── startTime: datetime     # Inizio osservazione
├── stopTime: datetime      # Fine osservazione
├── target: Target          # Target osservato (Luna/Mercurio)
├── phaseName: str          # Fase missione
├── data: Data              # Oggetto container dati
└── console: Console        # Output rich
```

### 4.2 Classe `Data`

**Responsabilità**: Container per i dati di imaging, gestisce filtri/segmenti

**Attributi dinamici**:
```python
# Per STC/HRIC:
├── filters: List[str]      # Lista nomi filtri
├── filter_pan_l: SimbioObject
├── filter_pan_r: SimbioObject
├── filter_vio: SimbioObject
└── ...

# Per VIHI:
├── segments: List[str]     # Lista segmenti
├── segment_001: SimbioObject
├── segment_002: SimbioObject
└── ...
```

### 4.3 Classe `SimbioObject`

**Responsabilità**: Rappresenta un singolo dataset di imaging (filtro o segmento)

**Attributi principali**:
```python
├── file_name: Path         # File .dat sorgente
├── channel: str            # Canale ("stc", "hric", "vihi")
├── img: np.ndarray         # Dati immagine (2D o 3D)
├── filter_name: str        # Nome filtro (STC/HRIC)
├── firstLine, firstSample  # Coordinate subframe
├── lines, samples, bands   # Dimensioni immagine
├── exposure_time: float    # Tempo esposizione
├── filter: Filter          # Oggetto Filter (se STC/HRIC)
├── detector: Detector      # Informazioni rilevatore
└── data_structure: DataStructure  # Metadati struttura
```

### 4.4 Classe `Detector`

**Estrae dalle info di subframe**:
```python
├── first_line: int
├── first_sample: int
├── lines: int
├── samples: int
├── line_fov: float         # Field of View lineare
└── sample_fov: float       # Field of View campionato
```

### 4.5 Classe `DataStructure`

**Estrae dalla struttura dati del label**:
```python
├── creation_time: datetime
├── file_size: int
├── md5: str                # Checksum integrità
├── axes: int               # 2 o 3
├── line: int, sample: int, band: int  # Dimensioni assi
├── data_type: str          # "UnsignedLSB2" o "IEEE754LSBSingle"
└── [attributi assi per ogni asse]
```

### 4.6 Classe `HK` (Housekeeping)

**Container per telemetria CSV**:
```python
├── df: pd.DataFrame        # DataFrame originale
└── [attributi dinamici per ogni colonna CSV]
```

---

## 5. Flusso di Visualizzazione e Output

### 5.1 Display Principale: `SimbioReader.show()`

```python
def show(self, hk=False, detector=False, data_structure=False, filters=False, all_info=False):
    columns = [self.info(), self.target.show()]
    
    if hk or all_info:
        columns.append(self.data.hk.show())
    
    if detector or all_info:
        for item in self.data.filters:
            disp = getattr(self.data, f"filter_{item.lower()}")
            columns.append(disp.detector.show(...))
    
    if data_structure or all_info:
        for item in self.data.filters:
            disp = getattr(self.data, f"filter_{item.lower()}")
            columns.append(disp.data_structure.show(...))
    
    if filters:
        for item in self.data.filters:
            disp = getattr(self.data, f"filter_{item.lower()}")
            columns.append(disp.show())
    
    return Panel(Columns(columns, expand=True), ...)
```

**Componenti visualizzati**:

```
┌─────────────────────────────────────────────────────┐
│              SimbioReader Summary                    │
├─────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌────────────┐ ┌──────────────┐   │
│ │ SimbioReader │ │   Target   │ │   Detector   │   │
│ │    Info      │ │    Info    │ │    Info      │   │
│ ├──────────────┤ ├────────────┤ ├──────────────┤   │
│ │- Channel     │ │- Name      │ │- First Line  │   │
│ │- Level       │ │- Type      │ │- First Sample│   │
│ │- LID         │ │            │ │- Lines       │   │
│ │- Version     │ │            │ │- Samples     │   │
│ │- Title       │ │            │ │- Line FOV    │   │
│ │- ObsTime     │ │            │ │- Sample FOV  │   │
│ └──────────────┘ └────────────┘ └──────────────┘   │
│                                                     │
│ [Additional panels if requested]                   │
└─────────────────────────────────────────────────────┘
```

### 5.2 Salvataggio Preview

**Metodo**: `SimbioReader.savePreview()`

```
1. Valida il formato immagine (PNG, TIF, JPG)
2. Crea cartella output se necessaria
3. Per ogni filtro/segmento:
   └─ Genera preview mediante SimbioObject.savePreview()
4. Se template XML fornito:
   └─ Aggiorna metadati XML con nuove preview
   └─ Genera nuovo LID e versione
   └─ Scrive file label aggiornato
```

**Flusso dettagliato**:

```python
def savePreview(self, img_type="png", quality=100, outFolder=None, template=None, ...):
    # 1. Gestione parametri
    if template:
        img_type = "png"
    if outFolder is None:
        dest = self.pdsLabel.parent
    else:
        dest = Path(outFolder)
        dest.mkdir(parents=True, exist_ok=True)
    
    # 2. Se template fornito: aggiorna metadati XML
    if template:
        tree = parse(template.as_posix())
        
        # Rimuove File_Area_Browse esistenti
        for item in tree.getElementsByTagName("File_Area_Browse"):
            item.parentNode.removeChild(item)
        
        # Aggiorna LID, versione, timestamp
        new_lid = lidUpdate(tree, new_label, calib=calib)
        updateXML(tree, "modification_date", creatTime.strftime("%Y-%m-%d"))
        updateXML(tree, "version_id", file_version)
        lvidUpdate(tree, new_label, file_version)
        
        # Salva preview e aggiorna XML
        ret = self.data.savePreview(img_type=img_type, outFolder=dest, tree=tree)
        br = getElement(tree, "Product_Browse")
        for item in ret:
            br.appendChild(item)
        
        # Serializza e scrive file label
        dom2 = parseString(pretty_print(tree))
        with open(new_label, "w") as xmlFile:
            dom2.writexml(xmlFile, encoding="utf-8")
    else:
        # Salva solo le preview
        self.data.savePreview(img_type=img_type, quality=quality, outFolder=dest)
```

---

## 6. Gestione Errori e Eccezioni

### 6.1 Eccezioni Personalizzate

```python
# src/SimbioReader/exceptions.py

class SizeError(Exception):
    """Sollevato quando la dimensione file non corrisponde ai dati attesi"""
    pass
```

### 6.2 Validazioni Chiave

| Validazione | Punto di Controllo | Eccezione |
|-----------|-----------------|-----------|
| Estensione file | `label_name()` | FileNotFoundError |
| Esistenza label | `__init__()` | FileNotFoundError |
| Canale valido | `__init__()` | ValueError |
| File dati | `Data.__init__()` | FileNotFoundError |
| Dimensione immagine | `SimbioObject.__init__()` | SizeError |

### 6.3 Modalità Debug e Verbose

```python
# Debug: Informazioni dettagliate di esecuzione
if debug:
    console.print(f"{MSG.DEBUG}Loading: {self.file_name}")

# Verbose: Output aggiuntivo
if verbose:
    console.print(f"{MSG.INFO}Image size: {self.samples}x{self.lines}")
    console.print(f"{MSG.INFO}File size: {self.file_name.stat().st_size * 8}")
```

---

## 7. Considerazioni Architetturali

### 7.1 Design Pattern Utilizzati

| Pattern | Ubicazione | Uso |
|---------|-----------|-----|
| Factory Method | `Data.__init__()` | Crea SimbioObject per filtri/segmenti |
| Builder | `SimbioReader.__init__()` | Costruisce oggetto complesso da XML |
| Composition | `SimbioReader` | Contiene Data, Target, etc. |
| Dynamic Attributes | `Data`, `HK` | Crea proprietà a runtime |

### 7.2 Separazione delle Responsabilità

```
┌─────────────────────────────────────────┐
│        SimbioReader (Orchestrator)      │
│  - Gestisce il flusso principale        │
│  - Coordina le componenti              │
│  - Espone interfaccia pubblica         │
└────────┬────────────────┬────────────────┘
         │                │
    ┌────▼────┐      ┌────▼────┐
    │   Data   │      │  Target │
    │ (Manager)│      │ (Entity)│
    └────┬────┘      └────┬────┘
         │                │
    ┌────▼──────────────────────┐
    │  SimbioObject (Handler)   │
    │  - Carica dati binari     │
    │  - Gestisce singolo file  │
    │  - Espone metadati        │
    └────┬──────────────────────┘
         │
    ┌────▼─────────────────────────┐
    │  Detector, Filter, HK, etc.  │
    │  (Data Models)              │
    │  - Rappresentano concetti   │
    │  - No logica complessa      │
    └─────────────────────────────┘
```

### 7.3 Flusso di Dati Memorizzazione

```
File Sistema                Memoria RAM                 Output
┌──────────┐    Parsing     ┌──────────────────────┐    ┌──────────┐
│.lblx     │────────────────▶│  XML DOM Tree        │   │          │
│(metadati)│                │  + Estratto dati     │   │  Display │
└──────────┘                │                      │   │  (Rich   │
                            │                      │───▶│ Panels)  │
┌──────────┐    NumPy       │  np.ndarray (img)    │   │          │
│.dat      │────────────────▶│  shapes: 2D o 3D    │   │          │
│(raw data)│    fromfile     │                      │   │  Save    │
└──────────┘                │                      │───▶│  Preview │
                            │                      │   │ (PNG/TIF)│
┌──────────┐    Pandas      │  pd.DataFrame (HK)   │   │          │
│.csv      │────────────────▶│  + attributi        │   └──────────┘
│(telemetry)│               │  dinamici            │
└──────────┘                └──────────────────────┘
```

---

## 8. Operazioni Principali Disponibili

### 8.1 Creazione Istanza e Caricamento

```python
from SimbioReader import SimbioReader

# Carica il file PDS
reader = SimbioReader("path/to/file.dat", verbose=True)
```

### 8.2 Accesso ai Dati

```python
# Informazioni generali
print(reader.channel)      # "stc", "hric", "vihi"
print(reader.lid)          # Logical Identifier
print(reader.target.name)  # Nome target

# Accesso ai filtri (STC/HRIC)
filter_obj = reader.data.filter_pan_l
filter_obj.img             # Array NumPy immagine
filter_obj.detector        # Info rilevatore

# Accesso ai segmenti (VIHI)
segment_obj = reader.data.segment_001
segment_obj.img            # Array NumPy immagine
```

### 8.3 Visualizzazione

```python
# Info completa con tutti i dettagli
reader.console.print(reader.show(all_info=True))

# Info specifica
reader.console.print(reader.info())
reader.console.print(reader.target.show())
reader.console.print(reader.data.hk.show())
```

### 8.4 Salvataggio Preview

```python
# Salva solo le preview
reader.savePreview(
    img_type="png",
    quality=95,
    outFolder="/path/to/output"
)

# Salva con template XML aggiornato
reader.savePreview(
    img_type="png",
    template=Path("template.lblx"),
    description="My custom description"
)
```

### 8.5 Estrazione Immagine PIL

```python
# Ottiene oggetto PIL Image
pil_image = reader.get_filter_by_file("filename.dat").img
# o
from SimbioReader import SimbioReader as SR
sr = SR("file.dat")
pil_img = sr.data.filter_pan_l.image()
```

---

## 9. Esempio di Flusso Completo

### Caso d'uso: Analizzare un file STC

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Riga di comando                                         │
├─────────────────────────────────────────────────────────────────┤
│ $ simbioReader sim_cal_sc_stc_cruise_ico11_2024-04-08_001.dat   │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: CLI parsing (cli.py)                                    │
├─────────────────────────────────────────────────────────────────┤
│ • Legge file path: .../sim_cal_sc_stc_cruise_ico11_2024-04-08_001.dat
│ • Nessuna opzione → show() con info di base                    │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: SimbioReader.__init__()                                 │
├─────────────────────────────────────────────────────────────────┤
│ • label_name() individua: ...sim_cal_sc_stc_cruise_ico11_2024-  │
│   04-08_001__0_1.lblx                                           │
│ • parse(lblx) → XML DOM tree                                    │
│ • Estrae: channel="stc", lid="urn:nasa:pds:...", version="1"   │
│ • Legge: obsArea, timeCoords, target, phases                   │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Data.__init__()                                         │
├─────────────────────────────────────────────────────────────────┤
│ • Itera File_Area_Observational dal XML                        │
│ • Per ogni file .dat o .qub:                                   │
│   ├─ Se .csv: crea HK object                                   │
│   └─ Se .dat: crea SimbioObject                                │
│ • Estrae filter_name: "PAN-L", "PAN-R", "VIO"                 │
│ • Crea attributi: filter_pan_l, filter_pan_r, filter_vio       │
│ • Memorizza lista: filters = ["pan-l", "pan-r", "vio"]         │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: SimbioObject.__init__() x 3 (per ogni filtro)          │
├─────────────────────────────────────────────────────────────────┤
│ Per filter_pan_l:                                               │
│ • Legge img:Subframe → firstLine, firstSample, lines, samples  │
│ • Crea DataStructure → data_type, axes, dimensioni            │
│ • Crea Detector → FOV, coordinate subframe                     │
│ • Crea Filter object                                            │
│ • np.fromfile(sim_cal_sc_stc_cruise_ico11_2024-04-08_001__     │
│   0_1.dat, dtype=int16, count=1280*1024)                       │
│ • Reshape → (1024, 1280)                                        │
│ • Memorizza in self.img                                         │
│                                                                 │
│ Idem per filter_pan_r e filter_vio                             │
└──────────────────────┬──────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Visualizzazione mediante show()                        │
├─────────────────────────────────────────────────────────────────┤
│ • Chiama self.info() → Panel con metadati principale           │
│ • Chiama self.target.show() → Panel con info target            │
│ • Chiama Columns() → organizza in colonne                      │
│ • Output via rich.console.print()                              │
│                                                                 │
│ Visualizzazione:                                                │
│ ┌─────────────────────────────────────────────────────────┐    │
│ │ ┌──────────────┐ ┌──────────────┐                       │    │
│ │ │   Channel    │ │     Name     │                       │    │
│ │ │      STC     │ │     Moon     │                       │    │
│ │ ├──────────────┤ ├──────────────┤                       │    │
│ │ │   Level      │ │     Type     │                       │    │
│ │ │      CAL     │ │  Satellite   │                       │    │
│ │ │              │ │              │                       │    │
│ │ │  Obs Time    │ │              │                       │    │
│ │ │ 2024-04-08   │ │              │                       │    │
│ │ └──────────────┘ └──────────────┘                       │    │
│ └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Limiti e Considerazioni

### 10.1 Gestione Memoria

**Considera per file grandi**:
- Immagini 3D (VIHI): fino a ~500 MB per band
- Intera immagine caricata in RAM come NumPy array
- Per analisi di subset, considera implementazione lazy loading

### 10.2 Performance

- **Parsing XML**: O(n) dove n = numero File_Area_Observational
- **Caricamento immagine**: O(n × m) dove n×m = numero pixel
- **Salvataggio preview**: dipende da format (PNG più lento di TIFF)

### 10.3 Compatibilità Format

- **XML Label**: Solo formato PDS4 (namespaces psa:, img:, geom:)
- **Dati binari**: Solo little-endian
- **Data type**: Supporta UnsignedLSB2 e IEEE754LSBSingle

---

## 11. Diagramma di Interazione tra Classi

```
┌─────────────────────────────────────────────────────────────┐
│                      SimbioReader                           │
│  (Entry point, coordinatore principale)                    │
├─────────────────────────────────────────────────────────────┤
│ • Legge file label (.lblx)                                  │
│ • Estrae metadati osservazione                              │
│ • Crea oggetto Data                                         │
│ • Espone interfaccia di visualizzazione                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ aggregates
                    ┌──────┴──────────┐
                    ▼                 ▼
             ┌────────────┐   ┌──────────────┐
             │   Data     │   │    Target    │
             │ (Manager)  │   │   (Entity)   │
             ├────────────┤   ├──────────────┤
             │ • filters  │   │ • name       │
             │ • segments │   │ • type       │
             │ • hk       │   └──────────────┘
             └──────┬─────┘
                    │ creates multiple
                    ▼
             ┌────────────────┐
             │  SimbioObject  │
             │   (Handler)    │
             ├────────────────┤
             │ • file_name    │
             │ • img (np arr) │
             │ • channel      │
             └────┬─────┬─────┤
                  │     │     │ contains
          ┌───────┘     │     └────────┐
          ▼             ▼              ▼
      ┌────────┐  ┌──────────┐  ┌────────────────┐
      │ Filter │  │ Detector │  │ DataStructure  │
      └────────┘  └──────────┘  └────────────────┤
                                 │ • creation_time│
                                 │ • file_size    │
                                 │ • data_type    │
                                 └────────────────┘
      
      ┌────────────────────────────────────┐
      │  HK (Optional)                     │
      │  Housekeeping Data                 │
      ├────────────────────────────────────┤
      │ • df: pd.DataFrame                 │
      │ • [dynamic attributes from CSV]    │
      └────────────────────────────────────┘
```

---

## 12. Riepilogo del Flusso

```
INPUT FILES
    ↓
    ├─→ .lblx (XML Label)  ─────────┐
    ├─→ .dat (Raw Data)    ─────────┤
    └─→ .csv (Housekeeping)─────────┤
                                    ↓
                        [SimbioReader.__init__()]
                            ├─ Parse XML
                            ├─ Valida canale
                            ├─ Estrae metadati osservazione
                            └─ Crea Data object
                                    ↓
                        [Data.__init__()]
                            ├─ Itera File_Area_Observational
                            ├─ Crea SimbioObject per ogni file
                            └─ Crea HK (se CSV)
                                    ↓
                        [SimbioObject.__init__()] x N
                            ├─ Legge Subframe info
                            ├─ Crea Detector object
                            ├─ Crea Filter object
                            ├─ Crea DataStructure object
                            ├─ Carica immagine binaria in RAM
                            └─ Valida dimensioni
                                    ↓
                            IN MEMORIA:
                    - SimbioReader con tutti i metadati
                    - Data con riferimenti a N SimbioObject
                    - Ogni SimbioObject contiene img come np.ndarray
                    - HK con telemetria CSV
                                    ↓
                        OPERAZIONI DISPONIBILI:
                    ├─ show() → Visualizza info
                    ├─ savePreview() → Salva PNG/TIF/JPG
                    ├─ image() → Ritorna PIL Image
                    ├─ get_filter_by_file() → Accesso selettivo
                    └─ Custom analysis on img arrays
```

---

## Riferimenti Codice

| Componente | File | Linee | Descrizione |
|-----------|------|-------|------------|
| `SimbioReader` | `sr.py` | 550-850 | Classe principale |
| `Data` | `sr.py` | 430-530 | Manager dati |
| `SimbioObject` | `sr.py` | 200-370 | Handler singolo file |
| `Detector` | `sr.py` | 40-100 | Info rilevatore |
| `DataStructure` | `sr.py` | 105-175 | Metadati struttura |
| `HK` | `sr.py` | 180-210 | Housekeeping |
| `CLI` | `cli.py` | 1-100 | Entry point riga di comando |
| `Constants` | `constants.py` | - | Configurazioni globali |
| `Exceptions` | `exceptions.py` | - | Eccezioni personalizzate |

