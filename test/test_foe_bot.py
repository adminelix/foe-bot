from foe_bot.request import Request


def test_sample_request():
    req = Request()
    body = '[{"__class__":"ServerRequest","requestData":[],"requestClass":"InventoryService","requestMethod":"getItems","requestId":7},{"__class__":"ServerRequest","requestData":[{"__class__":"LoadTimePerformance","module":"City","loadTime":5617}],"requestClass":"LogService","requestMethod":"logPerformanceMetrics","requestId":8}]'
    print(req.send(body))
