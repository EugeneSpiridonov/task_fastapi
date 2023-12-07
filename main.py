from typing import Union
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from celery.result import AsyncResult
from tasks import do_operation

app = FastAPI()
templates = Jinja2Templates(directory="templates")

task_results = {}


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/do/", response_class=HTMLResponse)
async def do_and_save_result(
    request: Request,
    x: Union[int, float] = Form(...),
    y: Union[int, float] = Form(...),
    operator: str = Form(...),
):
    result = do_operation.delay(x, y, operator)
    task_id = len(task_results) + 1
    task_results[task_id] = result.id

    return templates.TemplateResponse(
        "result.html", {"request": request, "task_id": task_id, "result": result.id}
    )


@app.get("/result/{task_id}", response_class=HTMLResponse)
async def get_result(task_id: int, request: Request):
    result_id = task_results.get(task_id)
    if result_id is not None:
        result = AsyncResult(result_id)
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "task_id": task_id, "result": result.result},
        )
    else:
        raise HTTPException(status_code=404, detail="Задача не найдена")


@app.get("/status/", response_class=HTMLResponse)
async def get_task_statuses(request: Request):
    return templates.TemplateResponse(
        "statuses.html",
        {"request": request, "task_statuses": list(task_results.keys())},
    )
