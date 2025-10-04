# PrivChat - Secure AI Chat Platform

A privacy-focused chat application that uses AI to detect and protect Personally Identifiable Information (PII) in real-time conversations.

## Features

- Real-time PII detection using spaCy
- AI-powered responses with Ollama integration
- Beautiful, minimalistic modern UI with dark theme
- End-to-end encryption
- Keyboard shortcuts for better UX
- Responsive design for all devices

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/privchat.git
cd privchat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Ollama:
- Visit [Ollama's official website](https://ollama.ai) and download the installer
- Run the installer and follow the setup instructions
- Pull the required model:
```bash
ollama pull llama2
```

4. Start the application:
```bash
uvicorn main:app --reload
```

5. Open your browser and navigate to:
```
http://localhost:8000
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: spaCy (NER), Ollama (LLM)
- **Styling**: Custom CSS with modern design principles

## 📝 Usage

1. Type your message in the input box
2. The system will automatically detect any PII
3. Detected PII will be highlighted and tagged
4. The AI will provide a response while maintaining privacy
5. Use Ctrl+Enter to quickly send messages

## 📸 Screenshots & Demo

Below are some screenshots and a demo video showcasing PrivChat in action.

### Screenshots

![Web View](Screenshots%20%26%2video/PrivChat1.png)
![Prompt & output](Screenshots%20%26%20video/PrivChat2.png)
![Console & visual display of Detected Name Enities & LLM's Reponse](Screenshots%20%26%20video/PrivChat3.png)

### Demo Video

[![Watch the Demo](Screenshots%20%26%20video/PrivChat1.png)](https://drive.google.com/file/d/1IuUaMSQkMwdwI4Ao1mqUwkkuvfBwf6mb/view?usp=sharing)
check video folder in the repo
<!-- 

-->

## Security Features

- PII detection and masking
- Secure API endpoints
- Input sanitization
- Error handling and logging
- People's own offline partner

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments 

- [FastAPI](https://fastapi.tiangolo.com/)
- [spaCy](https://spacy.io/)
- [Ollama](https://ollama.ai/)
- [GitHub](https://github.com/) 








