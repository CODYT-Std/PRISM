from flask import Flask, request, Response, abort
import os

app = Flask(__name__)

VIDEO_FOLDER = "/opt/render/project/src/videos"


def get_video_path(video_id):
    filename = f"{video_id}.mp4"
    path = os.path.join(VIDEO_FOLDER, filename)

    if not os.path.exists(path):
        return None

    return path


@app.route("/stream/<video_id>")
def stream(video_id):
    path = get_video_path(video_id)

    if not path:
        return abort(404)

    file_size = os.path.getsize(path)
    range_header = request.headers.get("Range", None)

    if not range_header:
        with open(path, "rb") as f:
            data = f.read()
        return Response(data, mimetype="video/mp4")

    bytes_range = range_header.replace("bytes=", "").split("-")
    start = int(bytes_range[0]) if bytes_range[0] else 0
    end = int(bytes_range[1]) if len(bytes_range) > 1 and bytes_range[1] else file_size - 1

    length = end - start + 1

    with open(path, "rb") as f:
        f.seek(start)
        chunk = f.read(length)

    response = Response(
        chunk,
        206,
        mimetype="video/mp4",
        direct_passthrough=True
    )

    response.headers.add("Content-Range", f"bytes {start}-{end}/{file_size}")
    response.headers.add("Accept-Ranges", "bytes")
    response.headers.add("Content-Length", str(length))

    return response


@app.route("/")
def home():
    return "Streaming server online"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
