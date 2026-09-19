# PC-INFO-DASHBOARD
<img width="1283" height="700" alt="vintage-computer-setup-on-wooden-desk-with-coffee-and-plant-nostalgic-office-scene-photo" src="https://github.com/user-attachments/assets/6863a3c0-430b-41d6-9e2c-7eb689eceac4" />

Tableau de bord système ultime

## Description


- Utilisation CPU globale et par cœur
- Mémoire RAM et Swap
- Disques et partitions
- Réseau (envoyé/reçu par interface)
- Batterie
- GPU (via GPUtil)
- Processus
- Graphiques temps réel

## Prérequis

- Python 3.8+
- Système Linux / Windows / macOS

## Installation

```bash
pip install -r requirements-pc-info-dashboard.txt
python pc-info-dashboard.py
```

## Dépendances

- `psutil` : informations système
- `py-cpuinfo` : détails CPU
- `gputil` : informations GPU (optionnel)

## Utilisation

Lancez simplement le script. Les onglets permettent de naviguer entre :
- Vue d'ensemble
- CPU
- Mémoire
- Disques
- Réseau
- Batterie
- GPU
- Processus
- Matrix

AUTEUR = HACKES_TCHAD
