@echo off
set TOP=%1
set BOTTOM=%2
set IMAGE=%3
set TOKEN=your-secret-token-here

curl -X POST http://localhost:3000/create-meme ^
  -H "Content-Type: application/json" ^
  -d "{\"token\":\"%TOKEN%\",\"topText\":\"%TOP%\",\"bottomText\":\"%BOTTOM%\",\"imageId\":\"%IMAGE%\"}"

echo Meme sent!