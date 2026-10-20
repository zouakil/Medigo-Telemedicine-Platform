import csv
import os
import sys
import django
import argparse
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, str(Path(__file__).resolve().parent))
django.setup()

from apps.ordonnances.models import Medicament

def clean(val):
    return val.strip() if val else ''

def trunc(val, length):
    return val[:length] if val else ''

def import_medicaments(csv_path):
    created = 0
    skipped = 0
    seen = set()

    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        required = {'STATUT AMM', 'STATUT COMMERCIALISATION', 'SPECIALITE', 'DOSAGE', 'FORME', 'SUBSTANCE ACTIVE', 'CLASSE THERAPEUTIQUE'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('Missing CSV columns: ' + ', '.join(sorted(required - set(reader.fieldnames or []))))
        for row in reader:
            statut_amm = clean(row.get('STATUT AMM', ''))
            statut_com = clean(row.get('STATUT COMMERCIALISATION', ''))

            if 'ENREGISTREE' not in statut_amm:
                skipped += 1
                continue
            if 'Commercialis' not in statut_com and 'Commrcialisé' not in statut_com:
                skipped += 1
                continue

            nom = clean(row.get('SPECIALITE', ''))
            dosage = clean(row.get('DOSAGE', ''))
            forme = clean(row.get('FORME', ''))
            dci = clean(row.get('SUBSTANCE ACTIVE', ''))
            categorie = clean(row.get('CLASSE THERAPEUTIQUE', ''))

            if not nom:
                skipped += 1
                continue

            key = f"{nom}|{dosage}|{forme}".upper()
            if key in seen:
                skipped += 1
                continue
            seen.add(key)

            if categorie in ('NA', '0', ''):
                categorie = 'Autre'

            _, was_created = Medicament.objects.get_or_create(
                nom=trunc(nom.title(), 200),
                dci=trunc(dci.title(), 500),
                forme=trunc(forme.title(), 200),
                dosage=trunc(dosage, 100),
                categorie=trunc(categorie.title(), 500),
            )
            created += int(was_created)
            skipped += int(not was_created)

    print(f"Imported: {created} medicaments, skipped: {skipped}")

if __name__ == '__main__':
    from django.db import transaction
    parser = argparse.ArgumentParser(description='Import a medicine CSV without deleting existing records.')
    parser.add_argument('csv_path', type=Path)
    args = parser.parse_args()
    with transaction.atomic():
        import_medicaments(args.csv_path)
