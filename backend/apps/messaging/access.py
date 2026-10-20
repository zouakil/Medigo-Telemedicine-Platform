"""Access checks for private consultation attachments."""
def is_participant(request, consultation):
    user = request.user
    if user.is_authenticated and user.is_active and user.role == 'medecin':
        return bool(consultation.medecin_id and consultation.medecin.user_id == user.id)
    return (
        str(consultation.patient_id) == request.session.get('patient_id')
        and consultation.patient.est_actif
    )
