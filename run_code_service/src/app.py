from fastapi import FastAPI
from pydantic import BaseModel
from run_code import run_user_code_in_docker

app = FastAPI()


class RunCodeRequest(BaseModel):
    user_code: str
    author_code: str
    checker: str
    tests: list[str]
    time_limit: int
    memory_limit: int


class RunCodeResponse(BaseModel):
    status: str   # AC, WA, TL, RE, Fail
    test_error: int | None
    message: str | None


@app.post("/run_code", response_model=RunCodeResponse)
def run_code(request: RunCodeRequest):
    result = run_user_code_in_docker(
        user_code=request.user_code,
        author_code=request.author_code,
        checker=request.checker,
        tests=request.tests,
        time_limit=request.time_limit,
        memory_limit=request.memory_limit,
    )
    return RunCodeResponse(**result)

# docker run -v /var/run/docker.sock:/var/run/docker.sock -v /tmp/code_runner_data:/tmp/code_runner_data -d -p 8080:8080 run_code_service
