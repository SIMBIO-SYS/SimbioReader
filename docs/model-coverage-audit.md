# Audit di copertura XML dei modelli SimbioReader

Data dell'audit: 2026-07-23.

## Ambito

Il confronto riguarda i modelli aggiunti in `simbio_classes` e i relativi blocchi
XML:

- `SIMBIO_General_Parameters`;
- `STC`, `HRIC` e `VIHI`;
- `Display_Settings`;
- `Imaging`;
- `Geometry`;
- `Reference_List`.

Sono stati analizzati tutti i file `.lblx` attualmente presenti in `tests/data`:

- `sim_raw_hric_cruise_ico4b_2021-04-24_001`;
- `sim_raw_stc_cruise_ico4b_2021-04-24_001`;
- `sim_raw_vihi_cruise_ico4b_2021-04-24_002`.

L'audit non comprende i blocchi generali PDS, le strutture
`File_Area_Observational` e le definizioni di array o tabelle, che appartengono
al reader preesistente e non ai modelli oggetto del confronto.

## Risultato sintetico

| Stato | Numero |
|---|---:|
| Campi XML di valore non modellati | 1 (intenzionalmente) |
| Problemi di collegamento al reader | 0 |
| Gruppi di attributi `unit` non conservati | 0 |

L'unico campo di valore non modellato è `integration_time`, omesso
intenzionalmente perché in dismissione. I 28 campi dei sette vettori geometrici
sono ora coperti.

## Campi e collegamenti scoperti

Gli ID riportati di seguito sono stabili e possono essere usati per richiedere
una specifica implementazione.

### Parametri generali SIMBIO

| ID | Stato | Percorso XML | File interessati | Nota |
|---|---|---|---|---|
| `SC-SIM-001` | Non modellato intenzionalmente | `SIMBIO/SIMBIO_General_Parameters/integration_time` | HRIC, STC, VIHI | Il campo verrà rimosso a breve dallo schema/XML; per questo motivo non è stato modellato e non è prevista la sua implementazione in `SimbioReader`. |

### Collegamento HRIC

| ID | Stato | Percorso/campo | File interessati | Nota |
|---|---|---|---|---|
| `SC-HRIC-001` | Risolto | `SIMBIO/HRIC` → `Simbio._hric` | HRIC | Implementato il ramo `INSTRUMENT.HRIC`: `Hric.from_xml()` popola ora `reader.simbio.hric`. |

Campi ora disponibili grazie a `SC-HRIC-001`:

- `windows_read`;
- `window`;
- `test_mode`;
- `detector_clock`;
- `HRIC_HK/tec_current`;
- `HRIC_HK/pe_voltage`;
- `HRIC_General_Parameters/Ifov/hk_angle_param`;
- `HRIC_General_Parameters/Focal_Length/hk_length_param`;
- `HRIC_General_Parameters/f_number`;
- tutti i campi di `Detector`;
- `filter_available`.

### Vettori geometrici VIHI

Il blocco `Geometry_Orbiter/Vectors` è presente soltanto nel fixture VIHI ed è
ora rappresentato da `GeometryVectors`. Nei canali in cui il blocco non è
presente, i sette attributi della classe valgono `None`.

| ID | Stato | Blocco XML | Campi scoperti |
|---|---|---|---|
| `SC-GEO-001` | Risolto | `Vector_Cartesian_Position_Earth_To_Spacecraft` | `x_position`, `y_position`, `z_position`, `light_time_correction_applied` |
| `SC-GEO-002` | Risolto | `Vector_Cartesian_Position_Spacecraft_To_Target` | `x_position`, `y_position`, `z_position`, `light_time_correction_applied` |
| `SC-GEO-003` | Risolto | `Vector_Cartesian_Position_Sun_To_Spacecraft` | `x_position`, `y_position`, `z_position`, `light_time_correction_applied` |
| `SC-GEO-004` | Risolto | `Vector_Cartesian_Position_Sun_To_Target` | `x_position`, `y_position`, `z_position`, `light_time_correction_applied` |
| `SC-GEO-005` | Risolto | `Vector_Cartesian_Velocity_Spacecraft_Relative_To_Earth` | `x_velocity`, `y_velocity`, `z_velocity`, `light_time_correction_applied` |
| `SC-GEO-006` | Risolto | `Vector_Cartesian_Velocity_Spacecraft_Relative_To_Sun` | `x_velocity`, `y_velocity`, `z_velocity`, `light_time_correction_applied` |
| `SC-GEO-007` | Risolto | `Vector_Cartesian_Velocity_Spacecraft_Relative_To_Target` | `x_velocity`, `y_velocity`, `z_velocity`, `light_time_correction_applied` |

Il percorso comune è:

```text
Geometry/Geometry_Orbiter/Vectors/Vectors_Cartesian_Specific
```

Le componenti di posizione hanno unità `km`; quelle di velocità hanno unità
`km/s`.

## Attributi `unit`

Le classi conservano i contenuti numerici e i relativi attributi XML `unit`
tramite campi `*_unit`.

| ID | Stato | Modelli interessati | Attributi coperti |
|---|---|---|---|
| `SC-UNIT-INS-001` | Risolto | `Stc`, `Hric`, `Vihi` | Unità di clock, correnti, tensioni, temperature, angoli, lunghezze focali e dimensioni pixel |
| `SC-UNIT-IMG-001` | Risolto | `Imaging` | Unità di esposizione, banda, lunghezza d'onda centrale, FOV e temperature |
| `SC-UNIT-GEO-001` | Risolto | `Geometry` | Unità di angoli, footprint, distanze, coordinate pixel, latitudini e longitudini |
| `SC-UNIT-VEC-001` | Risolto | Vettori geometrici | Unità `km` e `km/s` delle componenti indicate da `SC-GEO-001`–`SC-GEO-007` |

## Blocchi senza campi di valore scoperti

- `Display` copre tutti i campi osservati in `Display_Settings`;
- `Imaging` copre tutti i campi osservati, incluse le differenze VIHI
  (`Optical_Filter` e temperature assenti);
- `Reference` copre `lid_reference`, `lidvid_reference`, `reference_type`,
  `doi` e `reference_text`;
- `Stc` copre tutti i valori del blocco STC;
- `Hric.from_xml()` copre tutti i valori del blocco HRIC;
- `Vihi` copre tutti i valori del blocco VIHI;
- `Geometry` copre tutti i valori osservati, inclusi i sette vettori.

## Ordine suggerito di implementazione

Non rimangono implementazioni prioritarie tra gli ID rilevati dall'audit.

`SC-SIM-001` è escluso dalle priorità perché documenta un'omissione
intenzionale relativa a un campo in dismissione.
