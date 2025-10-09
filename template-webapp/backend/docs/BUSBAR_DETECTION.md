# 🧩 Détection et reconstruction des Jeux de Barres (Busbars) - IEC 61850

## 1. Contexte

L'objectif est de **reconstruire la topologie complète** d'un poste électrique à partir d'un fichier **IEC 61850 SCD/SCL**, notamment identifier les **Jeux de Barres (JdB / BusbarSection)** qui peuvent être:
- **Explicites** (équipement de type `BUSBAR`)
- **Implicites** (à reconstruire via analyse topologique)

## 2. Problématique

### ⚠️ Le fichier SCL ne garantit PAS la présence de tous les éléments topologiques

Contrairement au modèle **CIM (IEC 61970)**, le standard **IEC 61850** n'impose pas:
- La présence d'équipements `BUSBAR`
- La description complète des ConnectivityNodes côté barre
- L'existence de fonctions de contrôle `CBO` (Contrôle de Barre)

**Conséquence**: certains fichiers livrés par les constructeurs:
- ❌ Ne contiennent **aucun BusbarSection**
- ❌ Ne déclarent **pas tous les CN** côté barre
- ❌ Utilisent des **CN implicites** non reliés à une barre définie

## 3. Concepts clés et terminologie

| Abréviation | Signification | Norme | Description |
|-------------|---------------|-------|-------------|
| **CN** | ConnectivityNode | IEC 61850-6 | Point de connexion électrique |
| **CE** | ConductingEquipment | IEC 61850-6 | Équipement conducteur (CBR, DIS, PTR...) |
| **TE** | Terminal | IEC 61850-6 | Liaison entre CE et CN |
| **JdB** | Jeu De Barres | RTE | Busbar / BusbarSection |
| **CBO** | Contrôle de Barre | IEC 61850-7-4 | Fonction de contrôle associée à une barre |
| **SA** | Sectionneur d'Aiguillage | RTE | Disconnector reliant feeder au busbar (SA1→BB1, SA2→BB2) |
| **CBO** (Bay) | Couplage de barres | RTE | Bay contenant un disjoncteur reliant deux JdB |

## 4. Structure hiérarchique IEC 61850

```
Substation
 └─ VoltageLevel (90kV, 225kV, 400kV)
     └─ Bay (travée: BUIS1, BUIS2, CBO1, TR412...)
         ├─ ConductingEquipment (CBR, DIS, PTR, CAP, etc.)
         │    └─ Terminal → ConnectivityNode
         └─ ConnectivityNode (point de connexion)
```

**Principe fondamental**:
- Chaque **ConductingEquipment** se connecte à un/plusieurs **ConnectivityNode** via des **Terminal**
- Tous les équipements partageant le **même ConnectivityNode** sont **électriquement reliés**

## 5. Méthodologie de détection en cascade (implémentée)

Notre implémentation utilise une **approche robuste en 4 niveaux**:

### 🔍 Niveau 1 - BUSBAR explicite
```python
# Recherche d'équipements type="BUSBAR"
busbar_equipment = {
    eq_uri: eq_data for eq_uri, eq_data in equipment_nodes.items()
    if eq_data.get("type") == "BUSBAR"
}
```
**Si trouvé**:
- Extraire leurs ConnectivityNodes (via Terminals)
- Tous les équipements connectés aux mêmes CN sont reliés au busbar
- ✅ **Fiable à 100%**

### 🔍 Niveau 2 - Inférence via sectionneurs SA (implémenté)
```python
# Règle RTE: SA1 → Busbar 1, SA2 → Busbar 2
if equipment.type == "DIS" and equipment.subtype in ["SA1", "SA2", "SA3"]:
    busbar_number = int(subtype[2:])  # "SA1" → 1
    create_virtual_busbar(f"BB{busbar_number}_{voltage_level}")
```
**Logique**:
- Les **sectionneurs d'aiguillage** (SA) relient les feeders aux busbars
- SA1 = connecté au Busbar 1 (BB1)
- SA2 = connecté au Busbar 2 (BB2)
- Créer des **busbars virtuels** par VoltageLevel

**Avantages**:
- ✅ Fonctionne sans équipement BUSBAR explicite
- ✅ Respecte les conventions RTE
- ⚠️ Nécessite que les sous-types SA soient renseignés

### 🔍 Niveau 3 - Détection CBO (Couplage de barres)
```python
# Bay de couplage: relie deux busbars
if bay_name contains "CBO" or "COUPL":
    # Identifier les deux busbars reliés via ce bay
    # Créer lien topologique entre BB1 et BB2
```
**Utilité**:
- Les **bays CBO** (Couplage) relient deux JdB d'un même VoltageLevel
- Permet de détecter la présence de **double jeu de barres**
- 🚧 **TODO**: Non encore implémenté

### 🔍 Niveau 4 - Fallback ultime (VoltageLevel)
```python
# Si aucune autre méthode ne fonctionne
if len(busbars) == 0:
    # Créer UN busbar par VoltageLevel
    for voltage_level in topology.voltage_levels:
        create_busbar(f"BB_{voltage_level}")
```
**Principe**:
- Si aucun BUSBAR, SA ou CBO n'est trouvé
- Créer **1 busbar par VoltageLevel** (hypothèse: simple barre)
- Connecter **tous les équipements** du VL à ce busbar
- ⚠️ **Approximation** mais garantit un diagramme cohérent
- 🚧 **TODO**: Non encore implémenté

## 6. Risques à éviter

### ❌ Ne PAS se fier uniquement au CBO
> "Le CBO seul n'est pas suffisant, mais reste un bon indicateur."

