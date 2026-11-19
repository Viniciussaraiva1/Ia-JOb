import shutil, sys
from gradio_client import Client, handle_file
img, out, dur, prompt = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
S = "/tmp/claude-0/-home-user-Ia-JOb/8d7de059-9405-567d-85ae-68433aa2ddf9/scratchpad"
c = Client("https://lightricks-ltx-video-distilled.hf.space/", headers={"Authorization": "Bearer proxy-injected"}, download_files=S + "/dl", verbose=False)
v, seed = c.predict(prompt, "worst quality, inconsistent motion, blurry, jittery, distorted, deformed face, extra limbs, morphing",
                    handle_file(img), None, 896, 512, "image-to-video", dur, 9, 42, False, 1, True, api_name="/image_to_video")
shutil.copy(v["video"] if isinstance(v, dict) else v, out)
print("ok", out)
