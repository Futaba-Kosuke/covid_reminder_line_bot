import uvicorn
from fastapi import FastAPI

app = FastAPI()


def main():
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, workers=2)


if __name__ == '__main__':
    main()
