from fastapi import FastAPI, APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime

from configurations import collection
from database.schemas import all_tasks
from database.models import Todo

app = FastAPI()
router = APIRouter()


@app.get("/todos")
async def read_user():
    data = collection.find()
    print(data)
    return all_tasks(data)

@app.post("/todos")
async def create_post(new_todo: Todo):
    try:
        resp = collection.insert_one(dict(new_todo))
        return {"status code": status.HTTP_201_CREATED, "id": str(resp.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Some error occured as {e}")

@app.put("/todos/{task_id}")
async def upadte_todos(task_id: int, updated_task: Todo):
    try:
        id = ObjectId(task_id)
        existing_docs = collection.find_one({"id": id, "is_completed": False})
        if not existing_docs:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Task doesn't existed.")
        updated_task.updated_at = datetime.timestamp(datetime.now())
        resp = collection.update_one({"id": id}, {"$set": dict(updated_task)})
        return {"status code": status.HTTP_200_OK, "message": "Task Updated Succesfully!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Some error occured as {e}")

@app.delete("/todos/{task_id}")
async def delete_todo(task_id: int):
    try:
        id = ObjectId(task_id)
        existing_docs = collection.find_one({"id": id, "is_deleted": False})
        if not existing_docs:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Task doesn't existed.")
        existing_docs.is_deleted = True
        resp = collection.update_one({"id": id}, {"$set": dict(existing_docs)})
        return {"status code": status.HTTP_204_NO_CONTENT, "message": "Task Deleted Succesfully!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Some error occured as {e}")
    
app.include_router(router)
