import azure.functions as func
import base64, json, os, tempfile
from . import weather_cloud, extract_chart_image_cloud

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except Exception:
        return func.HttpResponse("Invalid JSON", status_code=400)

    pdf_b64 = body.get("pdf_b64")
    file_name = body.get("file_name", "input.pdf")
    if not pdf_b64:
        return func.HttpResponse("Missing pdf_b64", status_code=400)

    with tempfile.TemporaryDirectory() as td:
        pdf_path = os.path.join(td, file_name)
        with open(pdf_path, "wb") as f:
            f.write(base64.b64decode(pdf_b64))

        weather_out = weather_cloud.run(pdf_path)
        chart_out = extract_chart_image_cloud.run(pdf_path)

    return func.HttpResponse(
        json.dumps({"file": file_name, "weather": weather_out, "chart": chart_out}),
        mimetype="application/json",
        status_code=200
    )
