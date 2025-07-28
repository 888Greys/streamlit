# 🎩 Alfred - Your Gala Butler

Alfred is a sophisticated AI butler assistant designed for elegant gala events. Built with LangGraph and powered by Groq's Gemma2 model, Alfred can help you with guest information, weather updates, and web searches.

## 🌟 Features

- **👥 Guest Information**: Query detailed information about gala attendees
- **🌐 Web Search**: Get current information and news
- **🌤️ Weather & Fireworks**: Check weather conditions and get fireworks scheduling advice
- **💬 Beautiful Web Interface**: Streamlit-powered chat interface with conversation memory

## 🚀 Live Demo

[Deploy on Streamlit Cloud](https://share.streamlit.io/)

## 🛠️ Local Setup

### Prerequisites

- Python 3.8+
- Groq API Key (get one at [console.groq.com](https://console.groq.com))
- OpenWeatherMap API Key (optional, for real weather data)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd huggingface
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run the application**
   ```bash
   streamlit run alfred_frontend.py
   ```

## 🌐 Deployment on Streamlit Cloud

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Alfred Gala Butler"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Connect your GitHub account
3. Select your repository
4. Set the main file path: `alfred_frontend.py`
5. Add environment variables in the "Advanced settings":
   - `GROQ_API_KEY`: Your Groq API key
   - `WEATHER_API_KEY`: Your OpenWeatherMap API key (optional)

## 🔧 Configuration

### Environment Variables

- `GROQ_API_KEY`: Required for AI responses
- `WEATHER_API_KEY`: Optional for real weather data (falls back to simulated data)

### Guest Database

The guest information is stored in `guest_data.json`. You can modify this file to add your own gala attendees.

## 🎯 Usage Examples

- **Guest Inquiry**: "Tell me about Ada Lovelace"
- **Weather Check**: "What's the weather in London?"
- **Web Search**: "Search for recent AI news"
- **Fireworks Planning**: "Should we have fireworks tonight in Paris?"

## 🏗️ Architecture

- **Frontend**: Streamlit web interface
- **AI Model**: Groq's Gemma2-9b-it
- **Agent Framework**: LangGraph for tool orchestration
- **Tools**: Guest database, web search, weather API

## 📁 Project Structure

```
huggingface/
├── alfred_frontend.py      # Main Streamlit app
├── app.py                 # CLI version
├── retriever.py           # Guest information retrieval
├── tools.py              # Additional tools
├── guest_data.json       # Guest database
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🎩 About Alfred

Alfred is your distinguished digital butler, ready to assist with any gala-related inquiries. With his sophisticated knowledge base and real-time information access, he ensures your event runs smoothly and elegantly.

*"At your service, sir."* - Alfred