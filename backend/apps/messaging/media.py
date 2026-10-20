from django.core.files.storage import default_storage
from django.http import FileResponse, Http404

from apps.ordonnances.models import Ordonnance
from .access import is_participant
from .models import ImageMedicale


def private_media(request, path):
    """Serve only known attachments to their consultation participants."""
    if path.startswith('chat/'):
        record = ImageMedicale.objects.select_related(
            'consultation__patient', 'consultation__medecin'
        ).filter(storage_key=path).first()
    elif path.startswith('ordonnances/'):
        record = Ordonnance.objects.select_related(
            'consultation__patient', 'consultation__medecin'
        ).filter(storage_key=path).first()
    elif path.startswith('qrcodes/'):
        record = Ordonnance.objects.select_related(
            'consultation__patient', 'consultation__medecin'
        ).filter(qr_code_key=path).first()
    else:
        record = None
    if record is None or not is_participant(request, record.consultation):
        raise Http404
    if not default_storage.exists(path):
        raise Http404
    response = FileResponse(default_storage.open(path, 'rb'))
    response['Cache-Control'] = 'private, no-store'
    return response
