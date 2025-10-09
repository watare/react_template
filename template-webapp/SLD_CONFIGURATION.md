# Configuration du générateur de schémas unifilaires (SLD)

## Vue d'ensemble

Toutes les valeurs de configuration du générateur SLD sont définies dans le fichier `.env` à la racine du projet. Cela permet de personnaliser facilement l'apparence et la disposition des schémas sans modifier le code.

## Variables de configuration

### Layout (Dimensions en pixels)

Ces variables contrôlent l'espacement et les dimensions des éléments du schéma :

```bash
# Hauteur des jeux de barres (lignes horizontales)
SLD_BUSBAR_HEIGHT=80

# Largeur de chaque travée (colonne verticale)
SLD_BAY_WIDTH=150

# Hauteur de chaque équipement (rectangle)
SLD_EQUIPMENT_HEIGHT=40

# Largeur de chaque équipement (rectangle)
SLD_EQUIPMENT_WIDTH=100

# Espacement vertical entre équipements
SLD_VERTICAL_SPACING=60

# Espacement horizontal entre travées
SLD_HORIZONTAL_SPACING=50

# Marge autour du schéma
SLD_MARGIN=50
```

### Couleurs (Format hexadécimal sans #)

Ces variables définissent les couleurs de chaque type d'équipement :

```bash
# Disjoncteur (Circuit Breaker)
SLD_COLOR_CBR=FF6B6B        # Rouge

# Sectionneur (Disconnector)
SLD_COLOR_DIS=4ECDC4        # Cyan

# Transformateur de courant (Current Transformer)
SLD_COLOR_CTR=95E1D3        # Vert clair

# Transformateur de tension (Voltage Transformer)
SLD_COLOR_VTR=F38181        # Rose

# Transformateur de puissance (Power Transformer)
SLD_COLOR_PTR=AA96DA        # Violet

# Condensateur (Capacitor)
SLD_COLOR_CAP=FCBAD3        # Rose clair

# Réactance (Reactor)
SLD_COLOR_REA=FFFFD2        # Jaune

# Générateur (Generator)
SLD_COLOR_GEN=A8D8EA        # Bleu clair

# Batterie (Battery)
SLD_COLOR_BAT=FED766        # Jaune

# Couleur par défaut (équipements non reconnus)
SLD_COLOR_DEFAULT=CCCCCC    # Gris
```

## Comment personnaliser

### 1. Modifier les dimensions

Pour un schéma plus compact :
```bash
SLD_BUSBAR_HEIGHT=60
SLD_BAY_WIDTH=120
SLD_EQUIPMENT_HEIGHT=30
SLD_EQUIPMENT_WIDTH=80
SLD_VERTICAL_SPACING=40
SLD_HORIZONTAL_SPACING=40
```

Pour un schéma plus aéré :
```bash
SLD_BUSBAR_HEIGHT=100
SLD_BAY_WIDTH=200
SLD_EQUIPMENT_HEIGHT=50
SLD_EQUIPMENT_WIDTH=120
SLD_VERTICAL_SPACING=80
SLD_HORIZONTAL_SPACING=80
```

### 2. Modifier les couleurs

Pour un schéma en niveaux de gris :
```bash
SLD_COLOR_CBR=333333
SLD_COLOR_DIS=666666
SLD_COLOR_CTR=999999
SLD_COLOR_VTR=AAAAAA
SLD_COLOR_PTR=444444
```

Pour un schéma coloré type RTE :
```bash
SLD_COLOR_CBR=D32F2F        # Rouge foncé
SLD_COLOR_DIS=1976D2        # Bleu
SLD_COLOR_PTR=FF6F00        # Orange
```

### 3. Appliquer les changements

Après modification du fichier `.env` :

```bash
# Redémarrer le backend
docker restart template_backend

# Ou si vous utilisez docker-compose
docker-compose restart backend
```

Les nouveaux paramètres seront immédiatement appliqués à tous les schémas générés.

## Conventions de nommage

- **Dimensions** : Toujours en pixels (entiers)
- **Couleurs** : Hexadécimal **sans le #** (ex: `FF6B6B` et non `#FF6B6B`)

## Architecture technique

### Flux de configuration

```
.env
  │
  ├─> backend/app/core/config.py (Settings class)
  │      └─> Variables chargées avec pydantic_settings
  │
  └─> backend/app/sld/simple_svg_generator.py
         └─> Utilise settings.SLD_* pour générer le SVG
```

### Ajout de nouvelles variables

Pour ajouter une nouvelle variable de configuration SLD :

1. **Ajouter dans `.env.example` et `.env`** :
   ```bash
   SLD_NEW_PARAMETER=value
   ```

2. **Déclarer dans `backend/app/core/config.py`** :
   ```python
   class Settings(BaseSettings):
       # ...
       SLD_NEW_PARAMETER: int = 100  # ou str, bool, etc.
   ```

3. **Utiliser dans le générateur** :
   ```python
   from app.core.config import settings

   value = settings.SLD_NEW_PARAMETER
   ```

## Exemples de personnalisation

### Schéma pour impression papier (haute résolution)

```bash
SLD_BUSBAR_HEIGHT=120
SLD_BAY_WIDTH=220
SLD_EQUIPMENT_HEIGHT=60
SLD_EQUIPMENT_WIDTH=150
SLD_VERTICAL_SPACING=100
SLD_HORIZONTAL_SPACING=100
SLD_MARGIN=80
```

### Schéma pour dashboard (compact)

```bash
SLD_BUSBAR_HEIGHT=50
SLD_BAY_WIDTH=100
SLD_EQUIPMENT_HEIGHT=25
SLD_EQUIPMENT_WIDTH=70
SLD_VERTICAL_SPACING=35
SLD_HORIZONTAL_SPACING=30
SLD_MARGIN=30
```

## Notes

- Les modifications du `.env` nécessitent un redémarrage du backend
- Les valeurs par défaut sont optimisées pour un affichage sur écran standard (1920x1080)
- Pour PowSyBl (intégration future), ces paramètres ne s'appliqueront qu'au générateur simple
- Les couleurs doivent être lisibles sur fond clair (#f5f5f5)

## Support

Pour toute question sur la configuration, voir :
- `backend/app/core/config.py` : Définition des variables
- `backend/app/sld/simple_svg_generator.py` : Utilisation des variables
- `.env.example` : Valeurs par défaut recommandées
