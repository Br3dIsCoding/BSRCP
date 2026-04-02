param(
    [string]$topText,
    [string]$bottomText,
    [string]$imageId
)

$token = "your-secret-token-here"

$body = @{
    token = $token
    topText = $topText
    bottomText = $bottomText
    imageId = $imageId
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:3000/create-meme" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Meme sent successfully!"
}
catch {
    Write-Host "Error: $_"
}