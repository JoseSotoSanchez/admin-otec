from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):

        ruta = request.path


        # ============================================
        # RUTAS QUE NO REQUIEREN LOGIN
        # ============================================

        rutas_publicas = [
            reverse("login"),
            reverse("logout"),
        ]


        if ruta in rutas_publicas:
            return self.get_response(request)


        # Archivos estáticos
        if ruta.startswith("/static/"):
            return self.get_response(request)


        # Dejamos Django Admin independiente
        if ruta.startswith("/admin/"):
            return self.get_response(request)


        # ============================================
        # VALIDAR LOGIN
        # ============================================

        if not request.session.get("loggedin"):

            return redirect(
                "login"
            )


        # También validamos que exista ID
        if not request.session.get("id"):

            request.session.flush()

            return redirect(
                "login"
            )


        return self.get_response(request)