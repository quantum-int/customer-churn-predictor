#!/bin/bash

# GitHub Repository Setup Script for Customer Churn Prediction System

echo "🚀 Setting up GitHub repository for Customer Churn Prediction System..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📁 Adding files to git..."
git add .

# Commit
echo "💾 Creating initial commit..."
git commit -m "🎉 Initial release: Customer Churn Prediction System

- Complete full-stack AI/ML application
- Random Forest model with 61.8% AUC score  
- Flask backend API with SQLite database
- Interactive dashboard with real-time predictions
- 5,000+ synthetic customer dataset
- Docker deployment configuration
- Comprehensive documentation

Features:
✅ Real-time churn prediction
✅ Customer risk segmentation  
✅ Interactive analytics dashboard
✅ RESTful API with CORS support
✅ Professional UI/UX design
✅ Export functionality
✅ Production-ready architecture"

echo "🌐 Repository ready for GitHub!"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Run: git remote add origin https://github.com/yourusername/customer-churn-prediction.git"
echo "3. Run: git push -u origin main"
echo ""
echo "For GitHub Pages deployment:"
echo "1. Go to repository Settings → Pages"
echo "2. Select 'Deploy from branch'"
echo "3. Choose 'main' branch and '/ (root)' folder"
echo ""
echo "🎯 Your application will be available at:"
echo "   https://yourusername.github.io/customer-churn-prediction"
