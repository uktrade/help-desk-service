def temp_middleware(get_response):
    def mw(request):
        from django.conf import settings

        print(f"S_P_S_H: {settings.SECURE_PROXY_SSL_HEADER}")
        header, value = settings.SECURE_PROXY_SSL_HEADER
        header_value = request.META.get(header)
        print(f"META: {header_value}")
        return get_response(request)

    return mw
