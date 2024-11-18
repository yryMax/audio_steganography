from scipy.io import wavfile
from IPython.display import Audio, display
import pywt
from scipy.fftpack import dct, idct, fft, ifft
from scipy.signal import correlate
import numpy as np
import pandas as pd
import util
import argparse
class Config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_from_args(self, args):
        for key, value in vars(args).items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


def parse_args():
    parser = argparse.ArgumentParser(description="Audio Steganography Tool")
    parser.add_argument('--alpha', type=float, default=0.4, help='Strength of watermark embedding/extraction')

    subparsers = parser.add_subparsers(dest='mode', required=True, help="Mode of operation: 'embed' or 'extract'")

    embed_parser = subparsers.add_parser('embed', help='Embed a message into an audio file')
    embed_parser.add_argument('--audio', type=str, required=True, help='Path to the input audio file')
    embed_parser.add_argument('--message', type=str, default='Default Message' , help='Message')
    embed_parser.add_argument('--output', type=str, default='./output.wav',
                              help='Path to save the stego audio file (default: output.wav)')
    embed_parser.add_argument('--channel', type=str, default='cD', choices=['cA', 'cD'], help='Channel to embed the message')

    extract_parser = subparsers.add_parser('extract', help='Extract a message from a stego audio file')
    extract_parser.add_argument('--audio', type=str, required=True, help='Path to the original audio file')
    extract_parser.add_argument('--stegoAudio', type=str, required=True, help='Path to the stego audio file')
    extract_parser.add_argument('--channel', type=str, default='cD', choices=['cA', 'cD'], help='Channel to extract the message')


    return parser.parse_args()



def embed(audio_file, message, output_file, config):
    # read audio file
    rate, data = util.getAudioData(audio_file)
    print(data.shape)
    data = data / data.max()
  #  wavfile.write('normalized.wav', rate, data)

    # getpayload
    base, payload = util.getPayload(data, config.channel)
   # wavfile.write('payload.wav', rate // 2, payload)
   # wavfile.write('base.wav', rate // 2, base)

    # embed message
    payload_wm = util.embedChannel(payload, message, config.alpha)
    print(payload_wm.shape)
 #   wavfile.write('payload_wm.wav', rate // 2, payload_wm)

    # merge payload
    data_wm = util.mergePayload(base, payload_wm, config.channel)

    # write audio file
    wavfile.write(output_file, rate, data_wm)

    return output_file

def extract(audio_file, stego_audio_file, config):
    # read audio files
    rate, data = util.getAudioData(audio_file)
    rate_stego, data_stego = util.getAudioData(stego_audio_file)
    data = data / data.max()
    data_stego = data_stego / data_stego.max()


    # getpayload
    base, payload = util.getPayload(data, config.channel)

    base_stego, payload_stego = util.getPayload(data_stego, config.channel)

    # extract message
    message = util.extractChannel(payload_stego, payload, config.alpha)

    return message

if __name__ == '__main__':
    args = parse_args()
    config = Config()
    config.update_from_args(args)

    if config.mode == 'embed':
        embed(config.audio, config.message, config.output, config)
        print("Message embedded to audio file: ", config.output)
    elif config.mode == 'extract':
        print(extract(config.audio, config.stegoAudio, config))
    else:
        print("Invalid mode. Use 'embed' or 'extract'")