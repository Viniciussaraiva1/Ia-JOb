import shutil, sys
from gradio_client import Client
out, seed, prompt = sys.argv[1], int(sys.argv[2]), sys.argv[3]
c = Client("https://black-forest-labs-flux-1-dev.hf.space/", headers={"Authorization": "Bearer proxy-injected"}, download_files="/tmp/claude-0/-home-user-Ia-JOb/8d7de059-9405-567d-85ae-68433aa2ddf9/scratchpad/dl", verbose=False)
r, s = c.predict(prompt, seed, False, 576, 1024, 3.5, 24, api_name="/infer")
shutil.copy(r if isinstance(r, str) else r["path"], out)
print("ok", out, s)
