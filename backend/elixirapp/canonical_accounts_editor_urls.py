from elixirapp import account_urls, html

urlpatterns = account_urls.patterns()
handler404 = html.page_not_found
handler500 = html.server_error