**Pourquoi?**
- Tous les postes n'ont pas de fonction CBO explicite
- Certains constructeurs ne renseignent pas le CBO dans le SCL
- Le CBO peut exister **sans lien direct avec un CN** (fonction logique, pas topologique)

### ❌ Ne PAS se fier aux noms de ConnectivityNodes
> "POSTE/4/4BUIS1/_uuid" → CN du **feeder** BUIS1, PAS du busbar!

**Erreur fréquente**:
```python
# ❌ FAUX
if "BUIS" in cn_name or "BB" in cn_name:
    create_busbar()  # BUIS est un FEEDER, pas un BUSBAR!
```

**Correct**:
```python
# ✅ CORRECT
# Analyser les ÉQUIPEMENTS, pas les noms de CN
if equipment.type == "BUSBAR":
    use_this_as_busbar()
elif equipment.type == "DIS" and equipment.subtype == "SA1":
    infer_busbar_1()
```

## 7. Correspondance IEC 61850 ↔ CIM

| IEC 61850 (SCL) | CIM (IEC 61970) | Description | Commentaire |
|-----------------|-----------------|-------------|-------------|
| Substation | Substation | Poste physique | 1:1 |
| VoltageLevel | VoltageLevel | Niveau de tension | 1:1 |
| Bay | ConnectivityNodeContainer | Conteneur logique | 1:n |
| ConnectivityNode | ConnectivityNode | Point de connexion | Pivot principal |
| Terminal | Terminal | Lien CE-CN | Identique |
| ConductingEquipment | ConductingEquipment | Équipement | Identique |
| BUSBAR (si présent) | BusbarSection | Jeu de barres | **À reconstituer si absent** |

## 8. Implémentation actuelle

### ✅ Implémenté
- [x] Détection BUSBAR explicite (Niveau 1)
- [x] Inférence via SA1, SA2 (Niveau 2)
- [x] Extraction ConnectivityNodes et Terminals
- [x] Construction du graphe de connectivité
- [x] Création d'edges busbar→equipment

### 🚧 TODO
- [ ] Détection CBO (Niveau 3) - bays de couplage
- [ ] Fallback VoltageLevel (Niveau 4)
- [ ] Fusion de busbars via CBO
- [ ] Gestion des CN orphelins (extrémités ouvertes)
- [ ] Export vers CIM (TopologicalNode)

## 9. Exemple de reconstruction

### Cas typique: VoltageLevel 90kV avec double JdB

**Fichier SCL**:
```xml
<VoltageLevel name="4">  <!-- 90kV -->
  <Bay name="4BUIS1">    <!-- Feeder 1 -->
    <ConductingEquipment name="DIS_SA1" type="DIS">
      <Private type="RTE-ConductingEquipmentType">SA1</Private>
      <Terminal connectivityNode="POSTE/4/4BUIS1/CN_SA1_JDB1"/>
    </ConductingEquipment>
    <ConductingEquipment name="DIS_SA2" type="DIS">
      <Private type="RTE-ConductingEquipmentType">SA2</Private>
      <Terminal connectivityNode="POSTE/4/4BUIS1/CN_SA2_JDB2"/>
    </ConductingEquipment>
  </Bay>
</VoltageLevel>
```

**Reconstruction**:
1. ✅ Aucun équipement `type="BUSBAR"` trouvé
2. ✅ Détecté: DIS avec subtype="SA1" et "SA2"
3. ✅ Création de 2 busbars virtuels:
   - `busbar_BB1_4` (pour SA1)
   - `busbar_BB2_4` (pour SA2)
4. ✅ Connexion:
   - BB1 → DIS_SA1 (via CN_SA1_JDB1)
   - BB2 → DIS_SA2 (via CN_SA2_JDB2)

**Résultat visuel**:
```
   BB1 ═══════════════ BB2    (Busbars virtuels 90kV)
    │                   │
   SA1                 SA2     (Sectionneurs d'aiguillage)
    │                   │
   ...                 ...     (Feeders)
```

## 10. Références

- **IEC 61850-6**: Configuration description language for communication in electrical substations
- **IEC 61850-7-4**: Compatible logical node classes and data object classes
- **IEC 61970-301**: Common Information Model (CIM) - Base
- **RTE conventions**: Nomenclature des équipements HTA/HTB

## 11. Points d'attention

| Situation | Action recommandée | Priorité |
|-----------|-------------------|----------|
| BUSBAR explicite avec CN lié | Utiliser directement | ✅ Fiable |
| SA1, SA2 détectés | Créer busbars virtuels | ✅ Fiable |
| CBO présent sans BUSBAR | Inférer 2 busbars reliés | ⚠️ Heuristique |
| Aucun BUSBAR, SA ou CBO | 1 busbar par VoltageLevel | ⚠️ Fallback |
| CN orphelin unique | Marquer comme extrémité ouverte | 🚧 À qualifier |

## 12. Conclusion

La reconstruction des busbars dans IEC 61850 nécessite une **approche multi-niveaux robuste**:

1. **Niveau 1** (idéal): BUSBAR explicite → Utiliser directement
2. **Niveau 2** (fréquent): Inférer via SA1, SA2 → Conventions RTE
3. **Niveau 3** (complexe): Analyser CBO pour double JdB → Heuristique
4. **Niveau 4** (fallback): 1 busbar par VoltageLevel → Garantie minimale

> ⚠️ **Le CBO seul n'est jamais suffisant** - il faut combiner analyse structurelle, interprétation fonctionnelle et règles de continuité.

---

**Auteur**: Claude Code + Aurélien
**Date**: 2025-10-09
**Version**: 1.0
