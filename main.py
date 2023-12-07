from typing import Union
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

task_results = {}


def do_operation(
    x: Union[int, float], y: Union[int, float], operator: str
) -> Union[int, float]:
    if operator == "+":
        return x + y
    elif operator == "-":
        return x - y
    elif operator == "*":
        return x * y
    elif operator == "/":
        if y == 0:
            raise ValueError("Деление на ноль")
        return x / y
    else:
        raise ValueError("Введите корректный оператор")


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def on_background(result, task_id):
    print(f"Задача с ID {task_id}: {result}")


@app.post("/do/", response_class=HTMLResponse)
async def do_and_save_result(
    request: Request,
    background_tasks: BackgroundTasks,
    x: Union[int, float] = Form(...),
    y: Union[int, float] = Form(...),
    operator: str = Form(...),
):
    result = do_operation(x, y, operator)
    task_id = len(task_results) + 1
    task_results[task_id] = result

    background_tasks.add_task(on_background, result, task_id)

    return templates.TemplateResponse(
        "result.html", {"request": request, "task_id": task_id, "result": result}
    )


@app.get("/result/{task_id}", response_class=HTMLResponse)
async def get_result(task_id: int, request: Request):
    result = task_results.get(task_id)
    if result is not None:
        return templates.TemplateResponse(
            "result.html", {"request": request, "task_id": task_id, "result": result}
        )
    else:
        raise HTTPException(status_code=404, detail="Задача не найдена")


@app.get("/status/", response_class=HTMLResponse)
async def get_task_statuses(request: Request):
    return templates.TemplateResponse(
        "statuses.html",
        {"request": request, "task_statuses": list(task_results.keys())},
    )
