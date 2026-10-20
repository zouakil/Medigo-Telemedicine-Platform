from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.consultations.models import Consultation
from apps.accounts.models import MedecinProfile


class Command(BaseCommand):
    help = 'Nettoie les consultations abandonnées'

    def handle(self, *args, **options):
        limite = timezone.now() - timedelta(hours=2)
        abandonnees = Consultation.objects.filter(
            statut='en_cours',
            demarree_le__lt=limite
        )
        count = abandonnees.count()
        abandonnees.update(
            statut='expiree',
            cloturee_le=timezone.now(),
            ended_by='systeme'
        )
        MedecinProfile.objects.filter(
            statut='occupe',
            consultations__statut='expiree'
        ).update(statut='disponible')
        self.stdout.write(f'{count} consultations abandonnées nettoyées')
