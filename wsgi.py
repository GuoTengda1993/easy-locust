from easy_locust.web import init_app


if __name__ == '__main__':
    init_app(port=8899, debug=False, threaded=False)
