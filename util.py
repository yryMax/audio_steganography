from scipy.io import wavfile
import pywt
from scipy.fftpack import dct, idct, fft, ifft
import numpy as np
from scipy.signal import correlate


def getAudioData(audioPath):
    rate, data = wavfile.read(audioPath)
    return rate, data


def getPayload(data , channel = 'cD'):
    if channel not in ['cA', 'cD']:
        raise ValueError('Invalid channel')

    cA, cD = pywt.dwt(data, 'db1')

    if channel == 'cA':
        return cD, dct(cA, norm='ortho')
    else:
        return cA, dct(cD, norm='ortho')

def mergePayload(data, wm_payload, channel = 'cD'):
    if channel not in ['cA', 'cD']:
        raise ValueError('Invalid channel')

    wm_channel = idct(wm_payload, norm='ortho')
    if channel == 'cA':
        return pywt.idwt(wm_channel, data, 'db1')
    else:
        return pywt.idwt(data, wm_channel, 'db1')

def embedChannel(payload, message, alpha):
    message_bits = ''.join([format(ord(c), '08b') for c in message])
    alpha = alpha * (max(payload) - min(payload))
    watermarked_payload = payload.copy()
    wm_inx = 0
    for i in range(watermarked_payload.size):
        if watermarked_payload[i] == 0:
            continue
        watermarked_payload[i] += alpha * int(message_bits[wm_inx]) * payload[i]
        wm_inx = (wm_inx + 1) % len(message_bits)
    return watermarked_payload


def extractChannel(payload_stego, payload, alpha):
    alpha = alpha * (max(payload) - min(payload))

    extracted_message_bits = np.zeros(payload_stego.size)
    for i in range(payload_stego.size):
        if abs(payload[i]) <= 1e-6:
            continue
        extracted_message_bits[i] = (payload_stego[i] - payload[i]) / alpha / payload[i]

    # z normalize
    extracted_message_bits = (extracted_message_bits - extracted_message_bits.mean()) / extracted_message_bits.std()
    extracted_message_bits = (extracted_message_bits > 0).astype(int)

    # get period
    autocorr = correlate(extracted_message_bits, extracted_message_bits, mode='full')
    autocorr = autocorr[len(autocorr) // 2:]
    period = np.argmax(autocorr[1:]) + 1

    # majority vote
    extracted_message_bits_x = extracted_message_bits[:len(extracted_message_bits) // period * period].reshape(-1,
                                                                                                              period)
    extracted_message = (np.mean(extracted_message_bits_x, axis=0) + 0.5).astype(int)

    message = ''.join([chr(int(''.join(map(str, extracted_message[i:i + 8])), 2)) for i in range(0, len(extracted_message), 8)])
    return message