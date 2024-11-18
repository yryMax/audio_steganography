# audio_steganography

#### EXAMPLE USAGE:

extract watermark:

`python watermark.py extract --audio ./audio_example/payload.wav --stegoAudio ./output.wav`

embed watermark:

`python watermark.py embed --audio ./audio_example/payload.wav `

#### CREDITS:
https://github.com/ausilianapoli/Audio-watermark-using-DWT-DCT-scrambling-image

https://link.springer.com/chapter/10.1007/3-540-61996-8_41


#### NOTE:
- 如果wm在D带上，noise std>0.001的时候几乎就完全看不出来了。（我参考的一个reference实现里，他attack noise最大也只开到0.0001，可见确实是难顶 ）
std = 0.0005，对应alpha的调整值为0.3左右.
- 如果wm在A带上，保真度就极其的差（回音仙人）。
- 这东西还有一个致命的缺点，就是要原音频，不然没法反演，(但也不能说这完全是一个坏事，因为如果原音频是安全的，这个水印方法就是安全的，相比于LSB而言，假设别人知道你用了LSB，那
攻击者就可以随意篡改水印)



