#!/bin/bash

# PROJECT PHOENIX - Setup Script

echo "🚀 Setting up PROJECT PHOENIX Telegram Bot..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$PYTHON_VERSION" \< "3.11" ]; then
    echo "❌ Python version is $PYTHON_VERSION. Please upgrade to Python 3.11 or higher."
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "📦 Installing dependencies..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies."
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file to add your Telegram bot token before running the bot!"
fi

echo "🎉 Setup complete!"
echo ""
echo "To run the bot, use:"
echo "   python src/main.py"
echo ""
echo "To run in the background:"
echo "   nohup python src/main.py > bot.log 2>&1 &"