"""Authorization shared by consultation JSON endpoints."""
import json
from functools import wraps
from uuid import UUID

from django.http import JsonResponse

from .models import Consultation


def doctor_consultation_required(view):
    """Require the assigned, active doctor before reading or changing a consultation."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated or not user.is_active or user.role != 'medecin':
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        try:
            data = json.loads(request.body) if request.method == 'POST' else request.GET
            if not hasattr(data, 'get'):
                raise ValueError('Expected an object')
            consultation_id = kwargs.get('consultation_id') or data.get('consultation_id')
            UUID(str(consultation_id))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Requête invalide'}, status=400)
        if not Consultation.objects.filter(id=consultation_id, medecin__user=user).exists():
            return JsonResponse({'error': 'Consultation introuvable'}, status=404)
        return view(request, *args, **kwargs)
    return wrapped
