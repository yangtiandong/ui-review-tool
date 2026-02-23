#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI用例生成模块 - 支持DeepSeek和OpenAI
"""

import os
from typing import List, Dict
import json

class AIGenerator:
    """AI用例生成器"""
    
    def __init__(self, provider='deepseek', api_key=None, case_type='标准UI走查'):
        """
        初始化AI生成器
        
        Args:
            provider: 'deepseek' 或 'openai'
            api_key: API密钥
            case_type: '标准UI走查' 或 '竞品对标走查'
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(f'{provider.upper()}_API_KEY')
        self.client = None
        self.model = None
        self.case_type = case_type
        self.rules = self._load_rules()  # 加载规则文档
        
        # 只有在有API Key时才初始化客户端
        if self.api_key and self.api_key != 'dummy':
            try:
                from openai import OpenAI
                
                if provider == 'deepseek':
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url="https://api.deepseek.com"
                    )
                    self.model = "deepseek-chat"
                elif provider == 'openai':
                    self.client = OpenAI(api_key=self.api_key)
                    self.model = "gpt-4"
                else:
                    raise ValueError(f"不支持的provider: {provider}")
            except ImportError:
                print("警告: openai库未安装，将使用模板生成")
                self.client = None
    
    def _load_rules(self) -> str:
        """加载UI走查规则文档"""
        # 根据用例类型选择不同的规则文件
        if self.case_type == '竞品对标走查':
            rules_file = 'AI生成竞品对标UI走查用例规则.md'
        else:
            rules_file = 'AI生成UI走查用例规则.md'
        
        try:
            if os.path.exists(rules_file):
                with open(rules_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return content
            else:
                print(f"警告: 规则文件不存在: {rules_file}")
        except Exception as e:
            print(f"警告: 无法加载规则文档 {rules_file}: {e}")
        return ""
    
    def analyze_requirement(self, content: str) -> Dict:
        """
        分析需求文档，识别功能模块
        
        Args:
            content: 需求文档内容
            
        Returns:
            分析结果字典
        """
        # 如果没有客户端，使用基础分析
        if not self.client:
            return self._basic_analysis(content)
        
        prompt = f"""请分析以下需求文档，识别页面级别的功能模块。

需求文档：
{content[:3000]}

请返回JSON格式：
{{
    "modules": [
        {{
            "name": "模块名称",
            "description": "模块描述",
            "type": "页面类型"
        }}
    ],
    "total_modules": 数量
}}

识别规则：
1. 只识别页面级别的模块（如：首页、详情页、创建页、编辑页）
2. 不要识别小组件（如：按钮、输入框、下拉框）
3. 每个二级标题(##)通常代表一个页面模块
4. 弹窗、对话框如果功能独立也算一个模块
5. 模块名称要简洁明了（如：跨域训练首页、新建任务页）
6. 页面类型可以是：列表页、详情页、创建页、编辑页、弹窗等

注意：
- 不要过度拆分，一个完整的页面就是一个模块
- 避免识别出过多的小模块
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的UI需求分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"AI分析失败: {e}")
            # 返回基础分析结果
            return self._basic_analysis(content)
    
    def generate_test_cases(self, content: str, module: Dict, categories: List[str] = None) -> List[Dict]:
        """
        为指定模块生成UI走查用例
        
        Args:
            content: 需求文档内容
            module: 模块信息
            categories: 建议选项列表（全局页面、场景流程、异常场景、上下游验证）
            
        Returns:
            用例列表
        """
        # 如果没有客户端，使用模板生成
        if not self.client:
            return self._template_cases(module['name'], categories)
        
        # 加载规则文档内容
        rules_context = ""
        if self.rules:
            rules_context = f"""
请严格遵循以下UI走查规则：

{self.rules[:5000]}

"""
        
        # 根据用例类型和建议选项构建提示词
        if self.case_type == '竞品对标走查':
            principles_text = """必须遵循竞品对标十大设计原则：
1. 异常处理完备性 - 所有异常情况都能被捕获、处理并友好提示
2. 信息提示完整性 - 费用、到期、操作提示等关键信息完整清晰
3. 功能可用性保障 - 所有功能稳定可用，失效功能及时修复或下架
4. 文档同步一致性 - 帮助文档与产品实际功能保持同步
5. 响应速度优化 - 页面加载、刷新、操作响应时间符合预期
6. 跳转准确性 - 所有跳转准确到达目标页面
7. 信息一致性 - 同类信息的展示方式、格式、逻辑保持一致
8. 输入校验完整性 - 所有用户输入进行完整校验
9. 语言统一性 - 产品界面、提示信息使用统一语言
10. 操作高效性 - 支持批量操作，减少重复步骤

重点关注高频问题类型：
- 系统报错和异常处理（24.4%）
- 提示信息不清晰或缺失（17.1%）
- 功能无法正常使用（14.6%）
- 帮助文档与产品不一致（8.1%）
- 加载和刷新问题（6.5%）
- 跳转逻辑问题（6.5%）"""
            category_guidance = ""  # 竞品对标模式不使用建议选项
        else:
            principles_text = """必须遵循基于《UIUE设计技术规范》的UI走查原则体系（5大类别13个原则）：

一、易学性原则：
1.1 简化交互原则 - 流程简洁、逻辑直接、场景完整
1.2 引导与帮助原则 - 新手引导、流程引导、空状态引导
1.3 内容与文案准确性原则 - 语言规范、用户语言、指代明确

二、易操作性原则：
2.1 交互无障碍原则 - 最小可操作区域、焦点指示、键盘导航
2.2 遵从认知惯性原则 - 流程符合认知、选择优于输入、常见模式
2.3 异常与负向流程验证原则 - 异常告知、高风险确认、错误纠正

三、清晰性原则：
3.1 识别无障碍原则 - 信息完整性、颜色对比度、文本格式
3.2 层次分明原则 - 架构扁平化、位置指示、主次区分
3.3 组织有序原则 - 对齐规则、响应式布局、断点适配

四、高效性原则：
4.1 预置信息与快捷操作原则 - 预置信息、默认选项、批量操作
4.2 交互与反馈原则 - 控件状态反馈、加载状态、操作反馈

五、一致性原则：
5.1 视觉一致性原则 - 颜色一致、字体一致、功能一致
5.2 组件状态完整性原则 - 按钮状态、输入框状态、链接状态
5.3 数据与文案一致性原则 - 数据一致、句式一致、术语统一"""
            category_guidance = self._build_category_guidance(categories)
        
        prompt = f"""{rules_context}

请为"{module['name']}"模块生成UI走查用例。

模块信息：
- 模块名称：{module['name']}
- 模块描述：{module.get('description', '')}

需求文档片段：
{content[:1500]}

{principles_text}

{category_guidance}

严格按照CSV格式规范返回JSON：
{{
    "cases": [
        {{
            "检查点": "具体的设计元素或组件",
            "设计原则": "从13个原则中选择（只写原则名称，不要编号，如：简化交互原则、视觉一致性原则）",
            "检查项": "描述具体的检查内容",
            "优先级": "高/中/低",
            "预期结果/设计标准": "设计稿中的具体规范或期望表现"
        }}
    ]
}}

关键要求：
1. 生成用例数量：{self._get_case_count_guidance()}
2. 字段名必须完全匹配：检查点、设计原则、检查项、优先级、预期结果/设计标准
3. 严格按照以下优先级划分规则（基于检查的重要性，而非问题的严重性）：
   {self._get_priority_guidance()}
4. **用例排序规则（重要）**：
   • 必须按照页面从上到下的走查顺序排列，而非按优先级排序
   • 页面头部（导航、标题）→ 主要内容区 → 操作按钮 → 页面底部
   • 表单：标题 → 输入项（从上到下）→ 提交按钮 → 错误提示
   • 列表：标题 → 筛选/搜索 → 列表项 → 分页/加载更多
   • 详情页：标题 → 基本信息 → 详细信息 → 操作按钮
   • 同一区域内，高优先级用例可以优先，但不同区域必须按页面顺序
5. **设计原则格式（重要）**：
   • 只写原则名称，不要包含编号
   • 正确示例：简化交互原则、视觉一致性原则、交互与反馈原则
   • 错误示例：1.1 简化交互原则、5.1 视觉一致性原则
6. 所有文本内容保持单行，不要包含换行符
7. **预期结果描述要求（重要）**：
   • 对于视觉细节（字号、字重、颜色、间距等），使用通用描述，如"符合设计规范"、"保持一致"
   • 对于功能性检查，描述具体的预期行为，如"显示成功提示"、"跳转到详情页"
   • 避免使用具体数值（如16px、#262626），除非需求文档中明确提供
   • 可以保留行业标准数值（如WCAG对比度≥4.5:1、响应时间<3秒）
8. 检查点基于具体的功能或UI元素
9. 设计原则必须从上述原则中选择
10. 确保覆盖所有关键场景和高频问题类型
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的UI测试工程师，擅长编写详细的UI走查用例。请确保返回的JSON格式正确，所有字符串都要正确转义。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 降低温度，提高稳定性
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as je:
                print(f"JSON解析失败: {je}")
                print(f"原始内容: {content[:500]}...")
                # 尝试修复常见的JSON问题
                content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                try:
                    result = json.loads(content)
                except:
                    print("修复后仍然无法解析，使用模板生成")
                    return self._template_cases(module['name'], categories)
            
            cases = result.get('cases', [])
            
            if not cases:
                print("AI返回的用例为空，使用模板生成")
                return self._template_cases(module['name'], categories)
            
            # 验证和清理用例数据
            valid_cases = []
            required_fields = ['检查点', '设计原则', '检查项', '优先级', '预期结果/设计标准']
            
            for case in cases:
                # 确保所有必需字段都存在
                if all(field in case for field in required_fields):
                    # 添加模块名称
                    case['页面/模块'] = module['name']
                    # 清理字段值，移除多余的换行和空格
                    for key, value in case.items():
                        if isinstance(value, str):
                            case[key] = value.strip().replace('\n', ' ').replace('\r', '')
                    valid_cases.append(case)
                else:
                    print(f"用例缺少必需字段，跳过: {case}")
            
            if not valid_cases:
                print("没有有效的用例，使用模板生成")
                return self._template_cases(module['name'], categories)
            
            print(f"成功生成 {len(valid_cases)} 个用例")
            return valid_cases
            
        except Exception as e:
            print(f"AI生成用例失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回模板用例
            return self._template_cases(module['name'], categories)
    
    def _get_case_count_guidance(self) -> str:
        """
        根据用例类型返回用例数量指导
        
        Returns:
            用例数量要求文本
        """
        if self.case_type == '竞品对标走查':
            return "10-25个用例，根据模块复杂度调整（简单模块10-15个，复杂模块20-25个）。竞品对标更聚焦，不需要检查视觉细节，用更精准的用例覆盖高频问题"
        else:
            return "10-30个用例，根据模块复杂度调整（简单模块10-15个，复杂模块25-30个）。标准UI走查范围更广，需要覆盖视觉、交互、功能等各个方面"
    
    def _get_priority_guidance(self) -> str:
        """
        根据用例类型返回优先级划分指导
        
        Returns:
            优先级划分规则文本
        """
        if self.case_type == '竞品对标走查':
            return """
   【高优先级 70-80%】- 必须检查，如果不检查可能在竞品对标中被扣分
   • 异常场景处理（报错、失败、超时）
   • 关键信息完整性（费用、到期、限制说明）
   • 核心功能可用性
   • 页面响应速度（<3秒）
   • 跳转准确性
   • 输入校验完整性（特殊字符、边界值）
   
   【中优先级 15-25%】- 应该检查，影响用户体验
   • 帮助文档一致性
   • 信息展示统一性
   • 语言统一性
   • 批量操作支持
   
   【低优先级 5-10%】- 可选检查，优化建议
   • 视觉细节优化
   • 边缘场景"""
        else:
            return """
   【高优先级 40-50%】- 必须检查，如果不检查可能导致严重功能问题
   • 核心交互组件可用性（按钮、输入框、下拉框）
   • 必填项校验
   • 关键操作反馈（提交、保存、删除）
   • 错误提示清晰度
   • 核心业务流程流畅性
   • 页面正常加载
   
   【中优先级 40-50%】- 应该检查，如果不检查可能影响用户体验
   • 次要组件状态表现
   • 操作反馈及时性和明显性
   • 布局对齐和响应式
   • 文案准确性和清晰度
   • 辅助功能可用性
   • 加载速度和性能
   
   【低优先级 10-20%】- 可选检查，视觉细节优化
   • 字号、字重、行高等排版细节
   • 间距、边距精确数值
   • 颜色具体色值
   • 图标样式统一性
   • 装饰性元素
   • 动画效果流畅度"""
    
    def _build_category_guidance(self, categories: List[str] = None) -> str:
        """
        根据建议选项构建提示词指导
        
        Args:
            categories: 建议选项列表
            
        Returns:
            提示词片段
        """
        if not categories:
            return ""
        
        guidance_parts = []
        
        # 定义每个建议选项的提示词片段
        category_prompts = {
            '全局页面': """
【全局页面测试重点】
请特别关注以下通用组件和全局元素的测试用例：
- 页面头部（Header）：Logo、导航菜单、用户信息、搜索框等
- 页面底部（Footer）：版权信息、链接、联系方式等
- 侧边导航栏：菜单项、展开/收起状态、选中状态
- 面包屑导航：层级显示、点击跳转
- 全局提示组件：Toast、Message、Notification
- 全局加载状态：页面级Loading、骨架屏
- 通用按钮和图标：确保在不同页面中保持一致
- 响应式布局：在不同屏幕尺寸下的表现
请为这些全局组件生成至少3-4个专门的测试用例。
""",
            '场景流程': """
【场景流程测试重点】
请特别关注以下多步骤操作流程的测试用例：
- 完整的用户操作路径：从进入页面到完成目标的全流程
- 多步骤表单：步骤指示器、上一步/下一步、数据保存
- 向导式流程：引导提示、进度展示、步骤跳转
- 数据提交流程：填写→预览→确认→提交→反馈
- 审批流程：提交→审核→通过/驳回→通知
- 搜索筛选流程：输入条件→搜索→结果展示→详情查看
- 状态流转：草稿→待审核→已发布等状态变化
请为关键业务流程生成至少3-4个端到端的测试用例，覆盖正常路径和分支路径。
""",
            '异常场景': """
【异常场景测试重点】
请特别关注以下错误处理和边界条件的测试用例：
- 输入验证：必填项、格式校验、长度限制、特殊字符
- 网络异常：请求超时、网络断开、服务器错误（500、502等）
- 权限异常：无权限访问、登录过期、Token失效
- 数据异常：空数据、数据加载失败、数据格式错误
- 操作冲突：并发操作、重复提交、数据已被修改
- 边界条件：最大值、最小值、空值、极限数据量
- 错误提示：清晰的错误信息、友好的错误页面、错误恢复指引
- 降级处理：功能不可用时的降级方案
请为各类异常情况生成至少4-5个测试用例，确保系统的健壮性。
""",
            '上下游验证': """
【上下游验证测试重点】
请特别关注以下数据流转和接口调用的测试用例：
- 数据传递：页面间参数传递、数据回显、数据同步
- 接口调用：请求参数正确性、响应数据处理、错误处理
- 状态同步：操作后相关页面/组件的状态更新
- 缓存处理：数据缓存、缓存更新、缓存失效
- 消息通知：操作后的消息推送、通知展示
- 关联数据：主数据变更后关联数据的更新
- 跨页面影响：在A页面操作后，B页面的数据是否正确更新
- 数据一致性：列表页和详情页数据一致、编辑前后数据一致
请为数据流转和接口交互生成至少3-4个测试用例，确保上下游数据的正确性。
"""
        }
        
        # 根据选中的建议选项构建指导文本
        for category in categories:
            if category in category_prompts:
                guidance_parts.append(category_prompts[category])
        
        if guidance_parts:
            return "\n" + "\n".join(guidance_parts) + "\n"
        
        return ""
    
    def _basic_analysis(self, content: str) -> Dict:
        """基础分析（不使用AI）"""
        lines = content.split('\n')
        modules = []
        
        for line in lines:
            if line.startswith('##'):
                module_name = line.replace('##', '').strip()
                if module_name and not module_name[0].isdigit():
                    modules.append({
                        'name': module_name,
                        'description': '',
                        'pages': []
                    })
        
        return {
            'modules': modules[:10],  # 最多10个
            'total_modules': len(modules)
        }
    
    def _template_cases(self, module_name: str, categories: List[str] = None) -> List[Dict]:
        """
        模板用例（不使用AI）
        
        Args:
            module_name: 模块名称
            categories: 建议选项列表
            
        Returns:
            用例列表
        """
        # 根据用例类型生成不同的基础用例
        if self.case_type == '竞品对标走查':
            base_cases = self._get_competitive_template_cases(module_name)
        else:
            base_cases = self._get_standard_template_cases(module_name)
        
        # 根据建议选项添加额外用例（仅标准UI走查）
        if categories and self.case_type == '标准UI走查':
            additional_cases = self._get_category_template_cases(module_name, categories)
            base_cases.extend(additional_cases)
        
        return base_cases
    
    def _get_standard_template_cases(self, module_name: str) -> List[Dict]:
        """标准UI走查模板用例"""
        return [
            # 高优先级用例（40-50%）- 核心功能和交互
            {
                '页面/模块': module_name,
                '检查点': '按钮状态',
                '设计原则': '组件状态完整性原则',
                '检查项': f'检查{module_name}中主要按钮的各种状态',
                '优先级': '高',
                '预期结果/设计标准': '按钮有默认、悬停、点击、禁用状态，核心按钮可正常点击'
            },
            {
                '页面/模块': module_name,
                '检查点': '输入框状态',
                '设计原则': '组件状态完整性原则',
                '检查项': f'检查{module_name}中输入框的各种状态',
                '优先级': '高',
                '预期结果/设计标准': '输入框有占位符、聚焦、已输入、错误、禁用状态，必填项可正常输入'
            },
            {
                '页面/模块': module_name,
                '检查点': '错误提示',
                '设计原则': '异常与负向流程验证原则',
                '检查项': f'检查{module_name}中输入验证的错误提示',
                '优先级': '高',
                '预期结果/设计标准': '输入错误时显示清晰的错误提示信息，用户能理解如何修正'
            },
            {
                '页面/模块': module_name,
                '检查点': '操作反馈',
                '设计原则': '交互与反馈原则',
                '检查项': f'检查{module_name}中关键操作是否有反馈',
                '优先级': '高',
                '预期结果/设计标准': '提交、保存、删除等关键操作有成功/失败提示'
            },
            # 中优先级用例（40-50%）- 体验优化
            {
                '页面/模块': module_name,
                '检查点': '加载状态',
                '设计原则': '交互与反馈原则',
                '检查项': f'检查{module_name}中数据加载时的状态',
                '优先级': '中',
                '预期结果/设计标准': '数据加载时显示Loading提示或骨架屏'
            },
            {
                '页面/模块': module_name,
                '检查点': '页面布局',
                '设计原则': '组织有序原则',
                '检查项': f'检查{module_name}的页面布局和对齐',
                '优先级': '中',
                '预期结果/设计标准': '元素按网格系统对齐，布局清晰合理'
            },
            {
                '页面/模块': module_name,
                '检查点': '文案准确性',
                '设计原则': '内容与文案准确性原则',
                '检查项': f'检查{module_name}中所有文案是否准确无误',
                '优先级': '中',
                '预期结果/设计标准': '无错别字，专业术语准确，语句通顺'
            },
            # 低优先级用例（10-20%）- 视觉细节
            {
                '页面/模块': module_name,
                '检查点': '页面标题样式',
                '设计原则': '视觉一致性原则',
                '检查项': f'检查{module_name}页面标题的字体、字号、颜色',
                '优先级': '低',
                '预期结果/设计标准': '标题字号、字重、颜色符合设计规范'
            }
        ]
    
    def _get_competitive_template_cases(self, module_name: str) -> List[Dict]:
        """竞品对标走查模板用例"""
        return [
            {
                '页面/模块': module_name,
                '检查点': '异常处理',
                '设计原则': '异常处理完备性',
                '检查项': f'检查{module_name}中所有异常情况是否有友好提示',
                '优先级': '高',
                '预期结果/设计标准': '显示明确的失败原因和解决方案，避免技术性错误代码'
            },
            {
                '页面/模块': module_name,
                '检查点': '费用信息',
                '设计原则': '信息提示完整性',
                '检查项': f'检查{module_name}中费用、价格信息是否明确说明',
                '优先级': '高',
                '预期结果/设计标准': '明确显示费用金额、计费周期、到期时间'
            },
            {
                '页面/模块': module_name,
                '检查点': '功能可用性',
                '设计原则': '功能可用性保障',
                '检查项': f'检查{module_name}中所有功能是否稳定可用',
                '优先级': '高',
                '预期结果/设计标准': '核心功能稳定可用，不可用功能置灰并说明原因'
            },
            {
                '页面/模块': module_name,
                '检查点': '帮助文档',
                '设计原则': '文档同步一致性',
                '检查项': f'检查{module_name}的帮助文档是否与实际功能一致',
                '优先级': '中',
                '预期结果/设计标准': '文档与产品同步更新，截图为最新版本，链接有效'
            },
            {
                '页面/模块': module_name,
                '检查点': '页面加载速度',
                '设计原则': '响应速度优化',
                '检查项': f'检查{module_name}的页面加载和响应速度',
                '优先级': '高',
                '预期结果/设计标准': '页面首次加载<3秒，操作响应及时'
            },
            {
                '页面/模块': module_name,
                '检查点': '跳转准确性',
                '设计原则': '跳转准确性',
                '检查项': f'检查{module_name}中所有跳转是否准确到达目标页面',
                '优先级': '高',
                '预期结果/设计标准': '跳转目标准确，无需二次操作，链接有效'
            },
            {
                '页面/模块': module_name,
                '检查点': '信息一致性',
                '设计原则': '信息一致性',
                '检查项': f'检查{module_name}中同类信息的展示方式是否一致',
                '优先级': '中',
                '预期结果/设计标准': '费用显示格式统一，单位显示规则统一'
            },
            {
                '页面/模块': module_name,
                '检查点': '输入校验',
                '设计原则': '输入校验完整性',
                '检查项': f'检查{module_name}中所有用户输入是否进行完整校验',
                '优先级': '高',
                '预期结果/设计标准': '特殊字符过滤，输入长度限制，校验失败友好提示'
            },
            {
                '页面/模块': module_name,
                '检查点': '语言统一性',
                '设计原则': '语言统一性',
                '检查项': f'检查{module_name}中界面文案是否使用统一语言',
                '优先级': '中',
                '预期结果/设计标准': '所有界面文案使用中文，避免中英文混合'
            },
            {
                '页面/模块': module_name,
                '检查点': '批量操作',
                '设计原则': '操作高效性',
                '检查项': f'检查{module_name}是否支持批量操作',
                '优先级': '中',
                '预期结果/设计标准': '支持批量上传、删除、修改，减少重复操作'
            }
        ]
    
    def _get_category_template_cases(self, module_name: str, categories: List[str]) -> List[Dict]:
        """
        根据建议选项生成额外的模板用例
        
        Args:
            module_name: 模块名称（可以是实际模块名或建议选项名称）
            categories: 建议选项列表
            
        Returns:
            额外的用例列表
        """
        additional_cases = []
        
        # 全局页面用例
        if '全局页面' in categories:
            additional_cases.extend([
                {
                    '页面/模块': module_name,
                    '检查点': '页面头部',
                    '设计原则': '视觉一致性原则',
                    '检查项': f'检查{module_name}的页面头部Logo、导航菜单、用户信息等全局元素',
                    '优先级': '高',
                    '预期结果/设计标准': '头部高度64px，Logo尺寸120x32px，导航菜单字号14px'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '页面底部',
                    '设计原则': '视觉一致性原则',
                    '检查项': f'检查{module_name}的页面底部版权信息、链接等全局元素',
                    '优先级': '中',
                    '预期结果/设计标准': '底部高度48px，文字颜色#999999，字号12px'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '全局提示组件',
                    '设计原则': '交互与反馈原则',
                    '检查项': f'检查{module_name}中Toast、Message等全局提示组件的样式和行为',
                    '优先级': '高',
                    '预期结果/设计标准': 'Toast自动消失时间3秒，位置居中顶部，有淡入淡出动画'
                }
            ])
        
        # 场景流程用例
        if '场景流程' in categories:
            additional_cases.extend([
                {
                    '页面/模块': module_name,
                    '检查点': '完整操作流程',
                    '设计原则': '简化交互原则',
                    '检查项': f'检查{module_name}的完整用户操作路径，从进入到完成目标',
                    '优先级': '高',
                    '预期结果/设计标准': '流程步骤清晰，每步有明确的操作指引和反馈'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '多步骤表单',
                    '设计原则': '简化交互原则',
                    '检查项': f'检查{module_name}中多步骤表单的步骤指示器、上一步/下一步按钮',
                    '优先级': '高',
                    '预期结果/设计标准': '步骤指示器显示当前步骤，已完成步骤可点击返回，数据自动保存'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '状态流转',
                    '设计原则': '简化交互原则',
                    '检查项': f'检查{module_name}中数据状态的流转过程（如草稿→待审核→已发布）',
                    '优先级': '中',
                    '预期结果/设计标准': '状态变化有明确的视觉标识，状态流转符合业务逻辑'
                }
            ])
        
        # 异常场景用例
        if '异常场景' in categories:
            additional_cases.extend([
                {
                    '页面/模块': module_name,
                    '检查点': '输入验证',
                    '设计原则': '异常与负向流程验证',
                    '检查项': f'检查{module_name}中表单的输入验证（必填项、格式、长度、特殊字符）',
                    '优先级': '高',
                    '预期结果/设计标准': '必填项未填提示"该字段不能为空"，格式错误提示具体要求'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '网络异常处理',
                    '设计原则': '异常与负向流程验证',
                    '检查项': f'检查{module_name}在网络异常时的处理（超时、断网、服务器错误）',
                    '优先级': '高',
                    '预期结果/设计标准': '网络异常时显示友好的错误提示，提供重试按钮'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '权限异常处理',
                    '设计原则': '异常与负向流程验证',
                    '检查项': f'检查{module_name}在无权限或登录过期时的处理',
                    '优先级': '高',
                    '预期结果/设计标准': '无权限时跳转到403页面，登录过期时跳转到登录页'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '边界条件',
                    '设计原则': '异常与负向流程验证',
                    '检查项': f'检查{module_name}在极限数据量、空数据等边界条件下的表现',
                    '优先级': '中',
                    '预期结果/设计标准': '空数据时显示空状态提示，大数据量时有分页或虚拟滚动'
                }
            ])
        
        # 上下游验证用例
        if '上下游验证' in categories:
            additional_cases.extend([
                {
                    '页面/模块': module_name,
                    '检查点': '数据传递',
                    '设计原则': '简化交互原则',
                    '检查项': f'检查{module_name}与其他页面之间的数据传递和回显',
                    '优先级': '高',
                    '预期结果/设计标准': '页面间参数正确传递，数据准确回显，无数据丢失'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '状态同步',
                    '设计原则': '数据与文案一致性原则',
                    '检查项': f'检查{module_name}操作后相关页面/组件的状态更新',
                    '优先级': '高',
                    '预期结果/设计标准': '操作后相关数据实时更新，列表页和详情页数据一致'
                },
                {
                    '页面/模块': module_name,
                    '检查点': '接口调用',
                    '设计原则': '异常与负向流程验证原则',
                    '检查项': f'检查{module_name}的接口调用参数和响应数据处理',
                    '优先级': '中',
                    '预期结果/设计标准': '请求参数正确，响应数据正确解析，接口错误有友好提示'
                }
            ])
        
        return additional_cases
    
    def classify_problem(self, problem_description: str, classification_manual: str) -> str:
        """
        对问题进行智能分类
        
        Args:
            problem_description: 问题描述
            classification_manual: 分类手册内容
            
        Returns:
            JSON格式的分类结果，包含category、reason和reference
        """
        if not self.client:
            # 如果没有AI客户端，返回默认分类
            return json.dumps({
                'category': '功能完备性',
                'reason': '未配置AI服务，无法进行智能分类',
                'reference': ''
            }, ensure_ascii=False)
        
        try:
            prompt = f"""你是一个UI走查问题分类专家。请根据以下分类手册，对给定的问题进行分类。

# 分类手册
{classification_manual}

# 待分类问题
{problem_description}

# 分类要求
1. 仔细阅读分类手册，理解每个一级分类的定义和特征
2. 分析问题描述，判断其属于哪个一级分类
3. 分类结果必须是以下5个一级分类之一：
   - 功能完备性
   - 信息清晰性
   - 任务高效性
   - 系统可靠性
   - 一致性
4. 给出分类结果、简要的分类原因（50字以内）、以及参照的具体章节
5. 以JSON格式返回结果

# 输出格式（注意：目前正式手册中只有"一级指标-二级指标-问题类型"三层结构，不存在1.1.1这类第三级编号）
{{
    "category": "分类名称",
    "reason": "分类原因说明",
    "reference": "数字.一级分类-数字.数字 二级指标-具体问题类型"
}}

# reference字段格式说明
必须按照"数字.一级分类-数字.数字 二级指标-具体问题类型"的格式，其中：
- 前面的"数字.一级分类"和"数字.数字 二级指标"必须严格来自上面的分类手册标题（如"1. 功能完备性"、"2. 信息清晰性"、"2.2 页面结构清晰"等）
- 最后的"具体问题类型"可以直接使用手册中对应二级指标下的某一条问题描述（如"功能实现与需求不符"），**不要再人为增加诸如"1.1.1"、"1.1.2"之类的新的编号**

示例（注意没有1.1.1这类编号）：
- "2.信息清晰性-2.2 页面结构清晰-功能层级不明确"
- "4.系统可靠性-4.2 系统运行稳定-功能无法正常使用"
- "5.一致性-5.2 信息传达一致-前后端信息不一致"
- "3.任务高效性-3.2 任务步骤合理-任务步骤或操作路径复杂冗余"

# 正确示例
{{
    "category": "信息清晰性",
    "reason": "功能入口位置隐蔽，用户难以发现",
    "reference": "2.信息清晰性-2.2.2 功能入口易见-功能/信息入口隐蔽"
}}

{{
    "category": "系统可靠性",
    "reason": "功能无法正常使用",
    "reference": "4.系统可靠性-4.2.2 系统运行稳定-功能无法正常使用"
}}

注意：
1. category字段必须是上述5个一级分类之一
2. reference字段必须具体到二级指标和问题类型，格式要规范

请直接返回JSON，不要包含其他内容。"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的UI走查问题分类专家，擅长根据问题描述进行准确分类。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # 清理可能的markdown代码块标记
            if result.startswith('```'):
                # 移除开头的```json或```
                result = result.split('\n', 1)[1] if '\n' in result else result[3:]
            if result.endswith('```'):
                # 移除结尾的```
                result = result.rsplit('```', 1)[0]
            result = result.strip()
            
            # 尝试解析JSON，确保格式正确
            try:
                parsed = json.loads(result)
                # 确保包含所有必需字段
                if 'reference' not in parsed:
                    parsed['reference'] = ''
                if 'reason' not in parsed:
                    parsed['reason'] = '分类原因未提供'
                if 'category' not in parsed:
                    parsed['category'] = '功能完备性'
                return json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError as e:
                # JSON解析失败，尝试修复
                print(f"JSON解析失败: {e}")
                print(f"原始内容: {result[:200]}")
                
                # 尝试提取关键信息
                category = '功能完备性'
                reason = '解析失败'
                reference = ''
                
                # 尝试从不完整的JSON中提取信息
                if '"category"' in result:
                    try:
                        cat_start = result.find('"category"')
                        cat_value_start = result.find(':', cat_start) + 1
                        cat_value_end = result.find(',', cat_value_start)
                        if cat_value_end == -1:
                            cat_value_end = result.find('}', cat_value_start)
                        cat_str = result[cat_value_start:cat_value_end].strip().strip('"')
                        if cat_str:
                            category = cat_str
                    except:
                        pass
                
                return json.dumps({
                    'category': category,
                    'reason': reason,
                    'reference': reference
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                'category': '功能完备性',
                'reason': f'分类失败: {str(e)[:30]}',
                'reference': ''
            }, ensure_ascii=False)


# 使用示例
if __name__ == '__main__':
    # 使用DeepSeek
    generator = AIGenerator(provider='deepseek', api_key='your-deepseek-api-key')
    
    # 分析需求
    content = """
    # 跨域训练功能
    
    ## 1. 跨域训练首页
    展示训练任务列表
    
    ## 2. 新建训练任务
    创建新的训练任务
    """
    
    analysis = generator.analyze_requirement(content)
    print("分析结果:", analysis)
    
    # 生成用例
    if analysis['modules']:
        cases = generator.generate_test_cases(content, analysis['modules'][0])
        print(f"生成了 {len(cases)} 个用例")
        for case in cases:
            print(f"- {case['检查点']}: {case['检查项']}")