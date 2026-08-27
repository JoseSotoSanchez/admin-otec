from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):

        ruta = request.path


        # ============================================
        # RUTAS PUBLICAS
        # ============================================

        rutas_publicas = [
            reverse("login"),
            reverse("logout"),
        ]


        if ruta in rutas_publicas:

            response = self.get_response(request)

            # Nunca cachear login/logout
            response["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, "
                "max-age=0, private"
            )

            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

            return response


        # ============================================
        # ARCHIVOS ESTATICOS
        # ============================================

        if ruta.startswith("/static/"):
            return self.get_response(request)


        # ============================================
        # DJANGO ADMIN
        # ============================================

        if ruta.startswith("/admin/"):
            return self.get_response(request)


        # ============================================
        # VALIDAR SESION
        # ============================================

        if (
            not request.session.get("loggedin")
            or not request.session.get("id")
        ):

            request.session.flush()

            return redirect("login")


        # ============================================
        # EJECUTAR VISTA
        # ============================================

        response = self.get_response(request)


        # ============================================
        # MUY IMPORTANTE
        # NUNCA CACHEAR PAGINAS PRIVADAS
        # ============================================

        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, "
            "max-age=0, private"
        )

        response["Pragma"] = "no-cache"

        response["Expires"] = "0"


        return response