import os
import tempfile
import shutil
from google import genai
from google.genai import types
from pathlib import Path
from utils import *
import httpx


class Gemini:

    def __init__(self, api_keys: list[str]) -> None:
        self.api_keys = api_keys
        self.client = genai.Client(api_key=api_keys[0])
        self.current_key = 0
        self.max_try = 20

    def llm_potmizer(self, file_path: Path, llm_prompt: str, trans_to: str = "None"):

        system_instruction = f"""
你是一位专业的字幕编辑器。你的任务是根据用户的要求，修正并润色 SRT 字幕文件。
字幕内容已经通过文件附件的形式提供给你。

**用户的要求如下:**
---
{llm_prompt}
---

**请遵循以下严格规则:**
1.  **保持原始 SRT 格式**: 你的输出必须是完整的、格式正确的 SRT 字幕。
2.  **不要修改序号和时间戳**。
3.  **只修改字幕文本**。
4.  **不要添加任何额外内容**: 你的回复中，除了修正后的 SRT 内容，不要包含任何解释、前言或代码块标记。

请开始处理并输出修正后的 SRT 字幕。
"""

        tmp_file_path = None
        output_path = STORAGE_PATH/("subtitles")/file_path.name
        if trans_to != "None":
            output_path = STORAGE_PATH / \
                ("subtitles_translated")/(file_path.stem+"_"+trans_to)
            output_path = output_path.with_suffix(".srt")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".srt")
        tmp_file_path = tmp.name
        tmp.close()
        shutil.copy2(str(file_path), str(tmp_file_path))
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        for i in range(self.max_try):
            try:
                print(f"正在处理字幕文件: {file_path.name}")
                print("正在向模型发送请求")

                response = self.client.models.generate_content_stream(
                    model="gemini-2.5-pro",
                    contents=[
                        text
                        # types.Part.from_bytes(
                        #     data=file_bytes,
                        #     mime_type="text/plain"
                        # ),
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                result = ""
                for chunk in response:
                    print(chunk.text)
                    result += str(chunk.text)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已导出字幕文件{output_path}")
                break

            except Exception as e:
                print(f"api[{self.current_key}]不可用")
                print(e)
                self.switch_api()

        print("正在删除:\n", str(tmp_file_path))
        os.remove(tmp_file_path)

    def test_gemini_connection(self):
        try:
            self.switch_api()
            files = self.client.files.list()
            first = next(files, None)
            print("✅ 成功连接到 Gemini Files API。")
            return True
        except httpx.ConnectError as e:
            print("❌ 网络连接错误：", e)
        except httpx.ConnectTimeout as e:
            print("❌ 连接超时：", e)
        except httpx.ReadTimeout as e:
            print("❌ 读取超时：", e)
        except Exception as e:
            print("❌ 其他错误：", type(e).__name__, e)
        return False

    def switch_api(self):
        self.current_key += 1
        self.current_key = self.current_key % len(self.api_keys)
        self.client = genai.Client(api_key=self.api_keys[self.current_key])


if __name__ == "__main__":
    system_instruction = f"""
你是一位专业的字幕编辑器。你的任务是根据用户的要求，修正并润色 SRT 字幕文件。
字幕内容已经通过文件附件的形式提供给你。

**用户的要求如下:**
---
"test"
---

**请遵循以下严格规则:**
1.  **保持原始 SRT 格式**: 你的输出必须是完整的、格式正确的 SRT 字幕。
2.  **不要修改序号和时间戳**。
3.  **只修改字幕文本**。
4.  **不要添加任何额外内容**: 你的回复中，除了修正后的 SRT 内容，不要包含任何解释、前言或代码块标记。

请开始处理并输出修正后的 SRT 字幕。
"""

    # gemini=Gemini()
    # input_file=STORAGE_PATH/"subtitles_raw"/"高等数学A（下）_中国大学MOOC(慕课).srt"
    # llm_prompt="我将会发给你关于高等数学的视频的字幕文件，因为自动识别所有有大量错误，请修正，主要是高等数学名词的修正，并将其中的繁体字改为简体字，删除末尾句号和逗号，保持时间轴不变，逐句翻译"
    # gemini.llm_potmizer(input_file,llm_prompt)

    client = genai.Client(api_key="AIzaSyDpvGlCaBl1g7zIZ2iotUp4H7BBR36h4fQ")
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=[
            "test"
        ],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    result = ""
    for chunk in response:
        print(chunk.text)
        result += str(chunk.text)
