# PC-INFO-DASHBOARD

Tableau de bord système ultime en Tkinter, créé par hackers_tchad.

## Description

`pc-info-dashboard.py` affiche plus de 100 informations système en temps réel :

- Utilisation CPU globale et par cœur
- Mémoire RAM et Swap
- Disques et partitions
- Réseau (envoyé/reçu par interface)
- Batterie
- GPU (via GPUtil)
- Processus
- Console Matrix animée
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

## Avertissement

Usage éducatif uniquement.
