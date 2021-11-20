from request import Request


def main():
    req = Request()
    sample_request(req)


def sample_request(req):
    body = '[{"__class__":"ServerRequest","requestData":[],"requestClass":"InventoryService","requestMethod":"getItems","requestId":7},{"__class__":"ServerRequest","requestData":[{"__class__":"LoadTimePerformance","module":"City","loadTime":5617}],"requestClass":"LogService","requestMethod":"logPerformanceMetrics","requestId":8}]'
    print(req.send(body))


if __name__ == "__main__":
    main()
