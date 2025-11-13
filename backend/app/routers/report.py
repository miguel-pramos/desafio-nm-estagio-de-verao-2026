import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/report", tags=["report"])

FILE_DIRECTORY = "static"


@router.get("")
async def generate_report():
    """Generate and return a report."""

    headers = {"Content-Disposition": 'inline; filename="report.pdf"'}

    res = FileResponse(
        path=os.path.join(FILE_DIRECTORY, "report.pdf"),
        media_type="application/pdf",
        filename="report.pdf",
        headers=headers
    )

    return res
