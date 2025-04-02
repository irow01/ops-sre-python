from rest_framework import pagination


class PageNumberPagination(pagination.PageNumberPagination):
    # 每⻚显示的条数
    page_size = 10
    # 接⼝中⻚码查询关键字
    page_query_param = 'page'

    # ⽤户可以通过接⼝⾃定义⼀⻚条数，最⼤5条，使⽤关键字page_size查询。
    # 对应的请求接⼝: /apis/cars/?page=1&page_size=4, 可以让⽤户⾃定义每⻚显示的数量，最⼤不能超过5个。
    page_size_query_param = 'page_size'
    max_page_size = 400
