"""
TTS 语音播报助手
"""
import os
import base64
import requests
from pathlib import Path

# ElevenLabs API 配置
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

class TTSAssistant:
    """TTS 语音播报助手"""
    
    def __init__(self, api_key=None, voice_id=None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.voice_id = voice_id or ELEVENLABS_VOICE_ID
        self.api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
    
    def speak(self, text, stability=0.5, similarity_boost=0.8):
        """生成语音"""
        if not self.api_key:
            return {
                "error": "未配置 ElevenLabs API Key",
                "hint": "请设置环境变量 ELEVENLABS_API_KEY"
            }
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 返回 base64 音频
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            
            return {
                "audio": f"data:audio/mpeg;base64,{audio_base64}",
                "text": text,
                "duration": len(response.content) / 16000  # 估算
            }
        
        except requests.exceptions.RequestException as e:
            return {"error": f"TTS 请求失败: {str(e)}"}
    
    def speak_chinese(self, text):
        """中文语音播报"""
        return self.speak(text)
    
    def speak_english(self, text):
        """英文语音播报"""
        return self.speak(text)


class VoiceHelper:
    """语音助手"""
    
    # 预设语音
    VOICES = {
        "Rachel": "21m00Tcm4TlvDq8ikWAM",      # 温和女声
        "Domi": "AZnzlk1XvdvUeBnXmlld",       # 年轻女声
        "Bella": "EXAVITQu4vr4xnSDxMaL",      # 活泼女声
        "Arnold": "EQUxZ7g4SpWnNttjqmQm",      # 男性声音
        "Adam": "oWyFzF4S3uLhIjxpegpeq",       # 男性声音
    }
    
    @staticmethod
    def speak_with_voice(text, voice_name="Bella"):
        """使用指定声音播报"""
        voice_id = VoiceHelper.VOICES.get(voice_name, VoiceHelper.VOICES["Bella"])
        tts = TTSAssistant(voice_id=voice_id)
        return tts.speak(text)


# 快捷函数
def speak(text, voice="Bella"):
    """快捷语音播报"""
    return VoiceHelper.speak_with_voice(text, voice)


if __name__ == "__main__":
    # 测试
    print("=== TTS 测试 ===")
    tts = TTSAssistant()
    result = tts.speak("你好！欢迎使用校徽网。")
    
    if "error" in result:
        print(f"预期错误: {result['error']}")
    else:
        print(f"✓ 语音生成成功 (预计 {result.get('duration', 0):.1f} 秒)")
