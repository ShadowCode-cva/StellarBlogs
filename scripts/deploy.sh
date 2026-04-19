#!/bin/bash
cd /vercel/share/v0-project
git add .
git commit -m "Deploy StellarBlogs to Vercel" --allow-empty
git push origin project-setup
echo "Push complete! Now creating PR..."
