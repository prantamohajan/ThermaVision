# 🔥 ThermaVision

ThermaVision is a real-time thermal vision simulation system built using **Python** and **OpenCV**.  
It transforms normal webcam input into a **thermal-like heatmap view**, especially optimized for **low-light environments**. 🌙🔥

---

## 🚀 Features

✨ Real-time webcam processing  
🌡️ Thermal heatmap visualization using OpenCV colormap  
🌙 Low-light enhancement (Gamma Correction)  
🎯 Adaptive contrast improvement using CLAHE  
🧠 Noise reduction with Bilateral Filtering  
🔄 Side-by-side original & processed output  

---

## 🛠️ Tech Stack

- 🐍 Python  
- 📸 OpenCV  
- 🔢 NumPy  

---

## ⚙️ How It Works

This project simulates thermal vision by processing each frame from the webcam:

- 📈 **Gamma Correction** → Brightens dark areas  
- 🎯 **CLAHE (Adaptive Contrast)** → Enhances local details  
- 🧹 **Noise Reduction** → Smoothens image while preserving edges  
- 🌈 **Color Mapping (JET)** → Converts grayscale into thermal-style heatmap  

OpenCV color mapping is commonly used to visualize heat intensity in images and thermal-like effects. :contentReference[oaicite:0]{index=0}  

---

## ▶️ Usage

```bash
python main.py
