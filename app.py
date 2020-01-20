
import json
import os
from pathlib import Path
import subprocess
import tempfile

from aiohttp import web


# Retrieve executable path from mandatory PROCESS_EXECUTABLE env variable
executable = os.getenv('PROCESS_EXECUTABLE')
if executable is None:
    raise RuntimeError('Please provide PROCESS_EXECUTABLE environment variable')

executable_path = Path(executable)
if not executable_path.exists() or not executable_path.is_file():
    raise RuntimeError('PROCESS_EXECUTABLE must be a valid path to a file')


# Get maximum process timeout from PROCESS_MAX_TIMEOUT variable (defaults to 14 minutes)
subprocess_max_timeout = os.getenv('PROCESS_MAX_TIMEOUT', None)
subprocess_max_timeout = int(subprocess_max_timeout) if subprocess_max_timeout is not None else 840


async def handler(request):

    """
      {
        "timeout": 10,  // custom timeout. defaults to and capped by PROCESS_MAX_TIMEOUT
        "params": ["--param", "value"],  // params passed to subprocess
        "file-params": [  // an array of (param, file content) tuples. Content will be written to the file and replaced by the file path
            ["--param", "file-content"]
        ]
      }
    """
    process_command = [executable_path.as_posix()]

    try:
        request_data = await request.json()
    except json.JSONDecodeError:
        if await request.text():
            print(await request.text())
            return web.Response(status=400, text='Request data must be valid JSON')
        request_data = {}

    # Timeout
    timeout = request_data.get('timeout', subprocess_max_timeout)
    timeout = min(timeout, subprocess_max_timeout)

    # Parameters
    process_command += request_data.get('params', [])

    # File parameters
    temporary_files = []
    for param, file_content in request_data.get('file-params', []):
        fp = tempfile.NamedTemporaryFile(mode='w + b', buffering=0)
        fp.write(file_content.encode())
        temporary_files.append(fp)
        process_command += [param, fp.name]

    # Start executable subprocess
    executable_process = subprocess.Popen(
        process_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Wait for subprocess to complete
        executable_process.wait(timeout=timeout)

    except subprocess.TimeoutExpired:
        # Process timeout: kill and wait until shutdown
        executable_process.kill()
        executable_process.wait()

    finally:
        # Cleanup temporary files
        for fp in temporary_files:
            fp.close()

    response_data = {
        'returncode': executable_process.returncode,
        'stdout': executable_process.stdout.read().decode(),
        'stderr': executable_process.stderr.read().decode(),
    }

    return web.json_response(response_data)


app = web.Application()
app.add_routes([web.post('/', handler)])
