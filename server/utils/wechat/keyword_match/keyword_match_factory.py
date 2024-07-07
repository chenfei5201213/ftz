import json


class StringHandlerFactory:
    def __init__(self, keyword_config: list):
        self.handlers = []
        self.load_handlers(keyword_config)

    def load_handlers(self, keyword_config: list):
        for handler_config in keyword_config:
            keyword = handler_config.get('keyword', '')
            response = handler_config.get('response', '')
            handler = StringHandler(keyword, response)
            self.handlers.append(handler)

    def get_processor(self):
        processor = StringProcessor()
        for handler in self.handlers:
            processor.add_handler(handler)
        return processor


class StringHandler:
    def __init__(self, keyword, response):
        self.keyword = keyword
        self.response = response

    def handle(self, input_string):
        if self.keyword in input_string:
            return self.response
        return None


class StringProcessor:
    def __init__(self):
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)

    def process_string(self, input_string):
        for handler in self.handlers:
            response = handler.handle(input_string)
            if response:
                return response
        return


if __name__ == '__main__':
    # 示例用法
    factory = StringHandlerFactory('./config.json')
    processor = factory.get_processor()

    input_string = '这里包含字符串1'
    response = processor.process_string(input_string)
    print(response)  # 输出 '响应11'

    input_string = '这里包含字符串2'
    response = processor.process_string(input_string)
    print(response)  # 输出 '响应2'

    input_string = '其他字符串'
    response = processor.process_string(input_string)
    print(response)  # 输出 '未知模式或无匹配'
