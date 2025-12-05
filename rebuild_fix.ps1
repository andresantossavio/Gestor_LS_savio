# Remove arquivos temporários
Remove-Item "c:\PythonProjects\GESTOR_LS\frontend\react-app\src\components\TarefaDetalhesModal_NEW.jsx" -Force -ErrorAction SilentlyContinue

# Rebuild Docker
Set-Location "c:\PythonProjects\GESTOR_LS"
Write-Host "Construindo containers..." -ForegroundColor Yellow
docker-compose build

Write-Host "Iniciando containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`n✅ Concluído! Acesse http://localhost:8080" -ForegroundColor Green
