from django.http import HttpResponse


def index(request):
    squirrel_art = """
    <pre style="font-family: monospace; line-height: 1.2;">
  __
 ' )`\\
  /' |_./<
 |  /'-.\\_|
 `\\|/~\>>
   `\\_<_

Collecting nuts per usual...
    </pre>
    """
    return HttpResponse(squirrel_art)