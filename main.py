from dotenv import load_dotenv
import logfire
from fastapi import FastAPI
from controllers import router
import uvicorn
import os

load_dotenv()

logfire.configure(token='pylf_v1_eu_QspjdvKdFC6vydQQ6cyD5y7w0vtZBjGTCV8bCLhDZHwF')
logfire.instrument_openai_agents()

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
