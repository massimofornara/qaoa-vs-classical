#!/bin/bash

# Titolo: crea_video_tiktok.sh
# Requisiti: apt install imagemagick ffmpeg -y

mkdir -p tiktok_video
cd tiktok_video

# Parametri
WIDTH=1080
HEIGHT=1920
BG_COLOR="#0f142d"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Frame 1
convert -size ${WIDTH}x${HEIGHT} canvas:$BG_COLOR \
  -gravity center \
  -font "$FONT" -pointsize 70 \
  -fill white -annotate +0+0 "💸 Vuoi guadagnare con crypto bot\ne intelligenza artificiale?" \
  frame1.png

# Frame 2
convert -size ${WIDTH}x${HEIGHT} canvas:$BG_COLOR \
  -gravity center \
  -font "$FONT" -pointsize 65 \
  -fill white -annotate +0+0 "✅ Arbitraggio automatico\n✅ Grid trading su Binance\n✅ Scrittura eBook AI vendibili" \
  frame2.png

# Frame 3
convert -size ${WIDTH}x${HEIGHT} canvas:$BG_COLOR \
  -gravity center \
  -font "$FONT" -pointsize 60 \
  -fill white -annotate +0+0 "📦 Scarica tutto su gumroad.com/massimocrypto\n🚀 Link completo in bio" \
  frame3.png

# Unisci i frame in video con durata specifica
ffmpeg -y -loop 1 -t 2 -i frame1.png \
       -loop 1 -t 4 -i frame2.png \
       -loop 1 -t 4 -i frame3.png \
       -filter_complex "[0:v][1:v][2:v]concat=n=3:v=1:a=0[outv]" \
       -map "[outv]" -pix_fmt yuv420p -s ${WIDTH}x${HEIGHT} TikTok_CryptoBot_Template.mp4

echo "✅ Video generato: tiktok_video/TikTok_CryptoBot_Template.mp4"
