<div align="center">
  <h1>🔐 CipherX</h1>
  <p><b>A modern, interactive Cryptography Suite with Premium UI/UX</b></p>
</div>

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-REST%20API-green)

CipherX is a comprehensive web-based cryptography tool designed to encrypt, decrypt, and perform cryptanalysis using classical ciphers. It features a polished, modern, glassmorphism-inspired User Interface with smooth interactions and a responsive design.

## ✨ Features

- **Multiple Classical Ciphers**:
  - **Caesar Cipher**: Shift-based substitution.
  - **Affine Cipher**: Mathematical substitution using modular arithmetic.
  - **Substitution Cipher**: Arbitrary key-based letter substitution.
- **Advanced Cryptanalysis**: 
  - Real-time frequency analysis.
  - Automatic cipher and language detection.
- **Multi-language Support**: Encrypt and decrypt text in multiple alphabets (including English, Arabic, etc.).
- **Modern SPA Frontend**: An intuitive single-page application built with Vanilla JS, HTML, and high-quality CSS.
- **RESTful API Backend**: Powered by Python and Flask for robust and quick analysis.

## 📸 Interface Overview

*(You can add screenshots of your premium UI here)*
- **Sleek Aesthetics**: Beautiful dark mode with dynamic gradients.
- **Interactive Charts**: Visualize character frequencies seamlessly.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yacine-louis/ISEC.git
   cd ISEC
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   python main.py
   ```
   > The server will start (defaulting to port `5000`) and the application will automatically open in your default web browser.

## 🧪 Testing

The project includes a suite of unit tests for the cryptographic algorithms. To run the tests, execute the following commands from the root directory:

```bash
# Run a specific test module
python -m tests.<module_name>

# Example: Run Caesar cipher tests
python -m tests.cesar_test

# Example: Run Affine cipher tests
python -m tests.affine_test
```

## 📁 Project Structure

```text
ISEC/
├── app/                  # Frontend SPA and Flask Server
│   ├── static/           # CSS, JS, and image assets
│   ├── templates/        # HTML templates
│   └── server.py         # Flask REST API endpoints
├── src/                  # Core Cryptography Logic
│   ├── affine.py         # Affine cipher implementation
│   ├── auto_detect.py    # Auto-detection & frequency analysis logic
│   ├── cesar.py          # Caesar cipher implementation
│   ├── languages.py      # Multi-language definitions & frequencies
│   └── substitute.py     # Substitution cipher implementation
├── tests/                # Unit Tests for algorithms
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check out the repository issues page if you want to contribute.

## 📜 License

This project is open-source and available under the terms of the [MIT License](LICENSE).
