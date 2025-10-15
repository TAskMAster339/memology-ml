# 🧠 Memology-ML — AI Meme Generation Engine for the **Memology** Service

> **Memology-ML** is the core machine learning component of the **Memology** project —  
> an AI-powered meme generation platform.  
> This module is responsible for creating **visual meme content** and **funny captions** using **Stable Diffusion WebUI** and **Ollama (LLaMA 3.2)**.
>
> All processing runs **locally**, so your memes are created **privately and offline**.

## 🎨 Example Memes

| Input Idea                | Generated Meme                                    |
| ------------------------- | ------------------------------------------------- |
| “кот пьет кофе”           | ![cat meme](examples/cat_with_coffee_example.png) |
| “лошадь чихнула”          | ![night coder meme](examples/horse_example.png)   |
| “компьютер и ежу понятен” | ![computer meme](examples/computer_example.png)   |

---

## 🚀 Features

- 🖼️ Generates high-quality memes locally
- 🎨 Random visual styles (realistic, anime, horror, etc.)
- 🧠 English image prompts generated automatically from Russian ideas
- 😂 Funny short Russian captions
- ✍️ Automatic text overlay with Impact font
- 📜 Full logging of generation process
- 💾 Saves images in `generated_images/`

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/meme-generator.git
cd meme-generator
```

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # Linux / macOS
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🧠 Ollama Setup

Ollama is used for generating text prompts and captions.

### Install Ollama

👉 [https://ollama.com/download](https://ollama.com/download)

### Pull the LLaMA 3.2 model

```bash
ollama pull llama3.2:2b
```

Check it works:

```bash
ollama run llama3.2:2b
```

---

## 🎨 Stable Diffusion WebUI Setup

Stable Diffusion WebUI (by AUTOMATIC1111) is used for image generation.

### 1️⃣ Install WebUI

👉 [https://github.com/AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

### 2️⃣ Run WebUI with API enabled

```bash
python launch.py --api
```

This starts the API at:

```
http://127.0.0.1:7860/sdapi/v1/txt2img
```

### 3️⃣ (Optional) Add custom models

You can download additional models from [Civitai](https://civitai.com):

| Model            | Style                      | Link                                                                                               |
| ---------------- | -------------------------- | -------------------------------------------------------------------------------------------------- |
| **Memes XL**     | Meme-style, funny, vibrant | [https://civitai.com/models/205229/memes-xl](https://civitai.com/models/205229/memes-xl)           |
| **Crazy Horror** | Dark, surreal, horror      | [https://civitai.com/models/1101129/crazy-horror](https://civitai.com/models/1101129/crazy-horror) |

Place downloaded `.safetensors` files into:

```
stable-diffusion-webui/models/Stable-diffusion/
```

---

## 🧩 Configuration

- **LLM model:** `llama3.2:2b`
- **Sampler:** `Euler a`
- **Steps:** 20
- **CFG Scale:** 7
- **Resolution:** 512×512

You can change these parameters in `generate_image()` inside `main.py`.

---

## 🧠 Usage

Simply run:

```bash
python main.py
```

The program will:

1. Take a short idea (e.g., "кот пьет кофе")
2. Generate a detailed English scene description
3. Generate a short, funny Russian caption
4. Create the image in a random style (anime, realistic, horror, etc.)
5. Overlay the caption in meme format
6. Save and log the result

---

## 📜 Logging

Each generation is saved in `generation.log`, e.g.:

```
2025-10-14 23:40:54 | INFO | Model: llama3.2:3b | Prompt: кот пьет кофе | Visual: A small white kitten sits at a tiny wooden table, its fur fluffed up slightly as it gazes intently at a delicate china cup filled with steaming hot coffee... | Caption: Кот пьет кофе, а я пью чай. | RawFile: meme_20251014_234051_15f351c6_raw.png | FinalFile: meme_20251014_234054_b3e571e5_final.png | Time: 169.58s
```

---

## 📁 Project Structure

```
meme-generator/
│
├── examples/              # example memes (for README)
├── generated_images/      # auto-generated memes
├── impact.ttf             # meme font
├── main.py                # main program
├── requirements.txt       # dependencies
├── generation.log         # log file
└── README.md              # this file
```

---

## 🖼 Folder `examples/`

Add here a few example memes for your README:

```
examples/cat_with_coffee_example.png
examples/horse_example.png
examples/computer_example.png
```

These will be displayed at the top of the README.

---

## ⭐️ Contributing

Contributions are welcome!  
You can improve meme caption generation, add new visual styles, or optimize performance.

---

## 🧰 Tips

- Lower `steps` to `15` for faster generation.
- Use _SDXL_ or _Anything V5_ for more realistic output.
- Try _Crazy Horror_ for dark surreal memes.
- Everything works offline — no API keys required!
