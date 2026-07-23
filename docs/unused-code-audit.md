# Audit del codice non utilizzato

Data dell'audit: 2026-07-23.

## Obiettivo e metodo

L'analisi copre `sr.py`, tutti i moduli importati dal package
`src/SimbioReader` e i test correnti. Sono stati incrociati:

- definizioni AST di classi, funzioni e metodi;
- riferimenti per nome e accessi ad attributi nel package e nei test;
- registrazioni Click dei comandi CLI;
- esportazioni pubbliche in `__init__.py`;
- flusso effettivo del costruttore di `SimbioReader`;
- diagnostica Ruff per import, variabili e nomi non risolti.

L'assenza di utilizzi interni non prova che un simbolo pubblico non sia usato da
client esterni. Per questo ogni voce ha un livello di confidenza:

- **alta**: codice non raggiungibile dal reader corrente e non esportato;
- **media**: metodo pubblico senza chiamanti interni, spesso legato alla vecchia
  struttura;
- **bassa**: possibile API di convenienza, da verificare prima della rimozione.

Gli ID sono stabili e possono essere usati per approvare una rimozione
specifica. Lo stato delle voci viene aggiornato quando una rimozione è
approvata.

## Nucleo legacy in `sr.py`

Le quattro classi seguenti formano un sottosistema collegato internamente, ma
il costruttore corrente di `SimbioReader` non crea più un oggetto `Data`.
Non sono esportate dal package e non sono istanziate dai test.

| ID | Simbolo | Confidenza | Funzionalità precedente | Evidenza e nota per la rimozione |
|---|---|---|---|---|
| `UC-SR-001` | `Detector` | Alta | Estraeva detector e FOV da nodi DOM `img:Subframe` e produceva un pannello Rich. | Rimasta senza chiamanti dopo la rimozione di `SimbioObject`. Sostituita da `ImagingDetector`, `Subframe` e dai detector STC/HRIC. |
| `UC-SR-002` | `HK` | Alta | Trasformava la prima riga di un DataFrame housekeeping in attributi dinamici e pannello Rich. | Usata soltanto da `Data`. Le nuove classi `StcHousekeeping`, `HricHousekeeping` e `VihiHousekeeping` forniscono dati tipizzati. |
| `UC-SR-003` | `SimbioObject` | Rimosso | Caricava direttamente array NumPy per filtri/segmenti, associando detector, filtro e struttura dati. | Classe rimossa insieme ai punti di costruzione legacy presenti in `Data`. |
| `UC-SR-004` | `Data` | Alta | Catalogava file osservazionali, CSV, filtri STC/HRIC e segmenti VIHI. | Non viene più assegnata a `SimbioReader.data`; il reader usa ora strutture `pds4_tools` e modelli XML tipizzati. |

Queste classi dovrebbero essere valutate e, se approvate, rimosse insieme:
eliminare solo una parte lascerebbe riferimenti interni incoerenti.

### Metodi del nucleo legacy

| ID | Simbolo | Confidenza | Funzionalità precedente | Nota |
|---|---|---|---|---|
| `UC-SR-005` | `SimbioObject.show()` | Rimosso | Mostrava riepilogo di filtro, detector e struttura dati. | Rimosso insieme a `SimbioObject`; è sostituito dal nuovo `SimbioReader.show()` basato sulle dataclass. |
| `UC-SR-006` | `SimbioObject.savePreview()` | Rimosso | Convertiva l'array in PNG/TIFF e generava frammenti browse PDS4. | Rimosso insieme alla classe `SimbioObject`. |
| `UC-SR-007` | `Data.savePreview()` | Gestito come obsoleto | Iterava filtri o segmenti delegando a `SimbioObject.savePreview()`. | Mantiene temporaneamente la firma per compatibilità, ma ora stampa un warning e solleva `DeprecatedMethodError`. È prevista la rimozione in una versione futura. |

## Metodi legacy rimasti su `SimbioReader`

Questi metodi non hanno chiamanti nel package o nei test. Inoltre fanno
riferimento ad attributi (`self.data`, `self.img`) che il nuovo costruttore non
inizializza.

