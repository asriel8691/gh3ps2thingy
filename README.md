# Asriel8691's GH3PS2 Thingy

A convenience toolkit for modding Guitar Hero 3 on Play Station 2  
Place the files in the same directory as the script

> Note: To convert audio files to `.vag`, use **MFAudio 1.1** by **Muzzle Flash**

1. VAGs 2 Menu music

Needs two `.vag` files, one for the left channel and other for the right channel  
Rename each channel as: `(musicname)L.vag` and `(musicname)R.vag`

2. VAG/MSV parameters

Lists parameters like internal name, samplerate and byte length of the audio file  
Can list: `.vag`, `.wad`, `.msv`, `.msvs`, `.isf`, `.imf`

3. SFX Ripper

Extracts audio files from `sfx.wad` as `.vags`

4. Swap images columns

Swaps pair of columns in `.png` and `.jpg` files  
Some images, when converted to textures with **minibuildgh3** makes pairs of columns to swap, displaying them wrong in game  
This command swaps them beforehand, so the program converts them "correctly"
