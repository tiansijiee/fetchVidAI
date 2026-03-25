"""
AI视频总结模块 - 使用Deepseek API生成视频总结
兼容OpenAI SDK格式
"""
import os
import json
import re
import sys
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置UTF-8编码输出
if sys.version_info[0] >= 3:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class AISummarizer:
    """AI视频总结器 - 使用Deepseek API"""

    # 默认配置
    DEFAULT_MODEL = os.getenv('AI_MODEL_DEFAULT', 'deepseek-chat')
    DEFAULT_MAX_TOKENS = int(os.getenv('AI_MODEL_MAX_TOKENS', 4000))
    DEFAULT_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化AI总结器

        Args:
            api_key: Deepseek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = base_url or os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')

        if not self.api_key:
            raise ValueError('DEEPSEEK_API_KEY环境变量未设置')

        # 初始化OpenAI客户端（Deepseek兼容）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def summarize_video(self, subtitle_text: str, video_title: str = '',
                        video_description: str = '') -> Dict:
        """
        生成视频总结（非流式）

        Args:
            subtitle_text: 字幕文本
            video_title: 视频标题
            video_description: 视频描述

        Returns:
            {
                'success': bool,
                'summary': str,
                'mindmap': dict,
                'key_points': list,
                'message': str
            }
        """
        try:
            # 构建提示词
            prompt = self._build_summary_prompt(
                subtitle_text, video_title, video_description
            )

            # 调用AI生成总结
            response = self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的视频内容分析师，擅长总结和提炼视频的核心内容。请输出格式化的纯文本总结。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=self.DEFAULT_TEMPERATURE,
                max_tokens=self.DEFAULT_MAX_TOKENS
            )

            # 解析AI响应
            result_text = response.choices[0].message.content

            # 清理响应文本，移除可能的markdown标记
            result_text_clean = result_text.strip()

            # 移除markdown代码块标记（如果存在）
            if result_text_clean.startswith('```json'):
                result_text_clean = result_text_clean[7:]  # 移除 ```json
            elif result_text_clean.startswith('```'):
                result_text_clean = result_text_clean[3:]  # 移除 ```

            if result_text_clean.endswith('```'):
                result_text_clean = result_text_clean[:-3]  # 移除结尾的 ```

            result_text_clean = result_text_clean.strip()

            print(f"[AI] 原始响应长度: {len(result_text)} 清理后长度: {len(result_text_clean)}", file=sys.stderr)
            print(f"[AI] 响应预览: {result_text_clean[:200]}...", file=sys.stderr)

            # 解析JSON
            try:
                result = json.loads(result_text_clean)
            except json.JSONDecodeError as je:
                print(f"[AI] JSON解析失败: {str(je)}", file=sys.stderr)
                print(f"[AI] 完整响应内容: {result_text_clean}", file=sys.stderr)
                raise

            return {
                'success': True,
                'overview': result.get('overview', ''),
                'outline': result.get('outline', []),
                'key_points': result.get('key_points', []),
                'conclusion': result.get('conclusion', {}),
                'mindmap': result.get('mindmap', {}),
                # 保留旧字段以兼容性
                'summary': result.get('overview', result.get('summary', '')),
                'segments': result.get('outline', result.get('segments', [])),
                'message': '总结生成成功'
            }

        except Exception as e:
            import traceback
            print(f"[AI] 总结异常详情: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {
                'success': False,
                'message': f'AI总结失败: {str(e)}',
                'summary': None,
                'mindmap': None,
                'key_points': []
            }

    def summarize_video_stream(self, subtitle_text: str, video_title: str = '',
                               video_description: str = ''):
        """
        生成视频总结（流式输出）

        Args:
            subtitle_text: 字幕文本
            video_title: 视频标题
            video_description: 视频描述

        Yields:
            str: 流式输出的JSON片段
        """
        try:
            # 构建提示词
            prompt = self._build_summary_prompt(
                subtitle_text, video_title, video_description
            )

            # 调用AI生成总结（流式）
            print(f"[AI] 开始流式总结，字幕长度: {len(subtitle_text)}", file=sys.stderr)

            stream = self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的视频内容分析师，擅长总结和提炼视频的核心内容。请输出格式化的纯文本总结。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=self.DEFAULT_TEMPERATURE,
                max_tokens=self.DEFAULT_MAX_TOKENS,
                stream=True
            )

            # 流式输出
            full_content = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    try:
                        # 确保内容是UTF-8编码
                        if isinstance(content, bytes):
                            content = content.decode('utf-8', errors='ignore')
                        full_content += content
                        yield content
                    except Exception as e:
                        print(f"[AI] 流式输出编码错误: {e}", file=sys.stderr)
                        continue

            print(f"[AI] 流式总结完成，总长度: {len(full_content)}", file=sys.stderr)

        except Exception as e:
            error_msg = f'AI总结失败: {str(e)}'
            print(f"[AI] 错误: {error_msg}", file=sys.stderr)
            yield json.dumps({
                'error': True,
                'message': error_msg
            }, ensure_ascii=False)

    def analyze_video_without_subtitle(self, video_title: str = '',
                                      video_description: str = '',
                                      video_tags: list = None) -> Dict:
        """
        无字幕时的视频分析（基于标题、描述、标签）

        Args:
            video_title: 视频标题
            video_description: 视频描述
            video_tags: 视频标签

        Returns:
            {
                'success': bool,
                'summary': str,
                'suggested_topics': list,
                'message': str
            }
        """
        try:
            # 构建提示词
            tags_str = ', '.join(video_tags or [])
            prompt = f"""请基于以下视频信息生成一份内容分析报告：

## 视频信息
标题: {video_title or '未知'}
描述: {video_description or '无'}
标签: {tags_str or '无'}

## 要求
由于没有字幕内容，请基于标题和描述进行分析，以JSON格式返回：

1. **summary** (string): 基于标题和描述推测视频的核心内容（不超过100字）

2. **suggested_topics** (array): 推3-5个可能的视频主题话题

3. **likely_content_type** (string): 推测的内容类型（教程/解说/娱乐/新闻等）

4. **suggested_questions** (array): 推荐3-5个用户可能想问的问题

请确保返回纯JSON格式。"""

            # 调用AI
            response = self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个视频内容分析师，擅长根据标题和描述推测视频内容。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            # 解析响应
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            return {
                'success': True,
                'summary': result.get('summary', ''),
                'suggested_topics': result.get('suggested_topics', []),
                'likely_content_type': result.get('likely_content_type', ''),
                'suggested_questions': result.get('suggested_questions', []),
                'message': '视频分析完成（无字幕）'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'视频分析失败: {str(e)}',
                'summary': None,
                'suggested_topics': []
            }

    def translate_subtitle(self, subtitle_text: str, target_lang: str = '中文') -> Dict:
        """
        翻译字幕内容

        Args:
            subtitle_text: 原始字幕文本
            target_lang: 目标语言（中文、英文、日文等）

        Returns:
            {
                'success': bool,
                'translated_text': str,
                'message': str
            }
        """
        try:
            # 分段处理长文本
            max_length = 3000  # 每次翻译的最大长度
            chunks = []
            current_chunk = ""
            lines = subtitle_text.split('\n')

            for line in lines:
                if len(current_chunk) + len(line) < max_length:
                    current_chunk += line + '\n'
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = line + '\n'

            if current_chunk:
                chunks.append(current_chunk)

            # 翻译每个片段
            translated_chunks = []
            for chunk in chunks:
                prompt = f"""请将以下字幕内容翻译成{target_lang}，保持原有的格式和时间戳信息：

{chunk}

要求：
1. 保持原文的段落结构
2. 只翻译内容，不翻译时间戳
3. 保持专业术语的准确性
4. 翻译要自然流畅

请直接返回翻译结果，不要添加任何说明。"""

                response = self.client.chat.completions.create(
                    model=self.DEFAULT_MODEL,
                    messages=[
                        {
                            'role': 'system',
                            'content': f'你是一个专业的视频字幕翻译员，擅长将视频内容翻译成{target_lang}。'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )

                translated_chunk = response.choices[0].message.content
                translated_chunks.append(translated_chunk)

            # 合并翻译结果
            full_translation = '\n'.join(translated_chunks)

            return {
                'success': True,
                'translated_text': full_translation,
                'message': '字幕翻译完成'
            }

        except Exception as e:
            return {
                'success': False,
                'translated_text': None,
                'message': f'翻译失败: {str(e)}'
            }

    def translate_subtitle_stream(self, subtitle_text: str, target_lang: str = '中文'):
        """
        翻译字幕内容（流式输出）

        Args:
            subtitle_text: 原始字幕文本
            target_lang: 目标语言

        Yields:
            str: 流式输出的翻译内容片段
        """
        try:
            # 分段处理长文本
            max_length = 3000
            chunks = []
            current_chunk = ""
            lines = subtitle_text.split('\n')

            for line in lines:
                if len(current_chunk) + len(line) < max_length:
                    current_chunk += line + '\n'
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = line + '\n'

            if current_chunk:
                chunks.append(current_chunk)

            # 翻译每个片段（流式）
            for i, chunk in enumerate(chunks):
                prompt = f"""请将以下字幕内容翻译成{target_lang}，保持原有的格式：

{chunk}

要求：
1. 保持原文的段落结构
2. 只翻译内容，不翻译时间戳
3. 翻译要自然流畅

请直接返回翻译结果。"""

                stream = self.client.chat.completions.create(
                    model=self.DEFAULT_MODEL,
                    messages=[
                        {
                            'role': 'system',
                            'content': '你是一个专业的视频字幕翻译员。'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                    stream=True
                )

                # 流式输出当前片段
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

                # 如果不是最后一个片段，添加分隔符
                if i < len(chunks) - 1:
                    yield '\n\n'

        except Exception as e:
            yield json.dumps({
                'error': True,
                'message': f'翻译失败: {str(e)}'
            })

    def _build_summary_prompt(self, subtitle_text: str,
                              video_title: str = '',
                              video_description: str = '') -> str:
        """
        构建AI总结提示词 - 4段式结构化总结

        Returns:
            结构化的提示词
        """
        # 截断过长的字幕（避免超出token限制）
        max_subtitle_length = 8000  # 中文字符
        if len(subtitle_text) > max_subtitle_length:
            subtitle_text = subtitle_text[:max_subtitle_length] + '...'

        prompt = f"""请根据以下视频字幕内容，生成一份结构化的视频总结报告。

## 视频信息
标题: {video_title or '未知'}
描述: {video_description or '无'}

## 字幕内容
{subtitle_text}

## 要求
请按以下格式输出纯文本总结：

【视频概述】
（100-150字概括视频主题和核心价值）

【内容大纲】
1. 章节标题
   - 具体内容点1
   - 具体内容点2

请直接输出纯文本格式，不要使用JSON代码块。"""

        return prompt

    def chat_about_video(self, question: str, subtitle_text: str,
                        chat_history: List[Dict] = None) -> Dict:
        """
        基于视频内容的AI问答

        Args:
            question: 用户问题
            subtitle_text: 字幕文本（作为上下文）
            chat_history: 对话历史

        Returns:
            {
                'success': bool,
                'answer': str,
                'message': str
            }
        """
        try:
            # 构建对话历史
            messages = [
                {
                    'role': 'system',
                    'content': '你是一个视频内容助手，基于视频字幕内容回答用户问题。'
                }
            ]

            # 添加历史对话
            if chat_history:
                messages.extend(chat_history[-10:])  # 限制历史记录数量

            # 添加字幕上下文
            context_limit = 3000  # 限制上下文长度
            context = subtitle_text[:context_limit] if len(
                subtitle_text) > context_limit else subtitle_text

            # 添加当前问题
            messages.append({
                'role': 'user',
                'content': f"""基于以下视频字幕内容回答问题：

## 视频内容
{context}

## 问题
{question}

请基于视频内容给出准确的答案，如果内容中没有相关信息，请明确说明。"""
            })

            # 调用AI
            response = self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            answer = response.choices[0].message.content

            return {
                'success': True,
                'answer': answer,
                'message': '问答成功'
            }

        except Exception as e:
            return {
                'success': False,
                'answer': None,
                'message': f'问答失败: {str(e)}'
            }

    def export_to_markdown(self, summary_data: Dict, video_info: Dict = None) -> str:
        """
        将总结结果导出为Markdown格式（4段式结构）

        Args:
            summary_data: 总结数据（新4段式格式）
            video_info: 视频信息

        Returns:
            Markdown格式文本
        """
        md_lines = []

        # 标题
        title = video_info.get('title', '视频总结') if video_info else '视频总结'
        md_lines.append(f"# {title}\n")

        # 基本信息
        if video_info:
            md_lines.append("## 📹 视频信息\n")
            md_lines.append(f"- **标题**: {video_info.get('title', '未知')}\n")
            md_lines.append(f"- **时长**: {video_info.get('duration', '未知')}\n")
            md_lines.append(f"- **UP主**: {video_info.get('uploader', '未知')}\n")
            md_lines.append("\n")

        # Section 1: 视频概述
        if summary_data.get('overview'):
            md_lines.append("## 🎯 视频概述\n")
            md_lines.append(f"{summary_data['overview']}\n\n")

        # Section 2: 内容大纲
        if summary_data.get('outline'):
            md_lines.append("## 📚 内容大纲\n")
            for i, outline in enumerate(summary_data['outline'], 1):
                md_lines.append(f"### {i}. {outline.get('title', f'段落{i}')}\n")
                md_lines.append(f"{outline.get('content', '')}\n")
                if outline.get('timestamp'):
                    md_lines.append(f"⏱️ *时间: {outline['timestamp']}*\n")
                md_lines.append("\n")

        # Section 3: 核心要点
        if summary_data.get('key_points'):
            md_lines.append("## 💡 核心要点\n")
            for point in summary_data['key_points']:
                importance = point.get('importance', 3)
                stars = '⭐' * min(importance, 5)
                md_lines.append(f"- {stars} {point.get('point', '')}\n")
                if point.get('timestamp'):
                    md_lines.append(f"  ⏱️ {point['timestamp']}\n")
            md_lines.append("\n")

        # Section 4: 总结结论
        if summary_data.get('conclusion'):
            conclusion = summary_data['conclusion']
            md_lines.append("## 📝 总结结论\n")

            if conclusion.get('summary'):
                md_lines.append(f"**总结**: {conclusion['summary']}\n\n")

            if conclusion.get('takeaways'):
                md_lines.append("**主要收获**:\n")
                for takeaway in conclusion['takeaways']:
                    md_lines.append(f"- {takeaway}\n")
                md_lines.append("\n")

            if conclusion.get('recommendations'):
                md_lines.append("**建议**:\n")
                for rec in conclusion['recommendations']:
                    md_lines.append(f"- {rec}\n")
                md_lines.append("\n")

        # 思维导图（Markdown格式）
        if summary_data.get('mindmap'):
            md_lines.append("## 🧠 思维导图\n")
            mindmap = summary_data['mindmap']
            md_lines.append(f"### {mindmap.get('root', '主题')}\n")

            for branch in mindmap.get('branches', []):
                md_lines.append(f"- **{branch.get('name', '')}**\n")
                for child in branch.get('children', []):
                    md_lines.append(f"  - {child}\n")
            md_lines.append("\n")

        return ''.join(md_lines)

    def generate_mindmap_markdown(self, summary_data: Dict) -> str:
        """
        生成markmap兼容的思维导图Markdown格式

        Args:
            summary_data: 总结数据（4段式格式）

        Returns:
            markmap格式的Markdown
        """
        md_lines = []

        # 使用总结的overview作为根节点
        root_title = summary_data.get('overview', '视频主题')[:50] + ('...' if len(summary_data.get('overview', '')) > 50 else '')

        md_lines.append(f"# {root_title}\n")

        # 从outline生成主要分支
        if summary_data.get('outline'):
            for outline in summary_data['outline']:
                title = outline.get('title', '章节')
                md_lines.append(f"## {title}\n")

                # 从outline的content提取关键点作为子节点
                content = outline.get('content', '')
                if content:
                    # 简单的分句处理
                    sentences = content.split('。')
                    for sentence in sentences[:3]:  # 每个分支最多3个子节点
                        sentence = sentence.strip()
                        if sentence and len(sentence) > 5:
                            md_lines.append(f"- {sentence}。\n")

        # 从key_points生成额外分支
        if summary_data.get('key_points'):
            md_lines.append(f"## 核心要点\n")
            for point in summary_data['key_points']:
                md_lines.append(f"- {point.get('point', '')}\n")

        # 从conclusion生成总结分支
        if summary_data.get('conclusion'):
            conclusion = summary_data['conclusion']
            if conclusion.get('takeaways'):
                md_lines.append(f"## 主要收获\n")
                for takeaway in conclusion['takeaways']:
                    md_lines.append(f"- {takeaway}\n")

        return ''.join(md_lines)

    def summarize_video_structured_stream(self, subtitle_text: str, video_title: str = '',
                                         video_description: str = ''):
        """
        生成视频总结（流式输出 - 4段式结构化版本）

        Args:
            subtitle_text: 字幕文本
            video_title: 视频标题
            video_description: 视频描述

        Yields:
            dict: 包含section和content的流式输出
        """
        try:
            # 构建提示词
            prompt = self._build_summary_prompt(
                subtitle_text, video_title, video_description
            )

            # 调用AI生成总结（流式）
            stream = self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的视频内容分析师，擅长总结和提炼视频的核心内容。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=self.DEFAULT_TEMPERATURE,
                max_tokens=self.DEFAULT_MAX_TOKENS,
                response_format={'type': 'json_object'},
                stream=True
            )

            # 流式输出，按section分段
            buffer = ""
            current_section = "overview"

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    buffer += content

                    # 尝试解析JSON结构
                    try:
                        # 检查是否包含section标记
                        if '"overview":' in content:
                            current_section = "overview"
                        elif '"outline":' in content:
                            current_section = "outline"
                        elif '"key_points":' in content:
                            current_section = "key_points"
                        elif '"conclusion":' in content:
                            current_section = "conclusion"
                        elif '"mindmap":' in content:
                            current_section = "mindmap"

                        yield {
                            'section': current_section,
                            'content': content
                        }
                    except:
                        yield {
                            'section': current_section,
                            'content': content
                        }

        except Exception as e:
            yield {
                'section': 'error',
                'content': json.dumps({
                    'error': True,
                    'message': f'AI总结失败: {str(e)}'
                })
            }


# 便捷函数
def create_summarizer() -> AISummarizer:
    """创建AI总结器实例"""
    return AISummarizer()


def summarize_video(subtitle_text: str, video_title: str = '',
                   video_description: str = '') -> Dict:
    """总结视频的便捷函数"""
    summarizer = AISummarizer()
    return summarizer.summarize_video(subtitle_text, video_title, video_description)
