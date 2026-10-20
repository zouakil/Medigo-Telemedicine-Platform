"""Regression checks for access boundaries and basic application startup."""
import json
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import get_template
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User, MedecinProfile
from apps.messaging.models import ImageMedicale, Message
from apps.ordonnances.models import Ordonnance
from apps.patients.models import Patient
from .consumers import ConsultationConsumer, MedecinConsumer
from .models import Consultation


class AccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doctor = User.objects.create_user('doctor@example.test', 'test-password', role='medecin')
        cls.other = User.objects.create_user('other@example.test', 'test-password', role='medecin')
        cls.profile = MedecinProfile.objects.create(user=cls.doctor, nom='Demo', prenom='Doctor', specialite='General')
        cls.other_profile = MedecinProfile.objects.create(user=cls.other, nom='Other', prenom='Doctor', specialite='General')
        cls.patient = Patient.objects.create(nom='Demo', prenom='Patient', cin='TEST-001', telephone='000', date_naissance=date(2000, 1, 1))
        cls.consultation = Consultation.objects.create(patient=cls.patient, medecin=cls.profile, statut='en_cours')
        cls.prescription = Ordonnance.objects.create(consultation=cls.consultation, contenu='Test', storage_key='ordonnances/test.pdf')

    def post_symptoms(self, client=None, **payload):
        return (client or self.client).post(reverse('sauvegarder_symptomes'), json.dumps(payload), content_type='application/json')

    def test_owner_can_save_symptoms(self):
        self.client.force_login(self.doctor)
        response = self.post_symptoms(consultation_id=str(self.consultation.id), symptomes=['Test'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.consultation.symptomes.count(), 1)

    def test_other_doctor_cannot_modify_consultation(self):
        self.client.force_login(self.other)
        self.assertEqual(self.post_symptoms(consultation_id=str(self.consultation.id)).status_code, 404)
        self.assertEqual(self.consultation.symptomes.count(), 0)

    def test_invalid_json_is_rejected(self):
        self.client.force_login(self.doctor)
        response = self.client.post(reverse('sauvegarder_symptomes'), '[', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_csrf_is_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.doctor)
        self.assertEqual(self.post_symptoms(client, consultation_id=str(self.consultation.id)).status_code, 403)

    def test_deactivated_doctor_cannot_authenticate(self):
        self.doctor.est_actif = False
        self.doctor.save()
        self.assertFalse(self.client.login(email=self.doctor.email, password='test-password'))

    def test_doctor_activation_services(self):
        from apps.accounts.services.medecin import desactiver_medecin, reactiver_medecin
        desactiver_medecin(self.profile)
        self.doctor.refresh_from_db()
        self.assertFalse(self.doctor.is_active)
        reactiver_medecin(self.profile)
        self.doctor.refresh_from_db()
        self.assertTrue(self.doctor.is_active)

    def test_other_doctor_cannot_read_prescription(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('voir_ordonnance', args=[self.prescription.id])).status_code, 404)

    def test_anonymous_upload_is_rejected_before_storage(self):
        response = self.client.post('/api/chat/upload-image/', {'consultation_id': str(self.consultation.id)})
        self.assertEqual(response.status_code, 403)

    def test_fake_image_is_rejected(self):
        self.client.force_login(self.doctor)
        image = SimpleUploadedFile('fake.png', b'not an image', content_type='image/png')
        response = self.client.post('/api/chat/upload-image/', {'consultation_id': str(self.consultation.id), 'image': image})
        self.assertEqual(response.status_code, 400)

    def test_patient_upload_uses_session_identity(self):
        from io import BytesIO
        from PIL import Image
        session = self.client.session
        session['patient_id'] = str(self.patient.id)
        session.save()
        content = BytesIO()
        Image.new('RGB', (2, 2)).save(content, format='PNG')
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            response = self.client.post('/api/chat/upload-image/', {
                'consultation_id': str(self.consultation.id), 'expediteur': 'medecin',
                'image': SimpleUploadedFile('test.png', content.getvalue(), content_type='image/png'),
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Message.objects.get().expediteur, 'patient')
            self.assertEqual(ImageMedicale.objects.count(), 1)

    def test_private_qr_lookup(self):
        self.prescription.qr_code_key = 'qrcodes/test.png'
        self.prescription.save()
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            target = Path(directory, 'qrcodes', 'test.png')
            target.parent.mkdir()
            target.write_bytes(b'demo')
            self.client.force_login(self.doctor)
            response = self.client.get('/media/qrcodes/test.png')
            self.assertEqual(response.status_code, 200)
            response.close()

    def test_media_requires_participant(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            target = Path(directory, 'chat', 'test.png')
            target.parent.mkdir()
            target.write_bytes(b'demo')
            ImageMedicale.objects.create(consultation=self.consultation, storage_key='chat/test.png', nom_original='test.png', file_type='png')
            self.assertEqual(self.client.get('/media/chat/test.png').status_code, 404)
            self.client.force_login(self.other)
            self.assertEqual(self.client.get('/media/chat/test.png').status_code, 404)
            self.client.force_login(self.doctor)
            response = self.client.get('/media/chat/test.png')
            self.assertEqual(response.status_code, 200)
            response.close()

    @override_settings(SENSOR_API_KEY='test-device-key')
    def test_sensor_requires_device_key(self):
        self.assertEqual(self.client.get('/api/sensors/active-consultation/').status_code, 403)
        response = self.client.get('/api/sensors/active-consultation/', HTTP_X_SENSOR_KEY='test-device-key')
        self.assertEqual(response.status_code, 200)

    @override_settings(SENSOR_API_KEY='')
    def test_unconfigured_sensor_is_disabled(self):
        self.assertEqual(self.client.get('/api/sensors/active-consultation/').status_code, 403)

    def test_websocket_patient_requires_matching_session(self):
        consumer = ConsultationConsumer()
        consumer.patient_id = str(self.patient.id)
        consumer.patient_code = 'invalid'
        self.assertFalse(async_to_sync(consumer.patient_session_valid)())
        consumer.patient_code = self.patient.code_unique
        self.assertTrue(async_to_sync(consumer.patient_session_valid)())

    def test_websocket_doctor_cannot_write_to_other_consultation(self):
        consumer = MedecinConsumer()
        consumer.medecin_id = self.other_profile.id
        self.assertIsNone(async_to_sync(consumer.get_consultation)(self.consultation.id))
        async_to_sync(consumer.sauvegarder_message)(self.consultation.id, 'forbidden', 'medecin')
        self.assertEqual(Message.objects.count(), 0)

    def test_login_pages_render(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/patient/').status_code, 200)

    def test_all_templates_compile(self):
        root = settings.BASE_DIR / 'templates'
        for path in root.rglob('*.html'):
            with self.subTest(template=str(path.relative_to(root))):
                get_template(path.relative_to(root).as_posix())

    @override_settings(ENABLE_XGBOOST=False)
    def test_disabled_model_is_not_deserialized(self):
        from unittest.mock import patch
        from .services.medigo_ai_service import load_ai_bundle
        with patch('joblib.load') as load:
            with self.assertRaises(RuntimeError):
                load_ai_bundle()
            load.assert_not_called()

    @override_settings(ENABLE_XGBOOST=False)
    def test_rule_based_inference_without_model(self):
        from .services.medigo_ai_service import predict_live_consultation
        self.consultation.symptomes.create(nom_symptome='fièvre')
        result = predict_live_consultation(self.consultation.id)
        self.assertIn('diagnostics', result)
        self.assertIn('red_flags', result)