| ID | Metodo | Confidenza | Funzionalità | Rischio attuale |
|---|---|---|---|---|
| `UC-SR-008` | `filters_summary()` | Rimosso | Creava un pannello con i nomi dei filtri presenti in `self.data.filters`. | Rimosso: dipendeva dalla struttura legacy `self.data`, non più popolata. |
| `UC-SR-009` | `get_filter_by_file()` | Rimosso | Cercava un vecchio `SimbioObject` filtro tramite nome file. | Rimosso: dipendeva dalla struttura legacy `self.data`, non più popolata. |
| `UC-SR-010` | `get_filters()` | Rimosso | Restituiva tutti i vecchi oggetti filtro. | Rimosso: dipendeva dalla struttura legacy `self.data`, non più popolata. |
| `UC-SR-011` | `get_segment_by_file()` | Conservato con vincolo | Cerca una struttura array VIHI tramite il nome del relativo file. | Usa direttamente `data_arrays` e restituisce un risultato soltanto per prodotti VIHI contenenti più di un array. |
| `UC-SR-012` | `image()` | Rimosso | Convertiva `self.img` in un'immagine Pillow. | Rimosso: `self.img` non appartiene alla nuova struttura del reader. |

### Preview obsoleta

| ID | Elemento | Confidenza | Stato |
|---|---|---|---|
| `UC-SR-013` | Corpo storico dopo `raise DeprecatedMethodError` in `SimbioReader.savePreview()` | Rimosso | Eliminato il blocco irraggiungibile; rimane soltanto lo stub deprecato con firma compatibile, warning ed eccezione. |

`SimbioReader.savePreview()` non è classificato come metodo inutilizzato:
esiste intenzionalmente per compatibilità, stampa il warning richiesto ed è
coperto da test.

## Moduli e simboli duplicati

| ID | Simbolo | Confidenza | Funzionalità | Evidenza |
|---|---|---|---|---|
| `UC-MOD-001` | `filters_tools.Filter` | Alta | Leggeva le tabelle statiche HRIC/STC e costruiva un filtro dinamico. | Non è più importato da `sr.py` dopo la rimozione di `SimbioObject`; la nuova `OpticalFilter` legge direttamente la label. Esiste anche una distinta classe `simbioInfo.Filter`, ancora usata dalla CLI informativa. |
| `UC-MOD-002` | `filters_tools.show_filters()` | Alta | Genera una tabella Rich con tutti i filtri statici di un canale. | Nessun chiamante. La CLI usa invece `simbioInfo.show_filters()`, che svolge la stessa funzione. |
| `UC-CON-001` | `constants.FMODE` | Alta | Espone costanti testuali per modalità file (`r`, `rb`, `w`, `wb`, `a`). | Nessun riferimento nel package o nei test. |
| `UC-EXC-001` | `exceptions.SizeError` | Rimosso | Segnalava una differenza tra dimensione effettiva e attesa dell'array. | Rimossa insieme ai test dedicati dopo la rimozione di `SimbioObject`, unico utilizzatore in produzione. |

I dizionari in `filters.py`, `phases.py`, `subphases.py` e `tests.py` **non**
sono inutilizzati: sono consumati da `simbioInfo.py` e dalla relativa CLI.

## Analisi della CLI

Il package pubblica ora un solo entry point in `pyproject.toml`:

| Comando installato | Callback | Stato |
|---|---|---|
| `simbioReader` | `SimbioReader.cli:cli` | Gruppo Click raggiungibile anche tramite `python -m SimbioReader`; registra `version`, `about`, `phases`, `filters` e `info`. |

Le funzionalità supportate della precedente CLI `simbioInfo` sono disponibili
nei sottocomandi `phases` e `filters` della CLI principale. L'entry point
separato e il modulo `infocli.py` sono stati rimossi.

Non risultano callback inutilizzati nella nuova `cli.py`:

- `version()` mostra la versione del package e la compatibilità con i modelli
  PDS e SIMBIO-SYS;
- `about()` legge autore, contatti e descrizione dai metadati installati;
- `phases()` unifica la visualizzazione di fasi, sottofasi e test;
- `filters()` espone le informazioni dei filtri HRIC e STC;
- `info()` contiene il precedente flusso di lettura di un prodotto specifico.

Stato delle anomalie precedentemente identificate:

| ID | Elemento | Tipo | Evidenza e raccomandazione |
|---|---|---|---|
| `UC-CLI-001` | Parametro `self` di `cli.sh_version()` | Risolto | La vecchia funzione è stata rimossa e sostituita dal sottocomando `version()`. |
| `UC-CLI-002` | Variabile `ndt` in `infocli.phases()` | Rimosso | Eliminata insieme al modulo legacy `infocli.py`. |
| `UC-CLI-003` | Variabile `ndt` in `infocli.subphases()` | Rimosso | Eliminata insieme al modulo legacy `infocli.py`. |
| `UC-CLI-004` | `except:` in `infocli.tests()` | Rimosso | Eliminato insieme al modulo legacy `infocli.py`. |
| `UC-CLI-005` | Opzione `simbioReader --version` | Risolto | Sostituita da `simbioReader version`, che non richiede un prodotto. |
| `UC-CLI-006` | Invocazione senza sottocomando | Risolto | `simbioReader` senza sottocomando mostra automaticamente l'help. |
| `UC-CLI-007` | Versione hardcoded di `infocli.py` | Rimosso | Il nuovo `version` usa i metadati reali del package. |
| `UC-CLI-008` | Copertura della CLI | Risolto per i flussi correnti | I test coprono registrazione, help, `version`, `about`, `info`, fasi e normalizzazione/ricerca dei filtri. |
| `UC-CLI-009` | Modulo `infocli.py` | Rimosso | Le funzionalità supportate sono state consolidate nella CLI principale. |

