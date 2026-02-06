#!/bin/bash

# AI Operations Assistant - Quick Start Script

echo "=================================="
echo "AI Operations Assistant Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo "   Get your API key from: https://console.anthropic.com/"
    echo ""
    read -p "Press Enter to continue after adding your API key..."
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check installation
echo ""
echo "Verifying installation..."
python3 test.py

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Try these commands:"
echo '  python main.py "Find popular Python repositories"'
echo '  python main.py "What is the weather in London?"'
echo "  python main.py --api  # Start REST API server"
echo "  python demo.py        # Run interactive demos"
echo ""
echo "For detailed usage, see SETUP_GUIDE.md"
echo ""
