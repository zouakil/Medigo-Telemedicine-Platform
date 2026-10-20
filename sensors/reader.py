import smbus2
import time
import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')
BASE_URL = os.getenv('MEDIGO_BASE_URL', 'http://localhost').rstrip('/')
SENSOR_HEADERS = {'X-Sensor-Key': os.getenv('SENSOR_API_KEY', '')}

MLX_ADDR = 0x5a
MAX_ADDR = 0x57
DJANGO_URL = BASE_URL + '/api/sensors/data/'
ACTIVE_URL = BASE_URL + '/api/sensors/active-consultation/'
CAPTEURS_URL = BASE_URL + '/api/sensors/capteurs-actifs/'
INTERVAL = 2

def read_temperature():
    bus = smbus2.SMBus(1)
    try:
        data = bus.read_i2c_block_data(MLX_ADDR, 0x07, 3)
        temp_raw = (data[1] << 8) | data[0]
        temp = round(temp_raw * 0.02 - 273.15, 1)
        return temp
    except Exception as e:
        print(f"MLX90614 erreur: {e}")
        return None
    finally:
        bus.close()

def init_max30102():
    bus = smbus2.SMBus(1)
    try:
        # Reset
        bus.write_byte_data(MAX_ADDR, 0x09, 0x40)
        time.sleep(0.5)

        # FIFO Config: no averaging, rollover enabled
        bus.write_byte_data(MAX_ADDR, 0x08, 0x10)
        time.sleep(0.05)

        # SpO2 Config: ADC range 4096, 100 SPS, 411us pulse
        bus.write_byte_data(MAX_ADDR, 0x0A, 0x27)
        time.sleep(0.05)

        # LED Pulse Amplitude
        bus.write_byte_data(MAX_ADDR, 0x0C, 0x24)
        bus.write_byte_data(MAX_ADDR, 0x0D, 0x24)
        time.sleep(0.05)

        # Clear FIFO pointers
        bus.write_byte_data(MAX_ADDR, 0x04, 0x00)
        bus.write_byte_data(MAX_ADDR, 0x05, 0x00)
        bus.write_byte_data(MAX_ADDR, 0x06, 0x00)
        time.sleep(0.05)

        # Mode: SpO2 mode — MUST BE LAST to start acquisition
        bus.write_byte_data(MAX_ADDR, 0x09, 0x03)
        time.sleep(0.5)

        print("MAX30102 initialisé ✅")
    except Exception as e:
        print(f"MAX30102 init erreur: {e}")
    finally:
        bus.close()

def read_max30102_fifo():
    """Lire toutes les données disponibles du FIFO"""
    bus = smbus2.SMBus(1)
    red_samples = []
    ir_samples = []
    try:
        write_ptr = bus.read_byte_data(MAX_ADDR, 0x04)
        read_ptr = bus.read_byte_data(MAX_ADDR, 0x06)

        # Calculer le nombre d'échantillons disponibles
        num_samples = write_ptr - read_ptr
        if num_samples < 0:
            num_samples += 32  # FIFO wrap-around

        if num_samples == 0:
            return [], []

        # Limiter à 16 échantillons max par lecture
        num_samples = min(num_samples, 16)

        for _ in range(num_samples):
            raw = bus.read_i2c_block_data(MAX_ADDR, 0x07, 6)
            red = ((raw[0] & 0x03) << 16) | (raw[1] << 8) | raw[2]
            ir = ((raw[3] & 0x03) << 16) | (raw[4] << 8) | raw[5]
            if red > 1000 and ir > 1000:  # Filtrer le bruit
                red_samples.append(red)
                ir_samples.append(ir)

        return red_samples, ir_samples
    except Exception as e:
        print(f"MAX30102 FIFO erreur: {e}")
        return [], []
    finally:
        bus.close()

def calculate_spo2(red_values, ir_values):
    """Calculer SpO2 à partir de plusieurs échantillons"""
    if not red_values or not ir_values or len(red_values) < 5:
        return None

    # Moyenne des valeurs
    red_avg = sum(red_values) / len(red_values)
    ir_avg = sum(ir_values) / len(ir_values)

    if ir_avg == 0 or red_avg == 0:
        return None

    # Calculer AC (variation) et DC (moyenne) pour chaque canal
    red_ac = max(red_values) - min(red_values)
    ir_ac = max(ir_values) - min(ir_values)

    if ir_ac == 0 or red_avg == 0:
        return None

    # Ratio of ratios
    ratio = (red_ac / red_avg) / (ir_ac / ir_avg) if ir_avg > 0 else 0

    # Formule empirique SpO2
    spo2 = 110 - 25 * ratio
    spo2 = max(70, min(100, round(spo2, 1)))

    return spo2