Verifiche eseguite durante l'audit:

- il comando principale e gli help dei sottocomandi terminano con codice 0;
- il gruppo registra esattamente i cinque sottocomandi richiesti;
- `version` e `about` funzionano senza un file prodotto;
- `phases --kind phases` e `filters STC` producono le tabelle attese;
- la suite copre il passaggio delle opzioni `--hk`, `--detector`,
  `--data-structure`, `--all`, `--filters`, `--debug`, `--verbose` e
  `--summarize` dal sottocomando `info` a `SimbioReader`.

## API senza utilizzi interni

| ID | Simbolo | Confidenza | Funzionalità | Raccomandazione |
|---|---|---|---|---|
| `UC-API-001` | `InternalReference.identifier` | Bassa | Restituisce `lidvid_reference` quando presente, altrimenti `lid_reference`. | Nessun utilizzo interno o nei test, ma è una proprietà di convenienza plausibilmente pubblica. Verificare gli utenti esterni prima di rimuoverla; in alternativa aggiungere un test e documentarla. |

## Import e codice ausiliario eliminabili dopo approvazione

Questi elementi non sono classi o metodi, ma sono conseguenze dirette del
codice candidato alla rimozione.

| ID | Elemento | Stato |
|---|---|---|
| `UC-IMP-001` | `from dateutil import parser` in `sr.py` | Rimosso. |
| `UC-IMP-002` | `instruments` importato in `sr.py` | Conservato esplicitamente come riesportazione di compatibilità. |
| `UC-AUX-001` | Variabile `ndt` in `infocli.phases()` | Rimossa insieme a `infocli.py`. |
| `UC-AUX-002` | Variabile `ndt` in `infocli.subphases()` | Rimossa insieme a `infocli.py`. |
| `UC-ERR-001` | Nome `DataStructure` in `SimbioObject.__init__()` | Risolto tramite la rimozione di `UC-SR-003` e dei relativi punti di costruzione. |

Dopo la rimozione del nucleo legacy e del corpo storico della preview, vanno
ricontrollati anche gli import di NumPy, pandas, Pillow, `hashlib`,
`xml.dom.minidom`, `Filter` e `data_types`: oggi sono mantenuti quasi
esclusivamente da quel codice.

## Funzioni di `tools.py`

Non risultano funzioni completamente isolate:

- `getValue()` e `getElement()` sono testate e sono usate dal nucleo legacy;
- `gen_filename()`, `lidUpdate()`, `lvidUpdate()`, `updateXML()` e
  `pretty_print()` non sono più importate da `sr.py` dopo la rimozione di
  `UC-SR-013`, ma restano funzioni pubbliche coperte dai test;
- `getFromXml()`, `lidGenerator()` e `new_lvid()` sono dipendenze delle
  funzioni precedenti e sono coperte dai test.

Se vengono approvati `UC-SR-001`–`UC-SR-007`, occorre effettuare
un secondo audit di `tools.py`: alcune funzioni potrebbero diventare realmente
inutilizzate in produzione, pur restando richiamate dai test unitari.

## Ordine suggerito per l'analisi manuale

1. Valutare insieme le voci residue `UC-SR-001`–`UC-SR-007` e
   `UC-MOD-001`; `UC-EXC-001` è stato rimosso.
2. Completato: rimossi `UC-SR-008`–`UC-SR-010` e `UC-SR-012`;
   `UC-SR-011` è stato adattato ai prodotti VIHI multi-array.
3. Completato: eliminato il corpo irraggiungibile `UC-SR-013`, mantenendo lo
   stub deprecato.
4. Rimuovere i simboli certi e isolati `UC-MOD-002`, `UC-CON-001`,
   `UC-IMP-001` e `UC-IMP-002`.
5. Correggere `UC-AUX-001` e `UC-AUX-002`.
6. Trattare `UC-API-001` solo dopo una verifica di compatibilità esterna.
7. Ripetere l'analisi statica di `tools.py` dopo le rimozioni approvate.
8. Completato: `UC-CLI-009` è stato rimosso e la copertura indicata in
   `UC-CLI-008` è stata aggiornata.
