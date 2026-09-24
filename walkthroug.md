<!-- frontend -->
cd ~/Downloads/RailOptix-main
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
<!-- backend -->
cd ~/Downloads/RailOptix-main/client
npm run dev