def calculate_heart_rate(ir_history, sample_rate=25):
    """Calculer le BPM à partir de l'historique IR"""
    if len(ir_history) < 30:
        return None

    # Utiliser les 100 derniers échantillons
    data = ir_history[-100:] if len(ir_history) > 100 else ir_history[:]

    # Moyenne mobile pour lisser
    smoothed = []
    w = 3
    for i in range(len(data)):
        start = max(0, i - w)
        end = min(len(data), i + w + 1)
        smoothed.append(sum(data[start:end]) / (end - start))

    # Seuil dynamique
    min_val = min(smoothed)
    max_val = max(smoothed)
    amplitude = max_val - min_val

    if amplitude < 200:
        return None  # Signal trop faible

    threshold = min_val + amplitude * 0.5

    # Détecter les pics
    peaks = []
    min_distance = max(3, sample_rate // 5)  # Distance min entre pics

    for i in range(2, len(smoothed) - 2):
        if (smoothed[i] > smoothed[i-1] and
            smoothed[i] > smoothed[i-2] and
            smoothed[i] > smoothed[i+1] and
            smoothed[i] > smoothed[i+2] and
            smoothed[i] > threshold):
            if not peaks or (i - peaks[-1]) >= min_distance:
                peaks.append(i)

    if len(peaks) < 2:
        return None

    # Calculer BPM à partir des intervalles entre pics
    intervals = []
    for i in range(1, len(peaks)):
        intervals.append(peaks[i] - peaks[i-1])

    avg_interval = sum(intervals) / len(intervals)

    if avg_interval == 0:
        return None

    # Convertir en BPM
    bpm = (sample_rate / avg_interval) * 60
    bpm = round(bpm)

    if bpm < 40 or bpm > 200:
        return None

    return bpm

def get_active_consultation():
    try:
        response = requests.get(ACTIVE_URL, headers=SENSOR_HEADERS, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get('consultation_id')
    except Exception as e:
        print(f"Pas de consultation active: {e}")
    return None

def get_capteurs_actifs(consultation_id):
    try:
        response = requests.get(f"{CAPTEURS_URL}?consultation_id={consultation_id}", headers=SENSOR_HEADERS, timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {'spo2': False, 'temperature': False}

def send_to_django(consultation_id, temperature, spo2, heart_rate):
    try:
        payload = {
            'consultation_id': consultation_id,
            'temperature': temperature,
            'spo2': spo2,
            'frequence_cardiaque': heart_rate,
            'source': 'combined',
            'qualite_lecture': 'bon'
        }
        response = requests.post(DJANGO_URL, json=payload, headers=SENSOR_HEADERS, timeout=3)
        if response.status_code == 200:
            print(f"✅ Envoyé: SpO2={spo2}% FC={heart_rate} T={temperature}°C")
        else:
            print(f"❌ Erreur Django: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur envoi: {e}")

def main():
    print("=== Medigo Sensor Reader v2 ===")
    init_max30102()
    ir_history = []
    red_history = []
    # Approximation: avec avg=4 et 100Hz, on obtient ~25 samples/sec
    SAMPLE_RATE = 25

    while True:
        try:
            consultation_id = get_active_consultation()

            if not consultation_id:
                print("Aucune consultation active — capteurs en veille")
                ir_history = []
                red_history = []
                time.sleep(INTERVAL)
                continue

            capteurs = get_capteurs_actifs(consultation_id)
            spo2_actif = capteurs.get('spo2', False)
            temp_actif = capteurs.get('temperature', False)

            temperature = None
            spo2 = None
            heart_rate = None

            if temp_actif:
                temperature = read_temperature()

            if spo2_actif:
                red_samples, ir_samples = read_max30102_fifo()

                if ir_samples:
                    ir_history.extend(ir_samples)
                    red_history.extend(red_samples)

                    # Garder max 200 échantillons
                    if len(ir_history) > 200:
                        ir_history = ir_history[-200:]
                    if len(red_history) > 200:
                        red_history = red_history[-200:]

                    spo2 = calculate_spo2(red_samples, ir_samples)
                    heart_rate = calculate_heart_rate(ir_history, SAMPLE_RATE)
                else:
                    print("  Pas de signal — vérifiez le doigt sur le capteur")
            else:
                ir_history = []
                red_history = []

            print(f"T={temperature}°C | SpO2={spo2}% | FC={heart_rate} | Samples IR={len(ir_history)} | SpO2 actif={spo2_actif} | Temp actif={temp_actif}")

            if spo2_actif or temp_actif:
                send_to_django(consultation_id, temperature, spo2, heart_rate)

            time.sleep(INTERVAL)

        except KeyboardInterrupt:
            print("\nArrêt du reader")
            break
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
